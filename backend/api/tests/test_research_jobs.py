"""Research job creation, listing, and document upload contracts."""
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import ResearchSession


def _auth(user):
    return f"Token {Token.objects.create(user=user).key}"


@pytest.fixture(autouse=True)
def run_jobs_inline(settings):
    settings.RESEARCH_RUNS_ASYNC = False


@pytest.mark.django_db(transaction=True)
class TestCreateJob:
    def test_success(self, client, mock_research_graph):
        user = User.objects.create_user(username="alice", password="pw123456")
        resp = client.post(
            "/api/research/jobs/",
            {"topic": "solid-state batteries"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth(user),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "completed"
        assert data["final_report"].startswith("# Research Report")
        assert data["web_sources_count"] == 2
        assert len(data["sources"]) == 3

    def test_requires_auth(self, client):
        resp = client.post("/api/research/jobs/", {"topic": "test"}, content_type="application/json")
        assert resp.status_code == 401

    def test_rejects_blank_topic(self, client):
        user = User.objects.create_user(username="alice", password="pw123456")
        resp = client.post(
            "/api/research/jobs/",
            {"topic": "   "},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth(user),
        )
        assert resp.status_code == 400


@pytest.mark.django_db
class TestJobPrivacy:
    def test_other_user_cannot_view(self, client):
        alice = User.objects.create_user(username="alice", password="pw123456")
        bob = User.objects.create_user(username="bob", password="pw123456")
        job = ResearchSession.objects.create(user=alice, topic="private", final_report="r")
        resp = client.get(f"/api/research/jobs/{job.id}/", HTTP_AUTHORIZATION=_auth(bob))
        assert resp.status_code == 404

    def test_list_scoped_to_caller(self, client):
        alice = User.objects.create_user(username="alice", password="pw123456")
        bob = User.objects.create_user(username="bob", password="pw123456")
        ResearchSession.objects.create(user=alice, topic="alice", final_report="r")
        ResearchSession.objects.create(user=bob, topic="bob", final_report="r")
        resp = client.get("/api/research/jobs/", HTTP_AUTHORIZATION=_auth(alice))
        assert resp.json()["total"] == 1
        assert resp.json()["jobs"][0]["topic"] == "alice"


@pytest.mark.django_db
class TestDocumentUpload:
    def test_rejects_non_pdf(self, client):
        from django.core.files.uploadedfile import SimpleUploadedFile

        user = User.objects.create_user(username="alice", password="pw123456")
        resp = client.post(
            "/api/research/documents/",
            {"files": [SimpleUploadedFile("notes.txt", b"not pdf", content_type="text/plain")]},
            HTTP_AUTHORIZATION=_auth(user),
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == "unsupported_file_type"
