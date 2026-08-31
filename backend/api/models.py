from django.db import models
from django.contrib.auth.models import User


class ResearchSession(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.CharField(max_length=512)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    final_report = models.TextField()
    web_sources_count = models.IntegerField(default=0)
    rag_chunks_count = models.IntegerField(default=0)
    revision_count = models.IntegerField(default=0)
    duration_seconds = models.FloatField(null=True, blank=True)
    fact_check_result = models.TextField(blank=True)
    error_code = models.CharField(max_length=64, blank=True)
    error_message = models.TextField(blank=True)
    progress_version = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.topic} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ResearchEvent(models.Model):
    STAGE_CHOICES = [
        ("queued", "Queued"),
        ("researcher", "Researcher"),
        ("analyst", "Analyst"),
        ("fact_checker", "Fact checker"),
        ("writer", "Writer"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    session = models.ForeignKey(
        ResearchSession, related_name="events", on_delete=models.CASCADE
    )
    sequence = models.PositiveIntegerField()
    stage = models.CharField(max_length=32, choices=STAGE_CHOICES)
    message = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "sequence"], name="research_event_session_sequence"
            )
        ]

    def __str__(self):
        return f"{self.session_id} #{self.sequence}: {self.stage}"


class ResearchSource(models.Model):
    SOURCE_TYPE_CHOICES = [("web", "Web"), ("rag", "RAG")]

    session = models.ForeignKey(
        ResearchSession, related_name="sources", on_delete=models.CASCADE
    )
    source_type = models.CharField(max_length=16, choices=SOURCE_TYPE_CHOICES)
    position = models.PositiveIntegerField()
    url = models.URLField(blank=True, max_length=2048)
    title = models.CharField(max_length=512, blank=True)
    domain = models.CharField(max_length=255, blank=True)
    snippet = models.TextField()

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "source_type", "position"],
                name="research_source_session_type_position",
            )
        ]

    def __str__(self):
        return f"{self.session_id} {self.source_type} #{self.position}"


class ResearchTag(models.Model):
    """User-defined or auto-generated tags for research sessions."""
    session = models.ForeignKey(
        ResearchSession, related_name="tags", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=64, db_index=True)

    class Meta:
        unique_together = [("session", "name")]

    def __str__(self):
        return f"{self.session_id}: {self.name}"


class BenchmarkEvaluation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.CharField(max_length=512)
    single_agent_depth = models.IntegerField(default=0)
    multi_agent_depth = models.IntegerField(default=0)
    single_agent_verifiability = models.IntegerField(default=0)
    multi_agent_verifiability = models.IntegerField(default=0)
    verdict = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.topic} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
