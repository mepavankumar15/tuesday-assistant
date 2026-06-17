"""
LangChain @tool functions for OpenMeteo API.
Each function is a node-callable tool in the ReAct agent loop.
"""
from langchain_core.tools import tool
from config.settings import settings
from utils.logger import logger
import requests

def get_coordinates(city: str) -> dict:
    """Helper to get latitude and longitude for a city using OpenMeteo Geocoding API."""
    try:
        resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("results"):
            return {"error": f"Could not find coordinates for city: {city}"}
        result = data["results"][0]
        return {
            "lat": result["latitude"],
            "lon": result["longitude"],
            "name": result["name"],
            "country": result.get("country", "")
        }
    except Exception as e:
        logger.error(f"[WeatherTool] get_coordinates({city}): {e}")
        return {"error": str(e)}

def get_weather_description(code: int) -> str:
    """Convert WMO weather interpretation codes to readable descriptions."""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown weather")

@tool
def get_current_weather(city: str) -> dict:
    """
    Fetch real-time weather for a city. Returns temp (°C), humidity,
    wind speed, feels-like, and sky conditions.

    Args:
        city: City name e.g. 'Hyderabad', 'London', 'Tokyo'
    """
    geo = get_coordinates(city)
    if "error" in geo:
        return {"error": geo["error"], "city": city}

    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": geo["lat"],
                "longitude": geo["lon"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": "auto"
            },
            timeout=10,
        )
        resp.raise_for_status()
        d = resp.json()["current"]
        
        return {
            "city": geo["name"],
            "country": geo["country"],
            "temperature": d["temperature_2m"],
            "feels_like": d["apparent_temperature"],
            "humidity": d["relative_humidity_2m"],
            "wind_speed": d["wind_speed_10m"],
            "description": get_weather_description(d["weather_code"])
        }
    except Exception as e:
        logger.error(f"[WeatherTool] get_current_weather({city}): {e}")
        return {"error": str(e), "city": city}


@tool
def get_weather_forecast(city: str, days: int = 3) -> dict:
    """
    Fetch a multi-day weather forecast (max 14 days) for a city.

    Args:
        city: City name
        days: Number of forecast days
    """
    geo = get_coordinates(city)
    if "error" in geo:
        return {"error": geo["error"], "city": city}

    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": geo["lat"],
                "longitude": geo["lon"],
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean",
                "timezone": "auto",
                "forecast_days": min(max(days, 1), 14)
            },
            timeout=10,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]

        forecast = []
        for i in range(len(daily["time"])):
            # Handle potential None values for humidity
            hum_list = daily.get("relative_humidity_2m_mean", [])
            avg_hum = hum_list[i] if i < len(hum_list) and hum_list[i] is not None else "N/A"
            
            forecast.append({
                "date": daily["time"][i],
                "min_temp": daily["temperature_2m_min"][i],
                "max_temp": daily["temperature_2m_max"][i],
                "description": get_weather_description(daily["weather_code"][i]),
                "avg_humidity": avg_hum,
            })

        return {"city": geo["name"], "forecast": forecast}
    except Exception as e:
        logger.error(f"[WeatherTool] get_weather_forecast({city}): {e}")
        return {"error": str(e), "city": city}
