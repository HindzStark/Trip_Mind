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

    

                                                   

    existing_user = user_service.get_user_by_email(db=db, email=user_data.email)

    if existing_user:

        raise HTTPException(status_code=400, detail="Oops! That email is already taken!")

    user = user_service.create_user(db=db, user_data=user_data)

    return user

@router.post("/login")

def login(

    user_data: UserLogin,

    db: Session = Depends(get_db),

):

    

    user = user_service.authenticate_user(db=db, user_data=user_data)

    if user is None:

        raise HTTPException(status_code=401, detail="Wait, that's not the right email or password!")

                                        

                                           

    return {"message": "Welcome back! Login successful", "user_id": str(user.id)}

