"""
DRF Serializers for Authentication, Research Tasks, and Benchmark Results.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ResearchTask, BenchmarkResult


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class ResearchTaskSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ResearchTask
        fields = [
            'id', 'user', 'username', 'topic', 'status', 
            'final_report', 'revision_count', 'latency_seconds', 
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'final_report', 'revision_count', 'latency_seconds', 'error_message', 'created_at', 'updated_at']


class BenchmarkResultSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = BenchmarkResult
        fields = [
            'id', 'user', 'username', 'topic', 'single_agent_score',
            'multi_agent_score', 'quality_improvement_pct', 'winner',
            'full_results_json', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'single_agent_score', 'multi_agent_score', 'quality_improvement_pct', 'winner', 'full_results_json', 'created_at']
