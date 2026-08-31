"""Auth endpoint contracts: register, login, logout, profile, change-password."""
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def _token_header(user):
    return f"Token {Token.objects.create(user=user).key}"


@pytest.mark.django_db
class TestRegister:
    def test_success(self, client):
        resp = client.post(
            "/api/auth/register/",
            {"username": "alice", "email": "alice@example.com", "password": "secret1234"},
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["user"]["username"] == "alice"
        assert data["token"]
        assert User.objects.get(username="alice").check_password("secret1234")

    @pytest.mark.parametrize("payload", [
        {},
        {"email": "x@y.com"},
        {"username": "alice", "password": "short"},
    ])
    def test_rejects_invalid(self, client, payload):
        resp = client.post("/api/auth/register/", payload, content_type="application/json")
        assert resp.status_code == 400

    def test_rejects_duplicate_username(self, client):
        User.objects.create_user(username="alice", password="secret1234")
        resp = client.post(
            "/api/auth/register/",
            {"username": "alice", "password": "secret1234"},
            content_type="application/json",
        )
        assert resp.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_success(self, client):
        User.objects.create_user(username="bob", password="hunter21")
        resp = client.post(
            "/api/auth/login/",
            {"username": "bob", "password": "hunter21"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["token"]

    @pytest.mark.parametrize("username,password", [
        ("bob", "wrong"),
        ("nobody", "whatever"),
    ])
    def test_rejects_bad_credentials(self, client, username, password):
        if username == "bob":
            User.objects.create_user(username="bob", password="hunter21")
        resp = client.post(
            "/api/auth/login/",
            {"username": username, "password": password},
            content_type="application/json",
        )
        assert resp.status_code == 401

    def test_reuses_existing_token(self, client):
        user = User.objects.create_user(username="bob", password="hunter21")
        existing = Token.objects.create(user=user)
        resp = client.post(
            "/api/auth/login/",
            {"username": "bob", "password": "hunter21"},
            content_type="application/json",
        )
        assert resp.json()["token"] == existing.key


@pytest.mark.django_db
class TestLogout:
    def test_deletes_token(self, client):
        user = User.objects.create_user(username="carol", password="pw123456")
        token = Token.objects.create(user=user)
        resp = client.post("/api/auth/logout/", HTTP_AUTHORIZATION=f"Token {token.key}")
        assert resp.status_code == 200
        assert not Token.objects.filter(user=user).exists()

    def test_requires_auth(self, client):
        assert client.post("/api/auth/logout/").status_code == 401


@pytest.mark.django_db
class TestProfile:
    def test_get(self, client):
        user = User.objects.create_user(username="dave", password="pw123456", email="dave@test.com")
        resp = client.get("/api/auth/profile/", HTTP_AUTHORIZATION=_token_header(user))
        data = resp.json()
        assert data["username"] == "dave"
        assert data["email"] == "dave@test.com"

    @pytest.mark.parametrize("method,payload", [
        ("put", {"username": "david"}),
        ("patch", {"email": "new@test.com"}),
    ])
    def test_update(self, client, method, payload):
        user = User.objects.create_user(username="dave", password="pw123456")
        resp = getattr(client, method)(
            "/api/auth/profile/",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=_token_header(user),
        )
        assert resp.status_code == 200

    def test_rejects_duplicate_username(self, client):
        User.objects.create_user(username="dave", password="pw123456")
        user2 = User.objects.create_user(username="eve", password="pw123456")
        resp = client.put(
            "/api/auth/profile/",
            {"username": "dave"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_token_header(user2),
        )
        assert resp.status_code == 400

    def test_requires_auth(self, client):
        assert client.get("/api/auth/profile/").status_code == 401


@pytest.mark.django_db
class TestChangePassword:
    def test_success(self, client):
        user = User.objects.create_user(username="frank", password="oldpass123")
        resp = client.post(
            "/api/auth/change-password/",
            {"old_password": "oldpass123", "new_password": "newpass123"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_token_header(user),
        )
        assert resp.status_code == 200
        assert resp.json()["token"]  # new token issued
        user.refresh_from_db()
        assert user.check_password("newpass123")

    @pytest.mark.parametrize("old,new,expected", [
        ("wrongold", "newpass123", 400),
        ("oldpass123", "short", 400),
    ])
    def test_rejects_invalid(self, client, old, new, expected):
        user = User.objects.create_user(username="frank", password="oldpass123")
        resp = client.post(
            "/api/auth/change-password/",
            {"old_password": old, "new_password": new},
            content_type="application/json",
            HTTP_AUTHORIZATION=_token_header(user),
        )
        assert resp.status_code == expected

    def test_requires_auth(self, client):
        resp = client.post(
            "/api/auth/change-password/",
            {"old_password": "x", "new_password": "y"},
            content_type="application/json",
        )
        assert resp.status_code == 401
