# ============================================================
# routes/user.py — API endpoints for User
# ============================================================
# Same pattern as routes/trip.py, but simpler:
#   POST /users/register → create a new user
#   POST /users/login    → verify credentials
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserLogin, UserResponse, UserCreate
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """POST /users/register — Create a new user account."""

    # Check if email already exists BEFORE creating
    existing_user = user_service.get_user_by_email(db=db, email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_service.create_user(db=db, user_data=user_data)
    return user


@router.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    """POST /users/login — Verify email and password."""

    user = user_service.authenticate_user(db=db, user_data=user_data)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # For now, just confirm login works.
    # Later you'll return a JWT token here.
    return {"message": "Login successful", "user_id": str(user.id)}
