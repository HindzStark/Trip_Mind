import uuid

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password


def create_user(db: Session, user_data: UserCreate) -> User:
    hashed = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def get_user_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User).filter(User.email == email).first()
    )

def authenticate_user(db: Session, user_data: UserLogin) -> User | None:
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user is None:
        return None
    
    if not verify_password(user_data.password, existing_user.hashed_password):
        return None
    
    return existing_user

def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id)    
        .first()                
    )


    