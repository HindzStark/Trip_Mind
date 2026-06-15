# ============================================================
# models/trip.py — The Trip database table
# ============================================================
#
# WHAT IS THIS FILE?
#   This Python class = the "trips" table in PostgreSQL.
#   Each attribute below = one column in that table.
#
# WHAT DOES SQLALCHEMY DO WITH THIS?
#   When you write:    trip = Trip(source_city="Delhi", destination_city="Goa")
#   SQLAlchemy runs:   INSERT INTO trips (source_city, destination_city) VALUES ('Delhi', 'Goa')
#
#   When you write:    db.query(Trip).all()
#   SQLAlchemy runs:   SELECT * FROM trips
#
#   You write Python → SQLAlchemy converts to SQL → PostgreSQL executes it.
#
# WHY INHERIT FROM Base?
#   Base (from db/base.py) registers this class as a database table.
#   Without Base, SQLAlchemy doesn't know this class exists.
# ============================================================

import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, func, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Trip(Base):
    # This becomes the TABLE NAME in PostgreSQL
    __tablename__ = "trips"

    # ---------- COLUMNS ----------
    # Each line below = one column in the "trips" table.
    #
    # Mapped[type] = tells Python what type this column holds
    # mapped_column(...) = tells PostgreSQL the column details (size, nullable, etc.)

    # Primary Key — unique ID for each trip
    # UUID is better than integer IDs (harder to guess, globally unique)
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,        # auto-generates a new UUID for each trip
    )

    # Foreign Key — links this trip to a user
    # "users.id" means: this column references the `id` column in the `users` table
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # Trip details
    source_city: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_city: Mapped[str] = mapped_column(String(100), nullable=False)
    trip_days: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    travel_included: Mapped[bool] = mapped_column(Boolean, default=False)
    budget: Mapped[int] = mapped_column(Integer, nullable=False)        # in INR/USD
    adults: Mapped[int] = mapped_column(Integer, default=1)
    children: Mapped[int] = mapped_column(Integer, default=0)
    interests: Mapped[str | None] = mapped_column(Text, nullable=True)  # "temples, food, beaches"

    # Trip status — tracks where the trip is in the AI pipeline
    # "pending" → "processing" → "completed" or "failed"
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Timestamps — auto-filled by PostgreSQL
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # PostgreSQL fills this when row is INSERTed
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),        # PostgreSQL updates this on every UPDATE
    )

    def __repr__(self) -> str:
        return f"<Trip {self.source_city} → {self.destination_city}>"
