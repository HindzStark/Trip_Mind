from fastapi import APIRouter, Depends, HTTPException, status

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from google.oauth2 import id_token

from google.auth.transport import requests

from app.db.session import get_db

from app.schemas.user import UserCreate, UserResponse, UserLogin, Token

from app.services import user as user_service

from app.core.security import create_access_token

from app.core.config import settings

from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)

def register_user(user_data: UserCreate, db: Session = Depends(get_db)):

    existing_user = user_service.get_user_by_email(db, email=user_data.email)

    if existing_user:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Oops! That email is already registered."

        )

    return user_service.create_user(db=db, user_data=user_data)

@router.post("/login", response_model=Token)

def login_user(

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: Session = Depends(get_db)

):

    user_login_data = UserLogin(email=form_data.username, password=form_data.password)

    user = user_service.authenticate_user(db, user_login_data)

    

    if not user:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Wait! The email or password you entered is incorrect.",

            headers={"WWW-Authenticate": "Bearer"},

        )

        

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}

class GoogleTokenInput(UserCreate.__base__):                                                    

    pass

from pydantic import BaseModel

class GoogleToken(BaseModel):

    id_token: str

@router.post("/google", response_model=Token)

def google_login(token_data: GoogleToken, db: Session = Depends(get_db)):

    try:

        id_info = id_token.verify_oauth2_token(

            token_data.id_token,

            requests.Request(),

            settings.GOOGLE_CLIENT_ID

        )

        email = id_info["email"]

        full_name = id_info.get("name")

    except Exception as e:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=f"Invalid Google token: {str(e)}"

        )

    user = user_service.get_user_by_email(db, email=email)

    

    if not user:

        user = User(

            email=email,

            full_name=full_name,

            hashed_password=""

        )

        db.add(user)

        db.commit()

        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}

