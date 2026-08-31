"""Benchmark execution and history contracts."""
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import BenchmarkEvaluation


def _auth(user):
    return f"Token {Token.objects.create(user=user).key}"


@pytest.mark.django_db
class TestRunBenchmark:
    def test_missing_topic(self, client):
        resp = client.post("/api/research/benchmark/", {}, content_type="application/json")
        assert resp.status_code == 400

    def test_success(self, client, mock_research_graph, mock_benchmark):
        resp = client.post(
            "/api/research/benchmark/",
            {"topic": "rag best practices"},
            content_type="application/json",
        )
        data = resp.json()
        assert data["topic"] == "rag best practices"
        assert data["evaluation_metrics"]["verdict"] == "MULTI_AGENT_SUPERIOR"

        row = BenchmarkEvaluation.objects.get(topic="rag best practices")
        assert row.multi_agent_depth == 9
        assert row.verdict == "MULTI_AGENT_SUPERIOR"

    def test_links_to_authenticated_user(self, client, mock_research_graph, mock_benchmark):
        user = User.objects.create_user(username="alice", password="pw123456")
        client.post(
            "/api/research/benchmark/",
            {"topic": "auth test"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth(user),
        )
        assert BenchmarkEvaluation.objects.get(topic="auth test").user == user

    def test_pipeline_error(self, client, exploding_research_graph, mock_benchmark):
        resp = client.post(
            "/api/research/benchmark/",
            {"topic": "anything"},
            content_type="application/json",
        )
        assert resp.status_code == 500
        assert BenchmarkEvaluation.objects.count() == 0


@pytest.mark.django_db
class TestBenchmarkHistory:
    def _create(self, topic, user=None):
        return BenchmarkEvaluation.objects.create(
            topic=topic, single_agent_depth=1, multi_agent_depth=1,
            single_agent_verifiability=1, multi_agent_verifiability=1,
            verdict="COMPARABLE", user=user,
        )

    def test_newest_first(self, client):
        self._create("older")
        self._create("newer")
        resp = client.get("/api/benchmark/history/")
        assert [r["topic"] for r in resp.json()] == ["newer", "older"]

    def test_limit(self, client):
        for name in ("a", "b", "c"):
            self._create(name)
        assert len(client.get("/api/benchmark/history/?limit=2").json()) == 2

    def test_empty(self, client):
        assert client.get("/api/benchmark/history/").json() == []

    @pytest.mark.parametrize("auth_fn,expected_count", [
        (None, 3),       # unauthenticated sees all
        ("alice", 2),    # authenticated sees own only
        ("bob", 1),
    ])
    def test_auth_filtering(self, client, auth_fn, expected_count):
        alice = User.objects.create_user(username="alice", password="pw123456")
        bob = User.objects.create_user(username="bob", password="pw123456")
        self._create("a1", user=alice)
        self._create("b1", user=bob)
        self._create("a2", user=alice)

        headers = {}
        if auth_fn == "alice":
            headers["HTTP_AUTHORIZATION"] = _auth(alice)
        elif auth_fn == "bob":
            headers["HTTP_AUTHORIZATION"] = _auth(bob)

        assert len(client.get("/api/benchmark/history/", **headers).json()) == expected_count

    def test_admin_sees_all(self, client):
        admin = User.objects.create_superuser(username="admin", password="pw123456")
        alice = User.objects.create_user(username="alice", password="pw123456")
        self._create("admin", user=admin)
        self._create("alice", user=alice)
        assert len(client.get("/api/benchmark/history/", HTTP_AUTHORIZATION=_auth(admin)).json()) == 2
