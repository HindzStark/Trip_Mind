import uuid

from datetime import datetime

from pydantic import BaseModel, ConfigDict,EmailStr

class UserCreate(BaseModel):

    email: EmailStr

    full_name: str | None = None

    password: str

class UserLogin(BaseModel):

    email: EmailStr

    password: str

class UserResponse(BaseModel):

    id: uuid.UUID

    email: EmailStr

    full_name: str | None = None

    created_at: datetime

    updated_at: datetime

    model_config= ConfigDict(from_attributes=True)  

class Token(BaseModel):

    access_token: str

    token_type: str

