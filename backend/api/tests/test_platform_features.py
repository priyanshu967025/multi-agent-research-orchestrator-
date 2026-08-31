"""Tests for platform analytics, RAG querying, export formats, and provider configuration."""
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import ResearchSession, ResearchSource, BenchmarkEvaluation
from config.providers import provider_info, get_provider


def _auth(user):
    return f"Token {Token.objects.create(user=user).key}"


@pytest.mark.django_db
class TestPlatformStats:
    def test_stats_endpoint(self, client):
        user = User.objects.create_user(username="stat_user", password="pw123456")
        ResearchSession.objects.create(
            user=user,
            topic="Quantum ML",
            status="completed",
            final_report="# QML",
            web_sources_count=3,
            rag_chunks_count=2,
            revision_count=1,
            duration_seconds=12.5,
        )
        BenchmarkEvaluation.objects.create(
            user=user,
            topic="Quantum ML",
            single_agent_depth=4,
            multi_agent_depth=8,
            verdict="multi_agent_superior"
        )

        resp = client.get("/api/stats/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["sessions"]["total"] >= 1
        assert data["sessions"]["completed"] >= 1
        assert data["sessions"]["total_web_sources"] >= 3
        assert data["benchmarks"]["total_runs"] >= 1
        assert "providers" in data
        assert "rag" in data


@pytest.mark.django_db
class TestRAGEndpoints:
    def test_rag_stats(self, client):
        resp = client.get("/api/rag/stats/")
        assert resp.status_code == 200
        data = resp.json()
        assert "collections" in data
        assert "embedding_model" in data

    def test_rag_search_missing_query(self, client):
        resp = client.post("/api/rag/search/", {}, content_type="application/json")
        assert resp.status_code == 400

    def test_rag_search_valid(self, client, monkeypatch):
        # Mock search_with_scores to avoid downloading model in test
        monkeypatch.setattr(
            "rag.vector_store.search_with_scores",
            lambda q, collection_name="research_docs", k=5: [
                {"content": "Mocked chunk content", "metadata": {"source": "test.pdf"}, "score": 0.12}
            ]
        )
        resp = client.post(
            "/api/rag/search/",
            {"query": "quantum retrieval", "collection": "research_docs", "k": 3},
            content_type="application/json"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["content"] == "Mocked chunk content"


@pytest.mark.django_db
class TestExportEndpoints:
    def test_export_not_found(self, client):
        resp = client.get("/api/research/sessions/99999/export/")
        assert resp.status_code == 404

    def test_export_markdown(self, client):
        session = ResearchSession.objects.create(
            topic="CRISPR gene drive",
            status="completed",
            final_report="# CRISPR Research\nDetailed findings."
        )
        resp = client.get(f"/api/research/sessions/{session.id}/export/?format=markdown")
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/markdown")
        assert "Detailed findings" in resp.content.decode("utf-8")

    def test_export_html(self, client):
        session = ResearchSession.objects.create(
            topic="CRISPR gene drive",
            status="completed",
            final_report="# CRISPR Research\nDetailed findings."
        )
        resp = client.get(f"/api/research/sessions/{session.id}/export/?format=html")
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/html")
        assert "CRISPR gene drive" in resp.content.decode("utf-8")

    def test_export_json(self, client):
        session = ResearchSession.objects.create(
            topic="CRISPR gene drive",
            status="completed",
            final_report="# CRISPR Research\nDetailed findings."
        )
        resp = client.get(f"/api/research/sessions/{session.id}/export/?format=json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"] == "CRISPR gene drive"

    def test_export_bibtex(self, client):
        session = ResearchSession.objects.create(
            topic="CRISPR gene drive",
            status="completed",
            final_report="# CRISPR Research"
        )
        ResearchSource.objects.create(
            session=session,
            source_type="web",
            position=1,
            url="https://nature.com/articles/crispr",
            title="CRISPR Nature Article",
            domain="nature.com",
            snippet="Article snippet"
        )
        resp = client.get(f"/api/research/sessions/{session.id}/export/?format=bibtex")
        assert resp.status_code == 200
        content = resp.content.decode("utf-8")
        assert "@misc{ref_" in content
        assert "CRISPR Nature Article" in content


class TestProviderConfig:
    def test_provider_info(self):
        info = provider_info()
        assert "active_provider" in info
        assert "available" in info
        assert "gemini" in info["available"]
        assert "groq" in info["available"]
