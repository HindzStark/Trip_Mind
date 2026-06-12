import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TripAttractionCreate(BaseModel):
    trip_id: uuid.UUID
    name: str
    category: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class TripAttractionResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    name: str
    category: str | None
    address: str | None
    latitude: float | None
    longitude: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
