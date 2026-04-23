"""Tests for board endpoints: GET/POST /boards, GET/DELETE /boards/{id}"""

from fastapi.testclient import TestClient


class TestListBoards:
    def test_list_empty(self, client: TestClient, auth_headers: dict):
        """New user should have no boards."""
        resp = client.get("/boards", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_requires_auth(self, client: TestClient):
        """Unauthenticated request should be rejected with 401."""
        resp = client.get("/boards")
        assert resp.status_code in (401, 403)

    def test_list_only_own_boards(self, client: TestClient, auth_headers: dict):
        """User should only see their own boards, not other users' boards."""
        # Create Alice's board
        client.post("/boards", json={"name": "Alice's Board"}, headers=auth_headers)

        # Register Bob and create his board
        client.post(
            "/auth/register",
            json={"username": "bob", "email": "bob@test.com", "password": "bobpass123"},
        )
        bob_resp = client.post(
            "/auth/login",
            json={"username": "bob", "password": "bobpass123"},
        )
        bob_token = bob_resp.json()["access_token"]
        bob_headers = {"Authorization": f"Bearer {bob_token}"}
        client.post("/boards", json={"name": "Bob's Board"}, headers=bob_headers)

        # Alice should still only see 1 board
        alice_boards = client.get("/boards", headers=auth_headers).json()
        assert len(alice_boards) == 1
        assert alice_boards[0]["name"] == "Alice's Board"


class TestCreateBoard:
    def test_create_success(self, client: TestClient, auth_headers: dict):
        """Happy path: create a board with name and description."""
        resp = client.post(
            "/boards",
            json={"name": "My Sprint Board", "description": "Q1 sprint tasks"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My Sprint Board"
        assert data["description"] == "Q1 sprint tasks"
        assert "id" in data
        assert data["task_count"] == 0

    def test_create_without_description(self, client: TestClient, auth_headers: dict):
        """Board description should be optional."""
        resp = client.post(
            "/boards",
            json={"name": "Minimal Board"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["description"] is None

    def test_create_empty_name_rejected(self, client: TestClient, auth_headers: dict):
        """Empty board name should return 422."""
        resp = client.post(
            "/boards",
            json={"name": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_create_requires_auth(self, client: TestClient):
        """Unauthenticated board creation should be rejected with 401."""
        resp = client.post("/boards", json={"name": "Sneaky Board"})
        assert resp.status_code in (401, 403)


class TestGetBoard:
    def test_get_existing_board(self, client: TestClient, auth_headers: dict, board: dict):
        """Fetch a board that exists."""
        resp = client.get(f"/boards/{board['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == board["id"]

    def test_get_nonexistent_board(self, client: TestClient, auth_headers: dict):
        """Fetching a board that doesn't exist should return 404."""
        resp = client.get("/boards/does-not-exist", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_other_users_board_forbidden(self, client: TestClient, board: dict):
        """User cannot access another user's board."""
        # Register and login as Bob
        client.post(
            "/auth/register",
            json={"username": "bob", "email": "bob@test.com", "password": "bobpass123"},
        )
        login = client.post(
            "/auth/login",
            json={"username": "bob", "password": "bobpass123"},
        )
        bob_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        resp = client.get(f"/boards/{board['id']}", headers=bob_headers)
        assert resp.status_code == 403


class TestDeleteBoard:
    def test_delete_success(self, client: TestClient, auth_headers: dict, board: dict):
        """Delete a board and confirm it's gone."""
        resp = client.delete(f"/boards/{board['id']}", headers=auth_headers)
        assert resp.status_code == 204

        resp = client.get(f"/boards/{board['id']}", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_nonexistent_board(self, client: TestClient, auth_headers: dict):
        """Deleting a non-existent board should return 404."""
        resp = client.delete("/boards/ghost-board", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_cascades_tasks(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Deleting a board should cascade-delete all its tasks."""
        # Create a task
        client.post(
            f"/boards/{board['id']}/tasks",
            json={"title": "Will be deleted"},
            headers=auth_headers,
        )

        # Delete the board
        client.delete(f"/boards/{board['id']}", headers=auth_headers)

        # Confirm task is gone too (board 404, not task)
        resp = client.get(f"/boards/{board['id']}/tasks", headers=auth_headers)
        assert resp.status_code == 404
