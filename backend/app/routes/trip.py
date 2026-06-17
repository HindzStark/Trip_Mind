import uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.trip import TripCreate, TripUpdate, TripResponse

from app.services import trip as trip_service

from app.routes.deps import get_current_user

from app.models.user import User

                                             

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

        raise HTTPException(status_code=404, detail="Sorry, we couldn't find that trip anywhere!")

    if trip.user_id != current_user.id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="No peeking! This trip doesn't belong to you!"

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

        raise HTTPException(status_code=404, detail="Sorry, we couldn't find that trip anywhere!")

    if trip.user_id != current_user.id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="No peeking! This trip doesn't belong to you!"

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

        raise HTTPException(status_code=404, detail="Sorry, we couldn't find that trip anywhere!")

    if trip.user_id != current_user.id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="No peeking! This trip doesn't belong to you!"

        )

    trip_service.delete_trip(db=db, trip=trip)

