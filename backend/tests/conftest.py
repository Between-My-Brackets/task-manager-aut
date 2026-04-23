"""
Pytest Configuration & Shared Fixtures
----------------------------------------
Provides a fresh TestClient and clean store state for every test.
Tests run against the same FastAPI app but with an isolated in-memory store.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def reset_store():
    """
    Auto-used fixture: reset the in-memory store before each test.
    This ensures complete test isolation — no state leaks between tests.
    """
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client() -> TestClient:
    """Synchronous FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def registered_user(client: TestClient) -> dict:
    """Create and return a test user (without token)."""
    payload = {
        "username": "testuser",
        "email": "test@flowboard.dev",
        "full_name": "Test User",
        "password": "securepass123",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def auth_headers(client: TestClient, registered_user: dict) -> dict:
    """Register a user, log in, and return Authorization headers."""
    resp = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "securepass123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def board(client: TestClient, auth_headers: dict) -> dict:
    """Create a test board and return it."""
    resp = client.post(
        "/boards",
        json={"name": "Test Board", "description": "A board for testing"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()
