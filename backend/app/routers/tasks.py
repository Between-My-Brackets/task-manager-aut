"""
Tasks Router
------------
GET    /boards/{board_id}/tasks            — List tasks (filterable by status/priority)
POST   /boards/{board_id}/tasks            — Create a task
GET    /boards/{board_id}/tasks/{task_id}  — Get a specific task
PUT    /boards/{board_id}/tasks/{task_id}  — Update a task
DELETE /boards/{board_id}/tasks/{task_id}  — Delete a task
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.schemas import TaskCreate, TaskOut, TaskPriority, TaskStatus, TaskUpdate
from app.store import store

router = APIRouter(tags=["Tasks"])


def _get_board_for_user(board_id: str, user_id: str) -> dict:
    """Helper: fetch board and assert ownership. Raises 404/403 as needed."""
    board = store.get_board(board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if board["owner_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return board


@router.get("/boards/{board_id}/tasks", response_model=list[TaskOut])
def list_tasks(
    board_id: str,
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority_filter: TaskPriority | None = Query(None, alias="priority"),
    current_user: dict = Depends(get_current_user),
) -> list:
    """
    List all tasks in a board.
    Supports optional ?status= and ?priority= query filters.
    """
    _get_board_for_user(board_id, current_user["id"])
    return store.list_tasks(
        board_id,
        status=status_filter.value if status_filter else None,
        priority=priority_filter.value if priority_filter else None,
    )


@router.post(
    "/boards/{board_id}/tasks",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    board_id: str,
    payload: TaskCreate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Create a new task within the specified board."""
    _get_board_for_user(board_id, current_user["id"])

    now = datetime.now(UTC)
    task = {
        "id": str(uuid.uuid4()),
        "board_id": board_id,
        "title": payload.title,
        "description": payload.description,
        "status": payload.status.value,
        "priority": payload.priority.value,
        "created_at": now,
        "updated_at": now,
    }
    store.create_task(task)
    return task


@router.get("/boards/{board_id}/tasks/{task_id}", response_model=TaskOut)
def get_task(
    board_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get a specific task by ID."""
    _get_board_for_user(board_id, current_user["id"])

    task = store.get_task(task_id)
    if not task or task["board_id"] != board_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/boards/{board_id}/tasks/{task_id}", response_model=TaskOut)
def update_task(
    board_id: str,
    task_id: str,
    payload: TaskUpdate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Update a task's fields.
    Only provided fields are updated (partial update pattern).
    """
    _get_board_for_user(board_id, current_user["id"])

    task = store.get_task(task_id)
    if not task or task["board_id"] != board_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updates = payload.model_dump(exclude_unset=True)
    # Convert enums to their string values for storage
    if "status" in updates and updates["status"]:
        updates["status"] = updates["status"].value
    if "priority" in updates and updates["priority"]:
        updates["priority"] = updates["priority"].value
    updates["updated_at"] = datetime.now(UTC)

    return store.update_task(task_id, updates)


@router.delete("/boards/{board_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    board_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Delete a specific task."""
    _get_board_for_user(board_id, current_user["id"])

    task = store.get_task(task_id)
    if not task or task["board_id"] != board_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    store.delete_task(task_id)
