"""
Auth Router
-----------
POST /auth/register  — Create a new user account
POST /auth/login     — Authenticate and receive a JWT
GET  /auth/me        — Get current authenticated user
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserOut
from app.store import store

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate) -> dict:
    """
    Register a new user.
    Returns the created user profile (no password in response).
    """
    if store.get_user(payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{payload.username}' is already taken",
        )

    user = {
        "id": str(uuid.uuid4()),
        "username": payload.username,
        "email": str(payload.email),
        "full_name": payload.full_name,
        "hashed_password": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }
    store.create_user(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> dict:
    """
    Authenticate a user with username + password.
    Returns a JWT access token and user profile.
    """
    user = store.get_user(payload.username)

    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user["id"]})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserOut)
def get_me(current_user: dict = Depends(get_current_user)) -> dict:
    """Return the currently authenticated user's profile."""
    return current_user
