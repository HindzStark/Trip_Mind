from typing import TypedDict, Literal, NotRequired
from datetime import date



class TripState(TypedDict):
    source_city:str
    destination_city:str
    trip_days:int
    start_date: date
    travel_included:bool
    budget:int
    adults:int 
    children:int
    interests:NotRequired[str]
    status:Literal["pending","processing","completed","failed"]
    trip_context: NotRequired[dict]
    weather: NotRequired[dict]
    flights: NotRequired[dict]
    hotels: NotRequired[list[dict]]
    attractions: NotRequired[list[dict]]
    budget_breakdown: NotRequired[dict]
    itinerary: NotRequired[dict]



