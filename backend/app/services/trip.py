# ============================================================
# services/trip.py — Business logic for Trip
# ============================================================
#
# WHAT IS A SERVICE?
#   The service layer contains the actual logic:
#     "create a trip", "get all trips for a user", "delete a trip"
#
#   It sits BETWEEN the route and the model:
#     Route (receives request) → Service (does the work) → Model (talks to DB)
#
# WHY NOT PUT THIS IN THE ROUTE?
#   Separation of concerns:
#     - Route = HTTP stuff (request, response, status codes)
#     - Service = logic (create, read, update, delete)
#     - Model = database stuff
#
#   If you put everything in the route, it becomes a 200-line mess.
#   With services, each file has ONE job.
#
# HOW DOES db.query() WORK?
#   db = a SQLAlchemy Session (from get_db() in session.py)
#
#   db.query(Trip)           → SELECT * FROM trips
#   db.query(Trip).filter()  → SELECT * FROM trips WHERE ...
#   db.add(trip)             → stages an INSERT (doesn't save yet!)
#   db.commit()              → actually saves to PostgreSQL
#   db.refresh(trip)         → re-reads the trip from DB (gets auto-filled fields)
# ============================================================

import uuid

from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate
from app.graph.workflow import app_graph


def run_trip_planning_workflow(db: Session, trip_id: uuid.UUID):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return

    trip.status = "processing"
    db.commit()

    initial_state = {
        "source_city": trip.source_city,
        "destination_city": trip.destination_city,
        "trip_days": trip.trip_days,
        "start_date": trip.start_date,
        "travel_included": trip.travel_included,
        "budget": trip.budget,
        "adults": trip.adults,
        "children": trip.children,
        "interests": trip.interests,
        "status": "processing"
    }

    try:
        final_state = app_graph.invoke(initial_state)
        
        if final_state.get("status") == "failed":
            trip.status = "failed"
        else:
            trip.status = final_state.get("status", "completed")
            trip.trip_context = final_state.get("trip_context")
            trip.weather = final_state.get("weather")
            trip.flights = final_state.get("flights")
            hotels_data = final_state.get("hotels")
            if isinstance(hotels_data, dict) and "hotel_options" in hotels_data:
                trip.hotels = hotels_data["hotel_options"]
            else:
                trip.hotels = hotels_data
            trip.attractions = final_state.get("attractions")
            trip.budget_breakdown = final_state.get("budget_breakdown")
            trip.itinerary = final_state.get("itinerary")
            
        db.commit()
    except Exception as e:
        trip.status = "failed"
        db.commit()
        raise e






def create_trip(db: Session, trip_data: TripCreate, user_id: uuid.UUID) -> Trip:
    """
    Creates a new trip in the database.

    Step by step:
      1. Convert the Pydantic schema → SQLAlchemy model
      2. Add to session (stage the INSERT)
      3. Commit (actually save)
      4. Refresh (get the auto-generated id, created_at, etc.)
      5. Return the model object
    """
    trip = Trip(
        user_id=user_id,
        **trip_data.model_dump()    # ← converts Pydantic schema to a dict
        # model_dump() turns TripCreate(source_city="Delhi", ...)
        # into {"source_city": "Delhi", ...}
        # then ** unpacks it as keyword arguments
    )

    db.add(trip)        # → stages: INSERT INTO trips (...) VALUES (...)
    db.commit()         # → actually executes the INSERT in PostgreSQL
    db.refresh(trip)    # → re-reads the row to get id, created_at, etc.

    return trip


def get_trips_by_user(db: Session, user_id: uuid.UUID) -> list[Trip]:
    """
    Gets ALL trips for a specific user.

    .filter() = WHERE clause
    .all()    = get all matching rows as a list
    """
    return (
        db.query(Trip)
        .filter(Trip.user_id == user_id)    # → WHERE user_id = '...'
        .all()                               # → returns list of Trip objects
    )


def get_trip_by_id(db: Session, trip_id: uuid.UUID) -> Trip | None:
    """
    Gets ONE trip by its ID.

    .filter() = WHERE clause
    .first()  = get the first match, or None if not found
    """
    return (
        db.query(Trip)
        .filter(Trip.id == trip_id)
        .first()
    )


def update_trip(db: Session, trip: Trip, trip_data: TripUpdate) -> Trip:
    """
    Updates an existing trip.

    model_dump(exclude_unset=True):
      Only includes fields the user actually sent.
      If user sends {"budget": 50000}, this returns {"budget": 50000}
      — NOT {"budget": 50000, "source_city": None, "trip_days": None, ...}

    setattr(trip, key, value):
      Same as: trip.budget = 50000
      But lets us do it dynamically in a loop.
    """
    update_data = trip_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(trip, key, value)    # → trip.budget = 50000

    db.commit()         # → UPDATE trips SET budget = 50000 WHERE id = '...'
    db.refresh(trip)

    return trip


def delete_trip(db: Session, trip: Trip) -> None:
    """
    Deletes a trip from the database.
    """
    db.delete(trip)     # → DELETE FROM trips WHERE id = '...'
    db.commit()
