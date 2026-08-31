# Generated manually for the durable research workspace.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_alter_benchmarkevaluation_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="researchsession",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="researchsession",
            name="error_code",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="researchsession",
            name="error_message",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="researchsession",
            name="fact_check_result",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="researchsession",
            name="progress_version",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="researchsession",
            name="started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="researchsession",
            name="status",
            field=models.CharField(
                choices=[
                    ("queued", "Queued"),
                    ("running", "Running"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                ],
                default="completed",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="ResearchEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sequence", models.PositiveIntegerField()),
                ("stage", models.CharField(choices=[("queued", "Queued"), ("researcher", "Researcher"), ("analyst", "Analyst"), ("fact_checker", "Fact checker"), ("writer", "Writer"), ("completed", "Completed"), ("failed", "Failed")], max_length=32)),
                ("message", models.CharField(max_length=1000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="api.researchsession")),
            ],
            options={"ordering": ["sequence"]},
        ),
        migrations.CreateModel(
            name="ResearchSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_type", models.CharField(choices=[("web", "Web"), ("rag", "RAG")], max_length=16)),
                ("position", models.PositiveIntegerField()),
                ("url", models.URLField(blank=True, max_length=2048)),
                ("title", models.CharField(blank=True, max_length=512)),
                ("domain", models.CharField(blank=True, max_length=255)),
                ("snippet", models.TextField()),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sources", to="api.researchsession")),
            ],
            options={"ordering": ["position"]},
        ),
        migrations.AddConstraint(
            model_name="researchevent",
            constraint=models.UniqueConstraint(fields=("session", "sequence"), name="research_event_session_sequence"),
        ),
        migrations.AddConstraint(
            model_name="researchsource",
            constraint=models.UniqueConstraint(fields=("session", "source_type", "position"), name="research_source_session_type_position"),
        ),
    ]
