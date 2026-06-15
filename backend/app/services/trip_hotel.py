import uuid

from sqlalchemy.orm import Session

from app.models.trip_hotel import TripHotel
from app.schemas.trip_hotel import TripHotelCreate


def create_trip_hotel(db: Session, hotel_data: TripHotelCreate) -> TripHotel:
    hotel = TripHotel(**hotel_data.model_dump())

    db.add(hotel)
    db.commit()
    db.refresh(hotel)

    return hotel


def create_trip_hotels_bulk(db: Session, hotels: list[TripHotelCreate]) -> list[TripHotel]:
    """Create multiple hotels at once (AI returns several recommendations)."""
    db_hotels = [TripHotel(**h.model_dump()) for h in hotels]

    db.add_all(db_hotels)
    db.commit()
    for h in db_hotels:
        db.refresh(h)

    return db_hotels


def get_hotels_by_trip(db: Session, trip_id: uuid.UUID) -> list[TripHotel]:
    return (
        db.query(TripHotel)
        .filter(TripHotel.trip_id == trip_id)
        .all()
    )
