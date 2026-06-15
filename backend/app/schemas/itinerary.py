import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ItineraryCreate(BaseModel):
    trip_id: uuid.UUID
    itinerary_json: str
    budget_breakdown: str | None = None
    weather_summary: str | None = None


class ItineraryResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    itinerary_json: str
    budget_breakdown: str | None
    weather_summary: str | None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
