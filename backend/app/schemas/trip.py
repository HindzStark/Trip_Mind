import uuid

from datetime import datetime, date

from pydantic import BaseModel, ConfigDict

                                                           

class TripCreate(BaseModel):

    

    source_city: str

    destination_city: str

    trip_days: int

    start_date: date

    travel_included: bool = False                                        

    budget: int

    adults: int = 1                                                  

    children: int = 0                                                

    interests: str | None = None                      

class TripUpdate(BaseModel):

    

    source_city: str | None = None

    destination_city: str | None = None

    trip_days: int | None = None

    start_date: date | None = None

    travel_included: bool | None = None

    budget: int | None = None

    adults: int | None = None

    children: int | None = None

    interests: str | None = None

    status: str | None = None

                                                         

class TripResponse(BaseModel):

    

    id: uuid.UUID

    user_id: uuid.UUID

    source_city: str

    destination_city: str

    trip_days: int

    start_date: date | None

    travel_included: bool

    budget: int

    adults: int

    children: int

    interests: str | None

    status: str

    trip_context: dict | None = None

    weather: dict | None = None

    flights: dict | None = None

    hotels: list[dict] | None = None

    attractions: list[dict] | None = None

    budget_breakdown: dict | None = None

    itinerary: dict | None = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

