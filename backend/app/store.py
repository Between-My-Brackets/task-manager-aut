"""
In-Memory Data Store
--------------------
Thread-safe singleton that acts as the application's storage layer.
All data lives in memory — zero external dependencies required.

To migrate to a real database later:
  - Keep the same service interfaces
  - Replace the store calls in services/ with SQLAlchemy queries
  - Data models (Pydantic) stay unchanged
"""

import threading
from typing import Any


class InMemoryStore:
    """
    Centralized in-memory store for all application data.
    Uses a reentrant lock for thread safety.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._users: dict[str, dict[str, Any]] = {}       # username → user dict
        self._boards: dict[str, dict[str, Any]] = {}      # board_id → board dict
        self._tasks: dict[str, dict[str, Any]] = {}       # task_id → task dict

    # ── User Operations ───────────────────────────────────────────────────────

    def get_user(self, username: str) -> dict[str, Any] | None:
        with self._lock:
            return self._users.get(username)

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        with self._lock:
            return next(
                (u for u in self._users.values() if u["id"] == user_id), None
            )

    def create_user(self, user: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._users[user["username"]] = user
            return user

    def list_users(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._users.values())

    # ── Board Operations ──────────────────────────────────────────────────────

    def get_board(self, board_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._boards.get(board_id)

    def list_boards(self, owner_id: str) -> list[dict[str, Any]]:
        with self._lock:
            return [b for b in self._boards.values() if b["owner_id"] == owner_id]

    def create_board(self, board: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._boards[board["id"]] = board
            return board

    def delete_board(self, board_id: str) -> bool:
        with self._lock:
            if board_id not in self._boards:
                return False
            del self._boards[board_id]
            # Cascade delete tasks belonging to this board
            self._tasks = {
                tid: t
                for tid, t in self._tasks.items()
                if t["board_id"] != board_id
            }
            return True

    # ── Task Operations ───────────────────────────────────────────────────────

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(
        self,
        board_id: str,
        status: str | None = None,
        priority: str | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            tasks = [t for t in self._tasks.values() if t["board_id"] == board_id]
            if status:
                tasks = [t for t in tasks if t["status"] == status]
            if priority:
                tasks = [t for t in tasks if t["priority"] == priority]
            return sorted(tasks, key=lambda t: t["created_at"], reverse=True)

    def create_task(self, task: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._tasks[task["id"]] = task
            return task

    def update_task(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            if task_id not in self._tasks:
                return None
            self._tasks[task_id].update(updates)
            return self._tasks[task_id]

    def delete_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            return True

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self, owner_id: str) -> dict[str, Any]:
        with self._lock:
            boards = self.list_boards(owner_id)
            board_ids = {b["id"] for b in boards}
            tasks = [t for t in self._tasks.values() if t["board_id"] in board_ids]

            return {
                "total_boards": len(boards),
                "total_tasks": len(tasks),
                "tasks_by_status": {
                    "todo": sum(1 for t in tasks if t["status"] == "todo"),
                    "in_progress": sum(1 for t in tasks if t["status"] == "in_progress"),
                    "done": sum(1 for t in tasks if t["status"] == "done"),
                },
                "tasks_by_priority": {
                    "low": sum(1 for t in tasks if t["priority"] == "low"),
                    "medium": sum(1 for t in tasks if t["priority"] == "medium"),
                    "high": sum(1 for t in tasks if t["priority"] == "high"),
                },
            }

    def reset(self) -> None:
        """Reset all data. Used in tests to ensure isolation."""
        with self._lock:
            self._users.clear()
            self._boards.clear()
            self._tasks.clear()


# Global singleton — imported by services
store = InMemoryStore()
