"""
DRF API Views for Authentication, User Isolation, Research Tasks, and Evaluation Benchmarking.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import ResearchTask, BenchmarkResult
from .serializers import (
    UserSerializer, RegisterSerializer, 
    ResearchTaskSerializer, BenchmarkResultSerializer
)
from .services import ResearchOrchestratorService, EvaluationBenchmarkService


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "User registered successfully",
                "token": token.key,
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials. Please check your username and password."}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_data = UserSerializer(request.user).data
        task_count = ResearchTask.objects.filter(user=request.user).count()
        bench_count = BenchmarkResult.objects.filter(user=request.user).count()
        
        user_data['stats'] = {
            "total_research_tasks": task_count,
            "total_benchmarks": bench_count
        }
        return Response(user_data)


class StartResearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        topic = request.data.get('topic')
        if not topic:
            return Response({"error": "Field 'topic' is required."}, status=status.HTTP_400_BAD_REQUEST)

        task = ResearchOrchestratorService.execute_research_task(topic, user=request.user)
        serializer = ResearchTaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK if task.status == 'COMPLETED' else status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResearchHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = ResearchTask.objects.filter(user=request.user)
        serializer = ResearchTaskSerializer(tasks, many=True)
        return Response(serializer.data)


class RunEvaluationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        topic = request.data.get('topic')
        if not topic:
            return Response({"error": "Field 'topic' is required."}, status=status.HTTP_400_BAD_REQUEST)

        bench_obj = EvaluationBenchmarkService.run_benchmark_evaluation(topic, user=request.user)
        serializer = BenchmarkResultSerializer(bench_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EvaluationHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = BenchmarkResult.objects.filter(user=request.user)
        serializer = BenchmarkResultSerializer(results, many=True)
        return Response(serializer.data)
