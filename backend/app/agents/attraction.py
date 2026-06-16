from typing import TypedDict
import httpx
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.graph.state import TripState
from app.core.config import settings

class AttractionSpot(TypedDict):
    name: str
    description: str
    category: str
    estimated_duration_mins: int
    entry_fee_inr: int
    child_friendly: bool
    address: str

class AttractionList(TypedDict):
    attractions: list[AttractionSpot]

def AttractionAgent(state: TripState):
    destination_city = state["destination_city"]
    interests = state.get("interests", "")
    children = state.get("children", 0)

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
    attraction_llm = llm.with_structured_output(AttractionList)

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

    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "tourism,entertainment,leisure.park",
        "filter": f"circle:{lon},{lat},20000",
        "bias": f"proximity:{lon},{lat}",
        "limit": 30,
        "apiKey": settings.GEOAPIFY_API_KEY
    }

    response = httpx.get(url, params=params)
    response.raise_for_status()
    places_data = response.json()

    places_pool = []
    for feature in places_data.get("features", []):
        properties = feature.get("properties", {})
        name = properties.get("name")
        
        if not name:
            continue
            
        places_pool.append({
            "name": name,
            "address": properties.get("formatted"),
            "lat": properties.get("lat"),
            "lon": properties.get("lon"),
            "categories": properties.get("categories", [])
        })

    template = PromptTemplate(
        template="""You are a travel planning assistant. Curate a list of 5-8 top sightseeing spots and activities matching the traveler's profile.

**Trip Details:**
- Destination: {destination_city}
- Stated Interests: {interests}
- Children: {children}

**Geoapify Live Attraction Recommendations (Real places operating at the destination):**
{places_pool_raw}

**Tasks:**
1. From the Geoapify live attraction list, select the 5-8 best matches that align with the traveler's stated interests ({interests}). If the list is empty, use your knowledge to recommend real, popular spots in {destination_city}.
2. For each selected spot:
   - Match the name and address from the live list.
   - Categorize the spot (e.g., "culture", "nature", "adventure", "history", "shopping").
   - Estimate typical duration of a visit in minutes (e.g., 120 minutes).
   - Estimate the typical entry fee in INR per person (use 0 for free attractions).
   - Determine if the spot is child-friendly (this is highly important if children traveling is greater than 0, which is currently {children}).
   - Provide a brief description of what the spot is and why it matches their interest.

Provide the response in the requested structured format.""",
        input_variables=["destination_city", "interests", "children", "places_pool_raw"]
    )

    chain = template | attraction_llm
    result = chain.invoke({
        "destination_city": destination_city,
        "interests": interests or "general sightseeing",
        "children": children,
        "places_pool_raw": json.dumps(places_pool, indent=2)
    })

    return {
        "attractions": result["attractions"]
    }

