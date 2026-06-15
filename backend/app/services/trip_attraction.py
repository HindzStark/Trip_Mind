import uuid

from sqlalchemy.orm import Session

from app.models.trip_attraction import TripAttraction
from app.schemas.trip_attraction import TripAttractionCreate


def create_trip_attraction(db: Session, attraction_data: TripAttractionCreate) -> TripAttraction:
    attraction = TripAttraction(**attraction_data.model_dump())

    db.add(attraction)
    db.commit()
    db.refresh(attraction)

    return attraction


def create_trip_attractions_bulk(db: Session, attractions: list[TripAttractionCreate]) -> list[TripAttraction]:
    """Create multiple attractions at once (AI returns several)."""
    db_attractions = [TripAttraction(**a.model_dump()) for a in attractions]

    db.add_all(db_attractions)
    db.commit()
    for a in db_attractions:
        db.refresh(a)

    return db_attractions


def get_attractions_by_trip(db: Session, trip_id: uuid.UUID) -> list[TripAttraction]:
    return (
        db.query(TripAttraction)
        .filter(TripAttraction.trip_id == trip_id)
        .all()
    )
