import httpx
from langchain_core.tools import tool

# WMO Weather interpretation codes (https://open-meteo.com/en/docs)
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@tool
def get_weather(city: str) -> str:
    """
    Get current weather conditions for any city.
    Input: city name (e.g. 'London', 'New York', 'Tokyo', 'Hyderabad').
    Returns: temperature, feels like, conditions, humidity, wind speed.
    Uses the free Open-Meteo API (no API key required).
    """
    try:
        # Step 1: Geocode the city name to lat/lon
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}

        geo_resp = httpx.get(geo_url, params=geo_params, timeout=10.0)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        results = geo_data.get("results")
        if not results:
            return f"City '{city}' not found. Please check the city name and try again."

        location = results[0]
        lat = location["latitude"]
        lon = location["longitude"]
        city_name = location.get("name", city)
        country = location.get("country", "")

        # Step 2: Fetch current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
            "timezone": "auto",
        }

        weather_resp = httpx.get(weather_url, params=weather_params, timeout=10.0)
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()

        current = weather_data.get("current", {})
        units = weather_data.get("current_units", {})

        temp = current.get("temperature_2m", "N/A")
        feels_like = current.get("apparent_temperature", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")
        weather_code = current.get("weather_code", 0)

        temp_unit = units.get("temperature_2m", "°C")
        wind_unit = units.get("wind_speed_10m", "km/h")

        description = WMO_CODES.get(weather_code, "Unknown conditions")

        return (
            f"Weather in {city_name}, {country}: {description}. "
            f"Temperature: {temp}{temp_unit} (feels like {feels_like}{temp_unit}). "
            f"Humidity: {humidity}%. Wind: {wind_speed} {wind_unit}."
        )
    except httpx.HTTPStatusError as e:
        return f"Weather API error: {str(e)}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
