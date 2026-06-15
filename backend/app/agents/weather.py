import httpx
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.graph.state import TripState
from app.core.config import settings

class WeatherPredictions(TypedDict):
    estimated_weather: str
    estimated_temp: str
    best_weather: str
    
def WeatherAgent(state: TripState):
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

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric"
    }

    weather_response = httpx.get(url, params=params)
    current_weather_obj = weather_response.json()
    current_weather = current_weather_obj["weather"][0]["description"].capitalize()
    current_temp = f"{current_weather_obj['main']['temp']}°C"
    
    llm = ChatOpenAI(model='gpt-4o-mini', api_key=settings.OPENAI_API_KEY)
    WeatherLLM = llm.with_structured_output(WeatherPredictions)

    template = PromptTemplate(
        template="""You are a weather analyst assistant. Predict the typical weather details for {destination_city}.

Trip Details:
- Destination: {destination_city}
- Start Date: {start_date}
- Duration: {trip_days} days

Tasks:
1. Estimate the typical weather conditions ("estimated_weather") at the destination around the trip start date ({start_date}).
2. Estimate the typical temperature range ("estimated_temp") in Celsius around the trip start date.
3. Identify the best time of year to visit this destination ("best_weather") with brief reasoning.

Provide the response in the requested structured format.""",
        input_variables=["destination_city", "start_date", "trip_days"]
    )

    chain = template | WeatherLLM
    result = chain.invoke({
        "destination_city": destination_city,
        "start_date": str(state["start_date"]),
        "trip_days": state["trip_days"]
    })

    return {
        "weather": {
            "current_weather": current_weather,
            "current_temp": current_temp,
            "estimated_weather": result["estimated_weather"],
            "estimated_temp": result["estimated_temp"],
            "best_weather": result["best_weather"]
        }
    }

