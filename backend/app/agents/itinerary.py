from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.graph.state import TripState
from app.core.config import settings
import json

class Activity(TypedDict):
    time_of_day: Literal["morning", "afternoon", "evening"]
    name: str
    description: str
    duration_minutes: int
    cost_inr: int

class DayPlan(TypedDict):
    day: int
    date: str
    hotel: str
    activities: list[Activity]
    meals: str
    notes: str

class TripPlan(TypedDict):
    days: list[DayPlan]
    packing_list: list[str]
    summary: str

def ItineraryAgent(state: TripState):
    destination = state["destination_city"]
    source = state["source_city"]
    start_date = state["start_date"]
    trip_days = state["trip_days"]
    budget = state["budget"]
    
    trip_context = state.get("trip_context") or {}
    budget_category = trip_context.get("budget_category", "moderate")

    flights = state.get("flights") or {}
    hotels = state.get("hotels") or {}
    weather = state.get("weather") or {}
    attractions = state.get("attractions") or []
    budget_breakdown = state.get("budget_breakdown") or {}

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
    itinerary_llm = llm.with_structured_output(TripPlan)

    template = PromptTemplate(
        template="""You are a professional travel planner. Synthesize all the collected travel details into a cohesive, day-by-day travel plan.

**Trip Specifications:**
- Route: {source} to {destination}
- Start Date: {start_date}
- Duration: {trip_days} days
- Budget Category: {budget_category} (Total Budget: {budget} INR)

**Weather Summary:**
{weather_raw}

**Flight Details (Outbound and return flight transit times):**
{flights_raw}

**Hotel Selection (Lodging recommendation choice for stays):**
{hotels_raw}

**Curated Attraction Spots (Include these in the daily schedules):**
{attractions_raw}

**Budget Breakdown:**
{budget_raw}

**Tasks:**
1. Generate a daily itinerary (`days`) covering all {trip_days} days of the trip.
2. For each day:
   - Identify the date (starting from {start_date} and advancing day-by-day).
   - Set the `hotel` name (e.g. check-in on departure transit day, or check-out on final day).
   - Schedule flight transits on the correct days based on flight data.
   - Schedule morning, afternoon, and evening slots using the provided curated attraction spots.
   - Coordinate outdoor and indoor activities using the weather report recommendations (e.g., plan indoor museum activities on rainy days).
   - Propose local dining/meals for the day.
   - Write simple, brief, helpful daily notes.
3. Suggest a specific packing list based on the weather report.
4. Provide a short, summary paragraph of the trip's highlight vibes.

Provide the response in the requested structured format.""",
        input_variables=["source", "destination", "start_date", "trip_days", "budget_category", "budget", "weather_raw", "flights_raw", "hotels_raw", "attractions_raw", "budget_raw"]
    )

    chain = template | itinerary_llm
    result = chain.invoke({
        "source": source,
        "destination": destination,
        "start_date": str(start_date),
        "trip_days": trip_days,
        "budget_category": budget_category,
        "budget": budget,
        "weather_raw": json.dumps(weather, indent=2),
        "flights_raw": json.dumps(flights, indent=2),
        "hotels_raw": json.dumps(hotels, indent=2),
        "attractions_raw": json.dumps(attractions, indent=2),
        "budget_raw": json.dumps(budget_breakdown, indent=2)
    })

    return {
        "itinerary": dict(result),
        "status": "completed"
    }
