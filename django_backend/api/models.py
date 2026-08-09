"""
Django Models for Multi-Agent Research Orchestrator API.
"""

from django.db import models
from django.contrib.auth.models import User


class ResearchTask(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_tasks', null=True, blank=True)
    topic = models.CharField(max_length=500)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    final_report = models.TextField(blank=True, default='')
    revision_count = models.IntegerField(default=0)
    latency_seconds = models.FloatField(default=0.0)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ResearchTask({self.id}): {self.topic[:40]} [{self.status}]"


class BenchmarkResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='benchmark_results', null=True, blank=True)
    topic = models.CharField(max_length=500)
    single_agent_score = models.FloatField(default=0.0)
    multi_agent_score = models.FloatField(default=0.0)
    quality_improvement_pct = models.FloatField(default=0.0)
    winner = models.CharField(max_length=200, default='Multi-Agent Research Orchestrator')
    full_results_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"BenchmarkResult({self.id}): {self.topic[:40]} ({self.multi_agent_score}/10)"
