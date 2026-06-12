import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TripHotelCreate(BaseModel):
    trip_id: uuid.UUID
    hotel_name: str
    hotel_address: str | None = None
    price_per_night: float | None = None
    rating: float | None = None
    source: str | None = None


class TripHotelResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    hotel_name: str
    hotel_address: str | None
    price_per_night: float | None
    rating: float | None
    source: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
