import uuid

from sqlalchemy.orm import Session

from app.models.itinerary import Itinerary
from app.schemas.itinerary import ItineraryCreate


def create_itinerary(db: Session, itinerary_data: ItineraryCreate) -> Itinerary:
    itinerary = Itinerary(**itinerary_data.model_dump())

    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)

    return itinerary


def get_itinerary_by_trip(db: Session, trip_id: uuid.UUID) -> Itinerary | None:
    return (
        db.query(Itinerary)
        .filter(Itinerary.trip_id == trip_id)
        .first()
    )
