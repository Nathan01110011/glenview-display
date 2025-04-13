"""Route for the weather widget to fetch realtime data"""

from datetime import datetime, timedelta, timezone
import os

from fastapi import APIRouter
import httpx

router = APIRouter()

API_KEY = os.getenv("WEATHER_API_KEY")
LOCATION = "Ballynahinch"


class WeatherCache:
    def __init__(self):
        self._last_result = None
        self._last_updated = None

    def get_weather(self):
        if (
            self._last_result
            and self._last_updated
            and datetime.now(timezone.utc) - self._last_updated < timedelta(minutes=10)
        ):
            return self._last_result

        try:
            url = (
                f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={LOCATION}"
            )
            r = httpx.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()

            result = {
                "temp_c": data["current"]["temp_c"],
                "condition": data["current"]["condition"]["text"],
                "icon_url": "https:" + data["current"]["condition"]["icon"],
                "location": data["location"]["name"],
            }

            self._last_result = result
            self._last_updated = datetime.now(timezone.utc)
            return result

        except httpx.HTTPError as e:
            print("⚠️ Failed to fetch weather:", e)
            return {"error": "Unable to fetch weather"}


weather_cache = WeatherCache()


@router.get("/weather")
def get_weather():
    return weather_cache.get_weather()
