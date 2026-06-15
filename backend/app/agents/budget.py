from typing import TypedDict
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.graph.state import TripState
from app.core.config import settings

class ExpenseItem(TypedDict):
    category: str
    cost_inr: int
    details: str

class BudgetBreakdown(TypedDict):
    itemized_expenses: list[ExpenseItem]
    total_estimated_cost_inr: int
    is_over_budget: bool
    remaining_balance_inr: int
    savings_suggestions: list[str]

def BudgetAgent(state: TripState):
    total_budget = state["budget"]
    adults = state["adults"]
    children = state["children"]
    destination_city = state["destination_city"]
    
    trip_context = state.get("trip_context") or {}
    budget_category = trip_context.get("budget_category", "moderate")
    
    flights_state = state.get("flights") or {}
    flight_options = flights_state.get("flight_options", [])
    
    hotels_state = state.get("hotels") or {}
    hotel_options = hotels_state.get("hotel_options", [])
    
    attractions_list = state.get("attractions") or []

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
    budget_llm = llm.with_structured_output(BudgetBreakdown)

    template = PromptTemplate(
        template="""You are an expert travel budget planner. Analyze and create a comprehensive budget breakdown for the trip.

**Trip Specifications:**
- Destination: {destination_city}
- Total User Budget: {total_budget} INR
- Budget Category: {budget_category}
- Travelers: {adults} Adults, {children} Children

**Flight Options Available (Choose/focus on the one that best matches the "{budget_category}" tier):**
{flight_options_raw}

**Hotel Options Available (Choose/focus on the one that best matches the "{budget_category}" tier):**
{hotel_options_raw}

**Attractions Selected (Sum the ticket prices for all items):**
{attractions_raw}

**Tasks:**
1. Select the flight and hotel options that match the "{budget_category}" tier.
2. Sum the cost of:
   - Flights (for {adults} adults + {children} children, using the selected option's `total_price_inr`).
   - Lodging (using the selected hotel option's `total_cost_inr`).
   - Attractions (sum of `entry_fee_inr` for all attractions multiplied by traveler count).
3. Estimate other necessary travel costs (e.g. food, local taxis/metro, visa, shopping, contingency fund) that match the "{budget_category}" class for {destination_city}.
4. Provide a structured list of `itemized_expenses` with details for each category.
5. Compute:
   - `total_estimated_cost_inr` (sum of all expenses).
   - `is_over_budget` (true if `total_estimated_cost_inr` exceeds `total_budget`).
   - `remaining_balance_inr` (`total_budget - total_estimated_cost_inr`).
6. If the plan exceeds the user's budget (`is_over_budget` is true), generate 2-3 specific `savings_suggestions` (e.g., "Recommend switching to the budget hotel to save X INR", "Reduce shopping or dining expense in Rome"). Otherwise, provide tips for contingency or local savings.

Provide the response in the requested structured format.""",
        input_variables=["destination_city", "total_budget", "budget_category", "adults", "children", "flight_options_raw", "hotel_options_raw", "attractions_raw"]
    )

    chain = template | budget_llm
    result = chain.invoke({
        "destination_city": destination_city,
        "total_budget": total_budget,
        "budget_category": budget_category,
        "adults": adults,
        "children": children,
        "flight_options_raw": json.dumps(flight_options, indent=2),
        "hotel_options_raw": json.dumps(hotel_options, indent=2),
        "attractions_raw": json.dumps(attractions_list, indent=2)
    })

    return {
        "budget_breakdown": dict(result)
    }

