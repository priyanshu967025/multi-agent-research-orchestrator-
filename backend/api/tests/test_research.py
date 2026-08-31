"""Research execution, session list, and session detail contracts."""
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import ResearchSession


def _auth(user):
    return f"Token {Token.objects.create(user=user).key}"


# ── Execute Research ─────────────────────────────────────────────────


@pytest.mark.django_db
class TestExecuteResearch:
    def test_missing_topic(self, client):
        resp = client.post("/api/research/execute/", {}, content_type="application/json")
        assert resp.status_code == 400

    def test_success_persists_session(self, client, mock_research_graph):
        resp = client.post(
            "/api/research/execute/",
            {"topic": "solid state batteries"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"] == "solid state batteries"
        assert data["final_report"].startswith("# Research Report:")
        assert data["sources_count"] == 2
        assert data["session_id"]

        session = ResearchSession.objects.get(id=data["session_id"])
        assert session.status == "completed"
        assert session.user is None  # anonymous

    def test_links_to_authenticated_user(self, client, mock_research_graph):
        user = User.objects.create_user(username="carol", password="pw123456")
        resp = client.post(
            "/api/research/execute/",
            {"topic": "quantum computing"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth(user),
        )
        session = ResearchSession.objects.get(id=resp.json()["session_id"])
        assert session.user == user

    def test_pipeline_error(self, client, exploding_research_graph):
        resp = client.post(
            "/api/research/execute/",
            {"topic": "anything"},
            content_type="application/json",
        )
        assert resp.status_code == 500
        assert ResearchSession.objects.count() == 0


# ── User Sessions ────────────────────────────────────────────────────


@pytest.mark.django_db
class TestUserSessions:
    def test_empty(self, client):
        user = User.objects.create_user(username="alice", password="pw123456")
        resp = client.get("/api/research/sessions/", HTTP_AUTHORIZATION=_auth(user))
        assert resp.json()["total"] == 0

    def test_user_isolation(self, client):
        alice = User.objects.create_user(username="alice", password="pw123456")
        bob = User.objects.create_user(username="bob", password="pw123456")
        ResearchSession.objects.create(user=alice, topic="A", final_report="R")
        ResearchSession.objects.create(user=bob, topic="B", final_report="R")

        resp = client.get("/api/research/sessions/", HTTP_AUTHORIZATION=_auth(alice))
        topics = [s["topic"] for s in resp.json()["sessions"]]
        assert "B" not in topics

    def test_excludes_report(self, client):
        user = User.objects.create_user(username="alice", password="pw123456")
        ResearchSession.objects.create(user=user, topic="t", final_report="secret")
        resp = client.get("/api/research/sessions/", HTTP_AUTHORIZATION=_auth(user))
        assert "final_report" not in resp.json()["sessions"][0]

    def test_pagination(self, client):
        user = User.objects.create_user(username="alice", password="pw123456")
        for i in range(5):
            ResearchSession.objects.create(user=user, topic=f"T{i}", final_report="R")
        resp = client.get(
            "/api/research/sessions/?page=1&page_size=2",
            HTTP_AUTHORIZATION=_auth(user),
        )
        data = resp.json()
        assert data["total"] == 5
        assert len(data["sessions"]) == 2

    def test_requires_auth(self, client):
        assert client.get("/api/research/sessions/").status_code == 401


# ── Session Detail ───────────────────────────────────────────────────


@pytest.mark.django_db
class TestSessionDetail:
    def test_get(self, client):
        user = User.objects.create_user(username="alice", password="pw123456")
        s = ResearchSession.objects.create(user=user, topic="t", final_report="# Report")
        resp = client.get(f"/api/research/sessions/{s.id}/", HTTP_AUTHORIZATION=_auth(user))
        assert resp.status_code == 200
        assert resp.json()["final_report"] == "# Report"

    @pytest.mark.parametrize("method", ["get", "delete"])
    def test_not_found(self, client, method):
        user = User.objects.create_user(username="alice", password="pw123456")
        resp = getattr(client, method)("/api/research/sessions/99999/", HTTP_AUTHORIZATION=_auth(user))
        assert resp.status_code == 404

    def test_delete(self, client):
        user = User.objects.create_user(username="alice", password="pw123456")
        s = ResearchSession.objects.create(user=user, topic="t", final_report="x")
        resp = client.delete(f"/api/research/sessions/{s.id}/", HTTP_AUTHORIZATION=_auth(user))
        assert resp.status_code == 204
        assert not ResearchSession.objects.filter(id=s.id).exists()

    def test_other_user_forbidden(self, client):
        alice = User.objects.create_user(username="alice", password="pw123456")
        bob = User.objects.create_user(username="bob", password="pw123456")
        s = ResearchSession.objects.create(user=alice, topic="private", final_report="x")
        assert client.delete(f"/api/research/sessions/{s.id}/", HTTP_AUTHORIZATION=_auth(bob)).status_code == 403
        assert ResearchSession.objects.filter(id=s.id).exists()

    def test_requires_auth(self, client):
        assert client.get("/api/research/sessions/1/").status_code == 401
