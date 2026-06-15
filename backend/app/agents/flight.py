from typing import TypedDict
import httpx
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.graph.state import TripState
from app.core.config import settings

class CityIata(TypedDict):
    source_iata: str
    destination_iata: str

class FlightLeg(TypedDict):
    flight_no: str
    airline: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    stops: int

class FlightOption(TypedDict):
    outbound: FlightLeg
    return_leg: FlightLeg
    total_price_inr: int

class FlightData(TypedDict):
    flight_options: list[FlightOption]
    travel_days_consumed: int
    potential_delays_warning: str

def FlightAgent(state: TripState):
    source_city = state["source_city"]
    destination_city = state["destination_city"]
    start_date = state["start_date"]
    trip_days = state["trip_days"]
    budget = state["budget"]
    
    trip_context = state.get("trip_context") or {}
    budget_category = trip_context.get("budget_category", "moderate")
    
    weather_state = state.get("weather") or {}
    weather_description = weather_state.get("current_weather", "Unknown")

    llm = ChatOpenAI(model='gpt-4o-mini', api_key=settings.OPENAI_API_KEY)
    iata_llm = llm.with_structured_output(CityIata)
    flight_llm = llm.with_structured_output(FlightData)

    iata_template = PromptTemplate(
        template="""Find the 3-letter IATA airport codes for the main airports in these cities.
Source City: {source_city}
Destination City: {destination_city}""",
        input_variables=["source_city", "destination_city"]
    )
    iata_chain = iata_template | iata_llm
    iata_res = iata_chain.invoke({
        "source_city": source_city,
        "destination_city": destination_city
    })
    
    source_iata = iata_res["source_iata"].upper()
    destination_iata = iata_res["destination_iata"].upper()

    api_flights = []
    try:
        url = "http://api.aviationstack.com/v1/flights"
        params = {
            "access_key": settings.AVIATIONSTACK_API_KEY,
            "dep_iata": source_iata,
            "arr_iata": destination_iata,
            "limit": 10
        }
        response = httpx.get(url, params=params)
        response.raise_for_status()
        api_data = response.json()
        
        if api_data.get("data"):
            for flight in api_data["data"]:
                flight_no = flight.get("flight", {}).get("iata") or flight.get("flight", {}).get("number")
                airline = flight.get("airline", {}).get("name")
                dep_time = flight.get("departure", {}).get("scheduled")
                arr_time = flight.get("arrival", {}).get("scheduled")
                if flight_no and airline:
                    if dep_time and "T" in dep_time:
                        dep_time = dep_time.split("T")[1][:5]
                    if arr_time and "T" in arr_time:
                        arr_time = arr_time.split("T")[1][:5]
                    api_flights.append({
                        "flight_no": flight_no,
                        "airline": airline,
                        "departure_time": dep_time or "00:00",
                        "arrival_time": arr_time or "00:00"
                    })
    except Exception as e:
        pass

    flight_template = PromptTemplate(
        template="""You are an expert travel logistics assistant. Propose 2-3 flight options for a round-trip.

**Trip Details:**
- Origin: {source_city} ({source_iata})
- Destination: {destination_city} ({destination_iata})
- Start Date: {start_date}
- Duration: {trip_days} days
- Budget Category: {budget_category} (Total Trip Budget: {budget} INR)
- Destination Current Weather: {weather_description}

**AviationStack Live Flight Schedules (Use these as templates for outbound/return airline details if available):**
{api_flights_raw}

**Tasks:**
1. Generate 2-3 realistic round-trip `flight_options`.
   - Each option must have an `outbound` leg and a `return_leg`.
   - Estimate realistic departure and arrival times, and typical duration (in minutes).
   - If the AviationStack live flight schedules list is empty, use your knowledge to recommend standard flights on this route.
   - Estimate a total round-trip price (`total_price_inr`) per person in INR that matches the "{budget_category}" budget class.
2. Determine `travel_days_consumed` (usually 1 day for outbound transit + 1 day for return transit = 2 days total, or 1 if very short domestic).
3. Evaluate a warning message (`potential_delays_warning`) based on destination weather: {weather_description}. If weather is stormy, rainy, or has bad conditions, warning should indicate potential delay risk. Otherwise "Low delay risk".

Provide the response in the requested structured format.""",
        input_variables=["source_city", "source_iata", "destination_city", "destination_iata", "start_date", "trip_days", "budget_category", "budget", "weather_description", "api_flights_raw"]
    )

    flight_chain = flight_template | flight_llm
    flight_result = flight_chain.invoke({
        "source_city": source_city,
        "source_iata": source_iata,
        "destination_city": destination_city,
        "destination_iata": destination_iata,
        "start_date": str(start_date),
        "trip_days": trip_days,
        "budget_category": budget_category,
        "budget": budget,
        "weather_description": weather_description,
        "api_flights_raw": json.dumps(api_flights, indent=2)
    })

    return {
        "flights": dict(flight_result)
    }

