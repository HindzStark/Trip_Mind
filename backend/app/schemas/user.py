# schemas/user.py — PLACEHOLDER
# Implement: UserCreate, UserResponse, UserLogin
# Same pattern as schemas/trip.py

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    email: str
    full_name: str | None = None
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config= ConfigDict(from_attributes=True)  
    