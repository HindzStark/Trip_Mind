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

    

    trip = Trip(

        user_id=user_id,

        **trip_data.model_dump()                                          

                                                                 

                                            

                                                 

    )

    db.add(trip)                                                        

    db.commit()                                                       

    db.refresh(trip)                                                    

    return trip

def get_trips_by_user(db: Session, user_id: uuid.UUID) -> list[Trip]:

    

    return (

        db.query(Trip)

        .filter(Trip.user_id == user_id)                             

        .all()                                                               

    )

def get_trip_by_id(db: Session, trip_id: uuid.UUID) -> Trip | None:

    

    return (

        db.query(Trip)

        .filter(Trip.id == trip_id)

        .first()

    )

def update_trip(db: Session, trip: Trip, trip_data: TripUpdate) -> Trip:

    

    update_data = trip_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():

        setattr(trip, key, value)                           

    db.commit()                                                             

    db.refresh(trip)

    return trip

def delete_trip(db: Session, trip: Trip) -> None:

    

    db.delete(trip)                                           

    db.commit()

