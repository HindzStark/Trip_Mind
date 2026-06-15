from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.graph.state import TripState
from app.core.config import settings

class Planner(TypedDict):
    source_city_normalized: str
    destination_city_normalized: str
    destination_country: str
    trip_days: int
    interests_tags: list[str]
    budget_category: Literal["low", "moderate", "comfortable", "luxury"]
    travel_days_estimate: int
    realestic_budget: bool
    realestic_place: bool
    Flag_issue: bool
    issues: list[str]

def PlannerAgent(state: TripState):
    template = PromptTemplate(
        template="""You are a travel planning assistant. Validate and normalize this trip request.

**Trip Request:**
- From: {source_city}
- To: {destination_city}
- Duration: {trip_days} days
- Travel Included: {travel_included}
- Budget: {budget} INR
- Adults: {adults}, Children: {children}
- Interests: {interests}

**Tasks:**
1. Normalize city names (e.g. "blr" → "Bengaluru", "NYC" → "New York City")
2. Validate if the destination is a real, visitable place (set "realestic_place" to true if real and visitable, false otherwise)
3. Categorize interests into tags: culture, adventure, food, nature, shopping, nightlife, history, beaches, temples, wildlife
4. Estimate if the budget is realistic for this destination and category (set "realestic_budget" to true if feasible, false otherwise) and assign a budget category (low / moderate / comfortable / luxury)
5. Estimate travel days (transit time) needed
6. Flag any issues (e.g. 0 adults, negative budget, destination not real, budget extremely low for travel duration/destination) by setting "Flag_issue" to true and listing specific problems in "issues".

**Respond ONLY in this JSON format:**
{{
    "source_city_normalized": "Full city name",
    "destination_city_normalized": "Full city name",
    "destination_country": "Country name",
    "trip_days": {trip_days},
    "interests_tags": ["tag1", "tag2"],
    "budget_category": "low / moderate / comfortable / luxury",
    "travel_days_estimate": 1,
    "realestic_budget": true,
    "realestic_place": true,
    "Flag_issue": false,
    "issues": []
}}""",
        input_variables=[
            "source_city",
            "destination_city",
            "trip_days",
            "travel_included",
            "budget",
            "adults",
            "children",
            "interests",
        ],
    )

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
    PlannerLLM = llm.with_structured_output(Planner)

    source_city = state['source_city']
    destination_city = state['destination_city']
    trip_days = state['trip_days']
    travel_included = state['travel_included']
    budget = state['budget']
    adults = state['adults']
    children = state['children']
    interests = state['interests']

    chain = template | PlannerLLM
    
    result = chain.invoke({
        "source_city": source_city,
        "destination_city": destination_city,
        "trip_days": trip_days,
        "travel_included": travel_included,
        "budget": budget,
        "adults": adults,
        "children": children,
        "interests": interests or ""
    })
    
    if result.get("Flag_issue"):
        return {
            "status": "failed",
            "errors": result.get("issues", [])
        }
        
    return {
        "trip_context": dict(result),
        "status": "processing"
    }