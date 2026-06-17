import uuid

from datetime import datetime, date

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, func, Date, JSON

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Trip(Base):

                                               

    __tablename__ = "trips"

                                   

                                                        

     

                                                             

                                                                                     

                                           

                                                                        

    id: Mapped[uuid.UUID] = mapped_column(

        primary_key=True,

        default=uuid.uuid4,                                                 

    )

                                             

                                                                                   

    user_id: Mapped[uuid.UUID] = mapped_column(

        ForeignKey("users.id"),

        nullable=False,

    )

                  

    source_city:  Mapped[str]  =  mapped_column(String(100), nullable=False)

    destination_city:  Mapped[str]  =  mapped_column(String(100), nullable=False)

    trip_days: Mapped[int] = mapped_column(Integer, nullable=False)

    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    travel_included: Mapped[bool] = mapped_column(Boolean, default=False)

    budget: Mapped[int] = mapped_column(Integer, nullable=False)                    

    adults: Mapped[int] = mapped_column(Integer, default=1)

    children: Mapped[int] = mapped_column(Integer, default=0)

    interests: Mapped[str | None] = mapped_column(Text, nullable=True)                            

                                                               

                                                        

    status: Mapped[str] = mapped_column(String(20), default="pending")

                                         

    trip_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    weather: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    flights: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    hotels: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

    attractions: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

    budget_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    itinerary: Mapped[dict | None] = mapped_column(JSON, nullable=True)

                                            

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        server_default=func.now(),                                              

    )

    updated_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        server_default=func.now(),

        onupdate=func.now(),                                                 

    )

    def __repr__(self) -> str:

        return f"<Trip {self.source_city} → {self.destination_city}>"

