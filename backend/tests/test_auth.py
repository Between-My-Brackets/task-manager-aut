"""Tests for authentication endpoints: /auth/register, /auth/login, /auth/me"""

import pytest
from fastapi.testclient import TestClient


class TestRegister:
    def test_register_success(self, client: TestClient):
        """Happy path: register a new user and get back a user profile."""
        resp = client.post(
            "/auth/register",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "full_name": "Alice Wonder",
                "password": "strongpass1",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert "id" in data
        assert "hashed_password" not in data  # Never expose hash

    def test_register_duplicate_username(self, client: TestClient, registered_user: dict):
        """Registering with an existing username should return 409."""
        resp = client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "other@example.com",
                "password": "anotherpass1",
            },
        )
        assert resp.status_code == 409
        assert "already taken" in resp.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """Invalid email format should return 422 Unprocessable Entity."""
        resp = client.post(
            "/auth/register",
            json={
                "username": "bob",
                "email": "not-an-email",
                "password": "validpass1",
            },
        )
        assert resp.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Password shorter than 8 chars should return 422."""
        resp = client.post(
            "/auth/register",
            json={
                "username": "charlie",
                "email": "charlie@example.com",
                "password": "short",
            },
        )
        assert resp.status_code == 422

    def test_register_short_username(self, client: TestClient):
        """Username shorter than 3 chars should return 422."""
        resp = client.post(
            "/auth/register",
            json={
                "username": "ab",
                "email": "ab@example.com",
                "password": "validpass1",
            },
        )
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient, registered_user: dict):
        """Happy path: login returns a token and user profile."""
        resp = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "securepass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, client: TestClient, registered_user: dict):
        """Wrong password should return 401."""
        resp = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Login with a user that doesn't exist should return 401."""
        resp = client.post(
            "/auth/login",
            json={"username": "nobody", "password": "doesntmatter"},
        )
        assert resp.status_code == 401

    def test_login_case_sensitive_username(self, client: TestClient, registered_user: dict):
        """Usernames must match exactly — 'TestUser' != 'testuser'."""
        resp = client.post(
            "/auth/login",
            json={"username": "TestUser", "password": "securepass123"},
        )
        assert resp.status_code == 401


class TestGetMe:
    def test_get_me_authenticated(self, client: TestClient, auth_headers: dict):
        """Authenticated user can retrieve their own profile."""
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert "hashed_password" not in data

    def test_get_me_unauthenticated(self, client: TestClient):
        """No token should return 401 (HTTPBearer rejects missing credentials)."""
        resp = client.get("/auth/me")
        assert resp.status_code in (401, 403)  # FastAPI version dependent

    def test_get_me_invalid_token(self, client: TestClient):
        """Invalid/tampered token should return 401 (our app rejects bad JWTs)."""
        resp = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer this.is.invalid"},
        )
        assert resp.status_code == 401
