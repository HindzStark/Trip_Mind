from langgraph.graph import StateGraph, START, END
from app.graph.state import TripState
from app.agents.planner import PlannerAgent
from app.agents.weather import WeatherAgent
from app.agents.flight import FlightAgent
from app.agents.hotel import HotelAgent
from app.agents.attraction import AttractionAgent
from app.agents.budget import BudgetAgent
from app.agents.itinerary import ItineraryAgent

def route_planner(state: TripState):
    if state["status"] == "failed":
        return END
    return "weather"

builder = StateGraph(TripState)

builder.add_node("planner", PlannerAgent)
builder.add_node("weather", WeatherAgent)
builder.add_node("flight", FlightAgent)
builder.add_node("hotel", HotelAgent)
builder.add_node("attraction", AttractionAgent)
builder.add_node("budget", BudgetAgent)
builder.add_node("itinerary", ItineraryAgent)

builder.add_edge(START, "planner")
builder.add_conditional_edges("planner", route_planner, {END: END, "weather": "weather"})
builder.add_edge("weather", "flight")
builder.add_edge("flight", "hotel")
builder.add_edge("hotel", "attraction")
builder.add_edge("attraction", "budget")
builder.add_edge("budget", "itinerary")
builder.add_edge("itinerary", END)

app_graph = builder.compile()

