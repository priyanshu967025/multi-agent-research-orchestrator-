from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ResearchEvent, ResearchSession, ResearchSource, ResearchTag, BenchmarkEvaluation


class UserSerializer(serializers.ModelSerializer):
    research_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined", "research_count"]
        read_only_fields = ["id", "date_joined"]

    def get_research_count(self, obj):
        return ResearchSession.objects.filter(user=obj).count()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class ResearchSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — excludes the full report body."""

    class Meta:
        model = ResearchSession
        fields = [
            "id", "topic", "status", "web_sources_count",
            "rag_chunks_count", "revision_count", "duration_seconds",
            "created_at",
        ]


class ResearchEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchEvent
        fields = ["sequence", "stage", "message", "created_at"]


class ResearchSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchSource
        fields = ["source_type", "position", "url", "title", "domain", "snippet"]


class ResearchTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchTag
        fields = ["id", "name"]


class ResearchJobCreateSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=512, trim_whitespace=True)

    def validate_topic(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Topic cannot be blank.")
        return value


class ResearchSessionDetailSerializer(serializers.ModelSerializer):
    """Full serializer including the report text."""

    user_username = serializers.CharField(source="user.username", read_only=True, default=None)
    events = ResearchEventSerializer(many=True, read_only=True)
    sources = ResearchSourceSerializer(many=True, read_only=True)
    tags = ResearchTagSerializer(many=True, read_only=True)

    class Meta:
        model = ResearchSession
        fields = [
            "id", "user", "user_username", "topic", "status",
            "final_report", "web_sources_count", "rag_chunks_count",
            "revision_count", "duration_seconds", "fact_check_result",
            "error_code", "error_message", "progress_version", "started_at",
            "completed_at", "created_at", "events", "sources", "tags",
        ]
        read_only_fields = ["id", "user", "user_username", "created_at"]


class BenchmarkEvaluationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for history list."""

    class Meta:
        model = BenchmarkEvaluation
        fields = [
            "id", "topic", "single_agent_depth", "multi_agent_depth",
            "single_agent_verifiability", "multi_agent_verifiability",
            "verdict", "created_at",
        ]
