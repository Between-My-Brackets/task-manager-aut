"""
Boards Router
-------------
GET    /boards          — List current user's boards
POST   /boards          — Create a new board
GET    /boards/{id}     — Get a specific board
DELETE /boards/{id}     — Delete a board (owner only)
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.schemas import BoardCreate, BoardOut
from app.store import store

router = APIRouter(prefix="/boards", tags=["Boards"])


def _enrich_board(board: dict) -> dict:
    """Add computed fields to a board dict."""
    tasks = store.list_tasks(board["id"])
    return {**board, "task_count": len(tasks)}


@router.get("", response_model=list[BoardOut])
def list_boards(current_user: dict = Depends(get_current_user)) -> list:
    """Return all boards owned by the current user."""
    boards = store.list_boards(current_user["id"])
    return [_enrich_board(b) for b in boards]


@router.post("", response_model=BoardOut, status_code=status.HTTP_201_CREATED)
def create_board(
    payload: BoardCreate,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Create a new board for the current user."""
    board = {
        "id": str(uuid.uuid4()),
        "name": payload.name,
        "description": payload.description,
        "owner_id": current_user["id"],
        "created_at": datetime.now(timezone.utc),
    }
    store.create_board(board)
    return _enrich_board(board)


@router.get("/{board_id}", response_model=BoardOut)
def get_board(
    board_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get a single board by ID. Only the owner can access it."""
    board = store.get_board(board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if board["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return _enrich_board(board)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Delete a board and all its tasks. Only the owner can delete."""
    board = store.get_board(board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if board["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    store.delete_board(board_id)
