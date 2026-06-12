# services/user.py — PLACEHOLDER
# Implement: create_user, authenticate_user, get_user_by_id
# Same pattern as services/trip.py


import uuid

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate , UserLogin
from passlib.context import CryptContext


def create_user(db: Session, user_data: UserCreate) -> User:
    pwd_context = CryptContext(schemes=["bcrypt"])
    hashed = pwd_context.hash(user_data.password)
    user=User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def get_user_by_email(db:Session , email: str)-> User|None :
    return(
        db.query(User).filter(User.email==email).first()
    )

def authenticate_user(db:Session, user_data:UserLogin)->User | None :
    pwd_context = CryptContext(schemes=["bcrypt"])
    existing_user=get_user_by_email(db,user_data.email)
    if(existing_user==None):
        return None
    
    if(pwd_context.verify(user_data.password, existing_user.hashed_password) is False):
        return None
    
    return existing_user

def get_user_by_id(db: Session, user_id: uuid.UUID)-> User:
    return (
        db.query(User)
        .filter(User.id == user_id)    
        .first()                
    )

    