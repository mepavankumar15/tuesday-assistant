"""Weather tool — wraps Open-Meteo API for free weather data without an API key."""
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential


class WeatherInput(BaseModel):
    city: str = Field(..., description="City name, e.g. 'Hyderabad' or 'London, UK'")
    units: str = Field(default="metric", description="'metric' (Celsius) or 'imperial' (Fahrenheit)")


class WeatherTool(BaseTool):
    name: str = "WeatherTool"
    description: str = (
        "Fetches real-time weather data and 3-day forecast for a given city. "
        "Returns temperature, humidity, wind speed, condition, and forecast."
    )
    args_schema: type[BaseModel] = WeatherInput

    def _get_weather_description(self, code: int) -> str:
        """Map Open-Meteo WMO weather codes to human readable strings."""
        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
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
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return descriptions.get(code, "Unknown condition")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
    def _run(self, city: str, units: str = "metric") -> dict:
        # Step 1: Geocoding
        geo_resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        
        if not geo_data.get("results"):
            raise ValueError(f"Could not find coordinates for city: {city}")
            
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        resolved_city = location["name"]
        country = location.get("country", "")

        # Step 2: Get Weather
        # Open-Meteo uses specific string values for units
        temp_unit = "celsius" if units == "metric" else "fahrenheit"
        wind_unit = "kmh" if units == "metric" else "mph"
        
        weather_resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "temperature_unit": temp_unit,
                "wind_speed_unit": wind_unit,
                "timezone": "auto"
            },
            timeout=10,
        )
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()

        unit_symbol = "°C" if units == "metric" else "°F"

        current = weather_data["current"]
        temp = current["temperature_2m"]
        feels = current["apparent_temperature"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        condition = self._get_weather_description(current["weather_code"])

        daily = weather_data["daily"]
        forecast_3day = []
        # Take the next 3 days (index 0 is today, 1-3 are next 3 days)
        # Open-Meteo usually returns 7 days of daily data
        for i in range(min(3, len(daily["time"]))):
            forecast_3day.append({
                "date": daily["time"][i],
                "temp_max": f"{daily['temperature_2m_max'][i]:.1f}{unit_symbol}",
                "temp_min": f"{daily['temperature_2m_min'][i]:.1f}{unit_symbol}",
                "condition": self._get_weather_description(daily["weather_code"][i]),
            })

        # Helpful tip
        tip = "Carry an umbrella today!" if "rain" in condition.lower() or "drizzle" in condition.lower() else \
              "Great day to be outside!" if (units == "metric" and temp > 25) or (units != "metric" and temp > 77) else "Layer up, it's chilly!"

        return {
            "city": resolved_city,
            "country": country,
            "temp": f"{temp:.1f}{unit_symbol}",
            "feels_like": f"{feels:.1f}{unit_symbol}",
            "humidity": f"{humidity}%",
            "wind": f"{wind} {wind_unit}",
            "condition": condition,
            "forecast_3day": forecast_3day,
            "tip": tip,
        }
