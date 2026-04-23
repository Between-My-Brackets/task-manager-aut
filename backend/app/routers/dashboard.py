"""
GET /dashboard/stats — Dashboard statistics for the current user
"""

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.schemas import DashboardStats
from app.store import store

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Return aggregated stats for the current user:
    - Total boards
    - Total tasks
    - Tasks broken down by status
    - Tasks broken down by priority
    """
    return store.get_stats(current_user["id"])
