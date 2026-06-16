# ============================================================
# routes/trip.py — API endpoints for Trip
# ============================================================
#
# WHAT IS A ROUTE?
#   A route maps a URL to a Python function.
#   When someone hits POST /trips → the create_trip() function runs.
#
# WHAT IS APIRouter?
#   In main.py, we have one `app`. But if we put ALL routes there,
#   main.py would be 1000 lines long.
#
#   APIRouter lets us define routes in separate files, then "include"
#   them into the main app. Like chapters in a book.
#
# WHAT IS Depends(get_db)?
#   Remember get_db() from session.py?
#   Depends() tells FastAPI: "Before running this route, call get_db()
#   and give me the database session as `db`."
#
#   This is called DEPENDENCY INJECTION — FastAPI "injects" the db
#   session into your function automatically.
#
# WHAT IS response_model?
#   Tells FastAPI: "The response should look like TripResponse."
#   FastAPI will automatically filter out any extra fields.
#
# FULL FLOW FOR POST /trips:
#   1. User sends JSON: {"source_city": "Delhi", "destination_city": "Goa", ...}
#   2. FastAPI validates it against TripCreate schema
#   3. Depends(get_db) creates a database session
#   4. Route calls service.create_trip()
#   5. Service creates a Trip model, saves to DB
#   6. Service returns the Trip model
#   7. FastAPI converts it to TripResponse schema → JSON
#   8. User receives the response
# ============================================================

import uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.trip import TripCreate, TripUpdate, TripResponse
from app.services import trip as trip_service
from app.routes.deps import get_current_user
from app.models.user import User

# Create a router for all trip-related routes
router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("/", response_model=TripResponse, status_code=201)
def create_trip(
    trip_data: TripCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = trip_service.create_trip(db=db, trip_data=trip_data, user_id=current_user.id)
    background_tasks.add_task(trip_service.run_trip_planning_workflow, db, trip.id)
    return trip


@router.get("/", response_model=list[TripResponse])
def get_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return trip_service.get_trips_by_user(db=db, user_id=current_user.id)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = trip_service.get_trip_by_id(db=db, trip_id=trip_id)

    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this trip"
        )

    return trip


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: uuid.UUID,
    trip_data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = trip_service.get_trip_by_id(db=db, trip_id=trip_id)

    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this trip"
        )

    return trip_service.update_trip(db=db, trip=trip, trip_data=trip_data)


@router.delete("/{trip_id}", status_code=204)
def delete_trip(
    trip_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = trip_service.get_trip_by_id(db=db, trip_id=trip_id)

    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this trip"
        )

    trip_service.delete_trip(db=db, trip=trip)

