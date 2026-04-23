"""Tests for task endpoints and dashboard stats."""

from fastapi.testclient import TestClient


class TestCreateTask:
    def test_create_task_success(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Happy path: create a task with all fields."""
        resp = client.post(
            f"/boards/{board['id']}/tasks",
            json={
                "title": "Implement login page",
                "description": "Create the auth form",
                "status": "todo",
                "priority": "high",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Implement login page"
        assert data["status"] == "todo"
        assert data["priority"] == "high"
        assert data["board_id"] == board["id"]

    def test_create_task_defaults(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Task defaults to status=todo and priority=medium."""
        resp = client.post(
            f"/boards/{board['id']}/tasks",
            json={"title": "Quick task"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "todo"
        assert data["priority"] == "medium"

    def test_create_task_invalid_status(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Invalid status enum value should return 422."""
        resp = client.post(
            f"/boards/{board['id']}/tasks",
            json={"title": "Bad task", "status": "flying"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_create_task_on_nonexistent_board(
        self, client: TestClient, auth_headers: dict
    ):
        """Creating a task on a non-existent board should return 404."""
        resp = client.post(
            "/boards/ghost-board/tasks",
            json={"title": "Orphan task"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestListTasks:
    def test_list_tasks_empty(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """New board has no tasks."""
        resp = client.get(f"/boards/{board['id']}/tasks", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_tasks_filter_by_status(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Filter tasks by status query param."""
        # Create tasks with different statuses
        for title, status in [
            ("Task A", "todo"),
            ("Task B", "in_progress"),
            ("Task C", "done"),
        ]:
            client.post(
                f"/boards/{board['id']}/tasks",
                json={"title": title, "status": status},
                headers=auth_headers,
            )

        resp = client.get(
            f"/boards/{board['id']}/tasks?status=todo",
            headers=auth_headers,
        )
        tasks = resp.json()
        assert len(tasks) == 1
        assert tasks[0]["status"] == "todo"

    def test_list_tasks_filter_by_priority(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Filter tasks by priority query param."""
        for title, priority in [
            ("Low task", "low"),
            ("High task 1", "high"),
            ("High task 2", "high"),
        ]:
            client.post(
                f"/boards/{board['id']}/tasks",
                json={"title": title, "priority": priority},
                headers=auth_headers,
            )

        resp = client.get(
            f"/boards/{board['id']}/tasks?priority=high",
            headers=auth_headers,
        )
        assert len(resp.json()) == 2


class TestUpdateTask:
    def test_update_task_status(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Move a task from todo to in_progress."""
        create_resp = client.post(
            f"/boards/{board['id']}/tasks",
            json={"title": "Work item"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        update_resp = client.put(
            f"/boards/{board['id']}/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "in_progress"
        assert update_resp.json()["title"] == "Work item"  # Unchanged

    def test_update_task_partial(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Partial update: only the provided fields change."""
        create_resp = client.post(
            f"/boards/{board['id']}/tasks",
            json={"title": "Old Title", "priority": "low"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        update_resp = client.put(
            f"/boards/{board['id']}/tasks/{task_id}",
            json={"priority": "high"},
            headers=auth_headers,
        )
        data = update_resp.json()
        assert data["priority"] == "high"
        assert data["title"] == "Old Title"  # Unchanged

    def test_update_nonexistent_task(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Updating a non-existent task should return 404."""
        resp = client.put(
            f"/boards/{board['id']}/tasks/ghost",
            json={"status": "done"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestDeleteTask:
    def test_delete_task_success(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Delete a task and confirm it's gone."""
        create_resp = client.post(
            f"/boards/{board['id']}/tasks",
            json={"title": "To be deleted"},
            headers=auth_headers,
        )
        task_id = create_resp.json()["id"]

        del_resp = client.delete(
            f"/boards/{board['id']}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert del_resp.status_code == 204

        get_resp = client.get(
            f"/boards/{board['id']}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 404


class TestDashboardStats:
    def test_stats_empty_user(self, client: TestClient, auth_headers: dict):
        """Fresh user should have all-zero stats."""
        resp = client.get("/dashboard/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_boards"] == 0
        assert data["total_tasks"] == 0

    def test_stats_with_data(
        self, client: TestClient, auth_headers: dict, board: dict
    ):
        """Stats should reflect actual boards and tasks."""
        # Create tasks with mixed statuses
        for title, status, priority in [
            ("Task 1", "todo", "high"),
            ("Task 2", "in_progress", "medium"),
            ("Task 3", "done", "low"),
        ]:
            client.post(
                f"/boards/{board['id']}/tasks",
                json={"title": title, "status": status, "priority": priority},
                headers=auth_headers,
            )

        resp = client.get("/dashboard/stats", headers=auth_headers)
        data = resp.json()

        assert data["total_boards"] == 1
        assert data["total_tasks"] == 3
        assert data["tasks_by_status"]["todo"] == 1
        assert data["tasks_by_status"]["in_progress"] == 1
        assert data["tasks_by_status"]["done"] == 1
        assert data["tasks_by_priority"]["high"] == 1
        assert data["tasks_by_priority"]["medium"] == 1
        assert data["tasks_by_priority"]["low"] == 1
