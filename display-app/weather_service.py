import httpx
import os
from datetime import datetime, timedelta

API_KEY = os.getenv("WEATHER_API_KEY", "680f30fdbb69454ba2f121148251204")
LOCATION = "Ballynahinch"

_last_result = None
_last_updated = None

def get_weather():
    global _last_result, _last_updated

    # Use cached result if within 10 minutes
    if _last_result and _last_updated and datetime.now() - _last_updated < timedelta(minutes=10):
        return _last_result

    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={LOCATION}"
        r = httpx.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        result = {
            "temp_c": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "icon_url": "https:" + data["current"]["condition"]["icon"],
            "location": data["location"]["name"]
        }

        _last_result = result
        _last_updated = datetime.now()
        return result

    except Exception as e:
        print("⚠️ Failed to fetch weather:", e)
        return None