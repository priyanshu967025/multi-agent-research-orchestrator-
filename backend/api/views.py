import sys
import os
import time
import tempfile
from django.conf import settings
from django.utils import timezone

# Make the project root importable so `graph`, `benchmark`, `rag`, etc. resolve.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import ResearchSession, BenchmarkEvaluation
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    ResearchSessionListSerializer,
    ResearchSessionDetailSerializer,
    ResearchJobCreateSerializer,
    BenchmarkEvaluationListSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .services import initial_research_state, launch_research_job, queue_research_job


# ── Public endpoints (no auth required) ──────────────────────────────


class HealthAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok"})


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key,
                "message": "User registered successfully",
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key,
                "message": "Login successful",
            })
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


# ── Authenticated endpoints ──────────────────────────────────────────


class LogoutAPIView(APIView):
    """Delete the caller's auth token to log them out."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        return Response({"message": "Logged out successfully"})


class UserProfileAPIView(APIView):
    """GET  — return the current user's profile.
    PUT/PATCH — update username / email."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        if "username" in request.data:
            new_username = request.data["username"]
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                return Response(
                    {"error": "Username already taken"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.username = new_username
        if "email" in request.data:
            user.email = request.data["email"]
        user.save()
        return Response(UserSerializer(user).data)

    def patch(self, request):
        return self.put(request)


class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.save()
            # Re-issue token so the user stays logged in.
            Token.objects.filter(user=request.user).delete()
            new_token = Token.objects.create(user=request.user)
            return Response({
                "message": "Password changed successfully",
                "token": new_token.key,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Research endpoints ───────────────────────────────────────────────


class ExecuteResearchAPIView(APIView):
    """Execute the multi-agent research pipeline.

    Authenticated users have their sessions saved and linked.
    Anonymous users can still run research (but sessions won't be linked).
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        topic = request.data.get("topic")
        if not topic:
            return Response({"error": "Topic is required"}, status=status.HTTP_400_BAD_REQUEST)

        initial_state = initial_research_state(topic)

        try:
            from graph.workflow import research_graph

            start = time.time()
            result = research_graph.invoke(initial_state, {"recursion_limit": 25})
            elapsed = time.time() - start

            user = request.user if request.user.is_authenticated else None
            session = ResearchSession.objects.create(
                user=user,
                topic=topic,
                status="completed",
                final_report=result.get("final_report", ""),
                web_sources_count=len(result.get("research_data", [])),
                rag_chunks_count=len(result.get("rag_context", [])),
                revision_count=result.get("revision_count", 0),
                duration_seconds=round(elapsed, 2),
            )

            return Response({
                "session_id": session.id,
                "topic": topic,
                "final_report": result.get("final_report", ""),
                "messages": result.get("messages", []),
                "revision_count": result.get("revision_count", 0),
                "sources_count": len(result.get("research_data", [])),
            })
        except Exception as e:
            # Legacy endpoint preserves its established response contract. New job
            # endpoints record a safe public error and never expose exception text.
            return Response({"error": f"Execution failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResearchJobsAPIView(APIView):
    """Create and list durable, owner-scoped research jobs."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = max(1, min(50, int(request.query_params.get("page_size", 20))))
        queryset = ResearchSession.objects.filter(user=request.user)
        total = queryset.count()
        offset = (page - 1) * page_size
        sessions = queryset[offset : offset + page_size]
        return Response({
            "total": total,
            "page": page,
            "page_size": page_size,
            "jobs": ResearchSessionListSerializer(sessions, many=True).data,
        })

    def post(self, request):
        serializer = ResearchJobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = queue_research_job(request.user, serializer.validated_data["topic"])
        asynchronous = getattr(settings, "RESEARCH_RUNS_ASYNC", True)
        launch_research_job(session.id, asynchronous=asynchronous)
        session.refresh_from_db()
        response_status = status.HTTP_202_ACCEPTED if asynchronous else status.HTTP_201_CREATED
        return Response(ResearchSessionDetailSerializer(session).data, status=response_status)


class ResearchDocumentUploadAPIView(APIView):
    """Ingest owner-submitted PDFs into the research knowledge base."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        files = request.FILES.getlist("files")
        if not files:
            return Response(
                {"error": "At least one PDF is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        temp_paths = []
        try:
            for uploaded_file in files:
                if not uploaded_file.name.lower().endswith(".pdf"):
                    return Response(
                        {"error": "Only PDF files are supported.", "code": "unsupported_file_type"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_paths.append(temp_file.name)

            from rag.vector_store import ingest_documents
            result = ingest_documents(temp_paths)
            return Response({"message": "Documents ingested.", **result}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(
                {"error": "Documents could not be ingested."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            for path in temp_paths:
                try:
                    os.unlink(path)
                except OSError:
                    pass


class UserSessionsAPIView(APIView):
    """List all research sessions belonging to the authenticated user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = max(1, min(100, int(request.query_params.get("page_size", 20))))
        qs = ResearchSession.objects.filter(user=request.user).order_by("-created_at")
        total = qs.count()
        offset = (page - 1) * page_size
        sessions = qs[offset : offset + page_size]
        return Response({
            "total": total,
            "page": page,
            "page_size": page_size,
            "sessions": ResearchSessionListSerializer(sessions, many=True).data,
        })


class SessionDetailAPIView(APIView):
    """GET — retrieve a session (must own it).
    DELETE — delete a session (must own it)."""

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            obj = ResearchSession.objects.get(pk=pk)
        except ResearchSession.DoesNotExist:
            return None
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ResearchSessionDetailSerializer(obj).data)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Benchmark endpoints ──────────────────────────────────────────────


class RunBenchmarkAPIView(APIView):
    """Run single-agent vs multi-agent benchmark."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        topic = request.data.get("topic")
        if not topic:
            return Response({"error": "Topic is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from benchmark.evaluator import run_single_agent_baseline, evaluate_outputs
            from graph.workflow import research_graph

            baseline = run_single_agent_baseline(topic)

            initial_state = initial_research_state(topic)
            pipeline_result = research_graph.invoke(initial_state, {"recursion_limit": 25})
            multi_agent_report = pipeline_result.get("final_report", "")

            eval_metrics = evaluate_outputs(topic, baseline["text"], multi_agent_report)

            user = request.user if request.user.is_authenticated else None
            BenchmarkEvaluation.objects.create(
                user=user,
                topic=topic,
                single_agent_depth=eval_metrics.get("single_agent", {}).get("depth_score", 0),
                multi_agent_depth=eval_metrics.get("multi_agent", {}).get("depth_score", 0),
                single_agent_verifiability=eval_metrics.get("single_agent", {}).get("verifiability_score", 0),
                multi_agent_verifiability=eval_metrics.get("multi_agent", {}).get("verifiability_score", 0),
                verdict=eval_metrics.get("verdict", ""),
            )

            return Response({
                "topic": topic,
                "single_agent_baseline": baseline,
                "multi_agent_report": multi_agent_report,
                "evaluation_metrics": eval_metrics,
            })
        except Exception as e:
            return Response({"error": f"Benchmark evaluation failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BenchmarkHistoryAPIView(APIView):
    """List benchmark evaluations. Authenticated users see their own; admins see all."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        limit = max(1, min(int(request.query_params.get("limit", 50)), 500))

        qs = BenchmarkEvaluation.objects.all()
        if request.user.is_authenticated and not request.user.is_staff:
            qs = qs.filter(user=request.user)

        evaluations = qs.order_by("-created_at", "-id")[:limit]
        return Response(BenchmarkEvaluationListSerializer(evaluations, many=True).data)


# ── Streaming ────────────────────────────────────────────────────────


class ResearchStreamAPIView(APIView):
    """Stream research pipeline progress as Server-Sent Events."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        topic = request.data.get("topic")
        if not topic:
            return Response({"error": "Topic is required"}, status=status.HTTP_400_BAD_REQUEST)

        from .services import queue_research_job
        session = queue_research_job(request.user, topic)

        def event_stream():
            import json
            from django.db import transaction as _tx
            from .models import ResearchEvent, ResearchSession
            from .services import initial_research_state, _store_sources

            try:
                from graph.workflow import research_graph

                state = initial_research_state(session.topic)
                sequence = 1
                collected_web, collected_rag = [], []

                def emit(stage, message):
                    nonlocal sequence
                    sequence += 1
                    with _tx.atomic():
                        ResearchEvent.objects.create(session=session, sequence=sequence, stage=stage, message=message[:1000])
                        ResearchSession.objects.filter(pk=session.pk).update(progress_version=sequence)
                    yield f"data: {json.dumps({'stage': stage, 'message': message})}\n\n"

                ResearchSession.objects.filter(pk=session.pk).update(status="running", started_at=timezone.now())
                yield from emit("queued", "Starting research pipeline...")

                for event in research_graph.stream(state, {"recursion_limit": 25}):
                    for node_name, node_output in event.items():
                        if node_name == "__end__":
                            continue
                        state.update(node_output)
                        collected_web.extend(node_output.get("research_data", []))
                        collected_rag.extend(node_output.get("rag_context", []))
                        msg = node_output.get("messages", [f"{node_name} completed."])[-1]
                        valid_stage = node_name if node_name in dict(ResearchEvent.STAGE_CHOICES) else "researcher"
                        yield from emit(valid_stage, msg)

                with _tx.atomic():
                    _store_sources(session, collected_web, collected_rag)
                    session.status = "completed"
                    session.final_report = state.get("final_report", "")
                    session.fact_check_result = state.get("fact_check_result", "")
                    session.web_sources_count = len(collected_web)
                    session.rag_chunks_count = len(collected_rag)
                    session.revision_count = state.get("revision_count", 0)
                    session.completed_at = timezone.now()
                    session.save()

                yield f"data: {json.dumps({'stage': 'completed', 'message': 'Done', 'session_id': session.id})}\n\n"
            except Exception as exc:
                session.status = "failed"
                session.error_code = "streaming_failed"
                session.error_message = str(exc)[:500]
                session.completed_at = timezone.now()
                session.save()
                yield f"data: {json.dumps({'stage': 'failed', 'message': str(exc)[:200]})}\n\n"
            finally:
                yield "data: [DONE]\n\n"

        from django.http import StreamingHttpResponse
        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream",
                                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
        response["X-Research-Session-Id"] = session.id
        return response


# ── Tags ─────────────────────────────────────────────────────────────


from .models import ResearchTag
from .serializers import ResearchTagSerializer


class ResearchTagsAPIView(APIView):
    """List or add tags for a research session."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            session = ResearchSession.objects.get(pk=pk, user=request.user)
        except ResearchSession.DoesNotExist:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ResearchTagSerializer(session.tags.all(), many=True).data)

    def post(self, request, pk):
        try:
            session = ResearchSession.objects.get(pk=pk, user=request.user)
        except ResearchSession.DoesNotExist:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get("name", "").strip().lower()
        if not name or len(name) > 64:
            return Response({"error": "Provide a tag name (max 64 chars)."}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = ResearchTag.objects.get_or_create(session=session, name=name)
        return Response(ResearchTagSerializer(obj).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# ── Platform Overview & Analytics ────────────────────────────────────


class PlatformStatsAPIView(APIView):
    """Aggregate statistics on research jobs, sources, RAG, and providers."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.db.models import Sum, Avg
        from config.providers import provider_info
        from rag.vector_store import get_collection_stats

        total_sessions = ResearchSession.objects.count()
        completed_sessions = ResearchSession.objects.filter(status="completed").count()
        running_sessions = ResearchSession.objects.filter(status="running").count()
        failed_sessions = ResearchSession.objects.filter(status="failed").count()

        totals = ResearchSession.objects.aggregate(
            total_web=Sum("web_sources_count"),
            total_rag=Sum("rag_chunks_count"),
            total_revisions=Sum("revision_count"),
            avg_duration=Avg("duration_seconds"),
        )

        total_benchmarks = BenchmarkEvaluation.objects.count()
        llm_info = provider_info()
        rag_stats = get_collection_stats()

        return Response({
            "sessions": {
                "total": total_sessions,
                "completed": completed_sessions,
                "running": running_sessions,
                "failed": failed_sessions,
                "total_web_sources": totals["total_web"] or 0,
                "total_rag_chunks": totals["total_rag"] or 0,
                "total_revisions": totals["total_revisions"] or 0,
                "avg_duration_seconds": round(totals["avg_duration"] or 0, 2),
            },
            "benchmarks": {
                "total_runs": total_benchmarks,
            },
            "providers": llm_info,
            "rag": {
                "collections": rag_stats,
                "total_indexed_documents": sum(rag_stats.values()),
            },
        })


# ── RAG Sandbox Endpoints ────────────────────────────────────────────


class RAGStatsAPIView(APIView):
    """Get vector store statistics."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from rag.vector_store import get_collection_stats
        from config.setting import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

        stats = get_collection_stats()
        return Response({
            "collections": stats,
            "embedding_model": EMBEDDING_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
        })


class RAGQueryAPIView(APIView):
    """Query the RAG vector store directly with similarity scoring."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        query = request.data.get("query", "").strip()
        collection = request.data.get("collection", "research_docs")
        k = max(1, min(20, int(request.data.get("k", 5))))

        if not query:
            return Response({"error": "Query string is required."}, status=status.HTTP_400_BAD_REQUEST)

        from rag.vector_store import search_with_scores
        results = search_with_scores(query, collection_name=collection, k=k)
        return Response({
            "query": query,
            "collection": collection,
            "count": len(results),
            "results": results,
        })


# ── Export Endpoint ──────────────────────────────────────────────────


class ExportReportAPIView(APIView):
    """Export research session report into Markdown, JSON, HTML, or BibTeX."""

    permission_classes = [permissions.AllowAny]

    def perform_content_negotiation(self, request, force=False):
        from rest_framework.renderers import JSONRenderer, BaseRenderer
        fmt = (request.query_params.get("format") or request.query_params.get("export_format") or "markdown").lower()
        if fmt == "json":
            return (JSONRenderer(), "application/json")
        class PassthroughRenderer(BaseRenderer):
            media_type = "text/plain"
            format = "txt"
            def render(self, data, accepted_media_type=None, renderer_context=None):
                return data
        return (PassthroughRenderer(), "text/plain")

    def get(self, request, pk):
        try:
            session = ResearchSession.objects.get(pk=pk)
        except ResearchSession.DoesNotExist:
            return Response({"error": "Research session not found."}, status=status.HTTP_404_NOT_FOUND)

        fmt = (request.query_params.get("format") or request.query_params.get("export_format") or "markdown").lower()
        title = session.topic
        report = session.final_report or ""

        if fmt == "json":
            from .serializers import ResearchSessionDetailSerializer
            return Response(ResearchSessionDetailSerializer(session).data, content_type="application/json")

        elif fmt == "bibtex":
            sources = session.sources.all()
            bib_entries = []
            for i, src in enumerate(sources, 1):
                clean_title = (src.title or src.domain or f"Source {i}").replace("{", "").replace("}", "")
                entry = f"@misc{{ref_{session.id}_{i},\n  title = {{{clean_title}}},\n  url = {{{src.url}}},\n  note = {{Accessed via Multi-Agent Research Orchestrator}}\n}}"
                bib_entries.append(entry)
            bib_content = "\n\n".join(bib_entries) or f"% No sources recorded for research session {session.id}"
            from django.http import HttpResponse
            response = HttpResponse(bib_content, content_type="text/plain; charset=utf-8")
            response["Content-Disposition"] = f'attachment; filename="citations-{session.id}.bib"'
            return response

        elif fmt == "html":
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Research Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 0 auto; padding: 2rem; }}
h1 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }}
h2 {{ color: #1e293b; margin-top: 2rem; }}
code {{ background: #f1f5f9; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.9em; }}
pre {{ background: #0f172a; color: #f8fafc; padding: 1rem; border-radius: 8px; overflow-x: auto; }}
.badge {{ display: inline-block; padding: 0.25rem 0.5rem; background: #e0e7ff; color: #3730a3; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; }}
.meta {{ color: #64748b; font-size: 0.9rem; margin-bottom: 2rem; }}
</style>
</head>
<body>
<div class="badge">Multi-Agent Research Report</div>
<h1>{title}</h1>
<div class="meta">Sources: {session.web_sources_count + session.rag_chunks_count} | Revisions: {session.revision_count} | Generated by Multi-Agent Research Orchestrator</div>
<div class="content">
<pre style="white-space: pre-wrap; font-family: inherit; background: transparent; color: inherit; padding: 0;">{report}</pre>
</div>
</body>
</html>"""
            from django.http import HttpResponse
            response = HttpResponse(html_content, content_type="text/html; charset=utf-8")
            response["Content-Disposition"] = f'attachment; filename="report-{session.id}.html"'
            return response

        else:
            from django.http import HttpResponse
            response = HttpResponse(report, content_type="text/markdown; charset=utf-8")
            response["Content-Disposition"] = f'attachment; filename="report-{session.id}.md"'
            return response
