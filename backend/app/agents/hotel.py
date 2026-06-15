from typing import TypedDict, Literal
import httpx
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.graph.state import TripState
from app.core.config import settings

class Hotel(TypedDict):
    hotel_name: str
    tier: Literal["budget", "mid-range", "premium"]
    neighborhood: str
    nightly_rate_inr: int
    rooms_needed: int
    total_nights: int
    total_cost_inr: int
    description: str

class HotelData(TypedDict):
    hotel_options: list[Hotel]
    check_in_day: int
    check_out_day: int

def HotelAgent(state: TripState):
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
    hotel_llm = llm.with_structured_output(HotelData)

    destination_city = state['destination_city']

    geo_url = "https://api.geoapify.com/v1/geocode/search"
    geo_params = {
        "text": destination_city,
        "apiKey": settings.GEOAPIFY_API_KEY
    }
    geo_response = httpx.get(geo_url, params=geo_params)
    geo_response.raise_for_status()
    geo_data = geo_response.json()
    
    if not geo_data.get("features"):
        raise ValueError(f"Could not find coordinates for city: {destination_city}")
        
    first_feature = geo_data["features"][0]
    lat = first_feature["properties"]["lat"]
    lon = first_feature["properties"]["lon"]

    url = "https://api.geoapify.v2/places"
    params = {
        "categories": "accommodation.hotel,accommodation.hostel,accommodation.guest_house",
        "filter": f"circle:{lon},{lat},20000",  
        "bias": f"proximity:{lon},{lat}",        
        "limit": 20,
        "apiKey": settings.GEOAPIFY_API_KEY
    }

    response = httpx.get(url, params=params)
    response.raise_for_status()
    places_data = response.json()

    hotel_list = []

    for feature in places_data.get("features", []):
        properties = feature.get("properties", {})
        name = properties.get("name")
        
        if not name:
            continue
            
        hotel_info = {
            "name": name,
            "address": properties.get("formatted"),
            "lat": properties.get("lat"),
            "lon": properties.get("lon"),
            "categories": properties.get("categories", [])
        }
        hotel_list.append(hotel_info)
    
    flights_state = state.get("flights") or {}
    travel_days_consumed = flights_state.get("travel_days_consumed", 2)
    
    trip_days = state["trip_days"]
    adults = state["adults"]
    children = state["children"]
    budget = state["budget"]
    
    trip_context = state.get("trip_context") or {}
    budget_category = trip_context.get("budget_category", "moderate")

    template = PromptTemplate(
        template="""You are an expert travel accommodation assistant. Propose 3 lodging recommendations (Budget, Mid-range, Premium) for this trip.

**Trip Details:**
- Destination: {destination_city}
- Total Trip Duration: {trip_days} days
- Flight Transit Days: {travel_days_consumed} days
- Travelers: {adults} Adults, {children} Children
- Budget Category: {budget_category} (Total Trip Budget: {budget} INR)

**Geoapify Live Hotel Recommendations (Real hotels operating at the destination):**
{hotel_list_raw}

**Tasks:**
1. Suggest exactly 3 options in `hotel_options` (one matching "budget", one matching "mid-range", and one matching "premium").
   - Match the name (`hotel_name`) and neighborhood/address (`neighborhood`) from the Geoapify live hotel list. If the list is empty, use your knowledge to recommend real, popular hotels.
   - Determine `rooms_needed` based on the number of travelers ({adults} adults + {children} children). A typical room fits up to 2 adults + 1 child.
   - Calculate the stay duration in nights: typically `total_nights = trip_days - travel_days_consumed` (or at least 1 night if it's a short trip).
   - Estimate a realistic `nightly_rate_inr` per room in INR for each tier at this destination (e.g., Zurich is very expensive, Delhi is moderate).
   - Calculate the total lodging cost: `total_cost_inr = nightly_rate_inr * rooms_needed * total_nights`.
   - Provide a brief description of why this option is suitable.
2. Determine the `check_in_day` of the trip (usually Day 1, or Day 2 if overnight flight transit is consumed).
3. Determine the `check_out_day` of the trip.

Provide the response in the requested structured format.""",
        input_variables=["destination_city", "trip_days", "travel_days_consumed", "adults", "children", "budget_category", "budget", "hotel_list_raw"]
    )

    chain = template | hotel_llm
    result = chain.invoke({
        "destination_city": destination_city,
        "trip_days": trip_days,
        "travel_days_consumed": travel_days_consumed,
        "adults": adults,
        "children": children,
        "budget_category": budget_category,
        "budget": budget,
        "hotel_list_raw": json.dumps(hotel_list, indent=2)
    })

    return {
        "hotels": dict(result)
    }

