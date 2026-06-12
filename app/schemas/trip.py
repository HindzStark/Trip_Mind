# ============================================================
# schemas/trip.py — Validates data going IN and OUT of the API
# ============================================================
#
# WHAT IS A SCHEMA?
#   A schema is a "shape checker" for data.
#   Before data enters your database, the schema checks:
#     - Are all required fields present?
#     - Are the types correct? (int is int, not string)
#     - Are values within limits? (trip_days >= 1)
#
# WHY NOT USE THE MODEL DIRECTLY?
#   The Model has EVERYTHING (id, created_at, hashed_password).
#   But when a user CREATES a trip, they shouldn't send `id` or `created_at`.
#   And when you RESPOND, you shouldn't send `hashed_password`.
#
#   So we create different schemas for different situations:
#     TripCreate   → what the user SENDS to create a trip
#     TripUpdate   → what the user SENDS to update a trip
#     TripResponse → what we SEND BACK to the user
#
# MODEL vs SCHEMA:
#   Model  = database table (SQLAlchemy, talks to PostgreSQL)
#   Schema = data shape (Pydantic, talks to the API)
#
# FLOW:
#   User sends JSON → Schema validates it → Service uses it → Model saves to DB
#   DB returns data  → Model holds it     → Schema formats it → User gets JSON
# ============================================================

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ---------- INPUT SCHEMAS (what the user sends) ----------

class TripCreate(BaseModel):
    """
    Shape of data needed to CREATE a new trip.
    Notice: NO id, NO created_at, NO status.
    Those are auto-generated — the user doesn't send them.
    """
    source_city: str
    destination_city: str
    trip_days: int
    travel_included: bool = False           # optional, defaults to False
    budget: int
    adults: int = 1                         # optional, defaults to 1
    children: int = 0                       # optional, defaults to 0
    interests: str | None = None            # optional


class TripUpdate(BaseModel):
    """
    Shape of data needed to UPDATE a trip.
    Everything is optional — user sends ONLY the fields they want to change.
    """
    source_city: str | None = None
    destination_city: str | None = None
    trip_days: int | None = None
    travel_included: bool | None = None
    budget: int | None = None
    adults: int | None = None
    children: int | None = None
    interests: str | None = None
    status: str | None = None


# ---------- OUTPUT SCHEMA (what we send back) ----------

class TripResponse(BaseModel):
    """
    Shape of data we RETURN to the user.
    Includes everything — id, status, timestamps.

    model_config with from_attributes=True:
      This tells Pydantic to read data from SQLAlchemy model attributes.
      Without this, Pydantic can't convert a Trip model object into JSON.

      SQLAlchemy model:  trip.source_city     (attribute access)
      Pydantic needs:    trip["source_city"]   (dict access)
      from_attributes=True makes Pydantic accept BOTH styles.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    source_city: str
    destination_city: str
    trip_days: int
    travel_included: bool
    budget: int
    adults: int
    children: int
    interests: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
