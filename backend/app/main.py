"""
FlowBoard — FastAPI Application Entry Point
"""
#dummy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth_router, boards_router, dashboard_router, tasks_router

# ── Application Factory ───────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "FlowBoard API — Production-grade task management backend. "
        "Built with FastAPI for the DevOps Workshop."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(boards_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)

# ── Health Check ─────────────────────────────────────────────────────────────


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Kubernetes/Docker health check endpoint.
    Returns 200 OK when the service is up and ready.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/", tags=["Root"])
def root() -> dict:
    """API root — redirect hint to docs."""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": "/docs",
        "health": "/health",
    }
