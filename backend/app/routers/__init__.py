"""Routers package."""

from app.routers.auth import router as auth_router
from app.routers.boards import router as boards_router
from app.routers.dashboard import router as dashboard_router
from app.routers.tasks import router as tasks_router

__all__ = ["auth_router", "boards_router", "tasks_router", "dashboard_router"]
