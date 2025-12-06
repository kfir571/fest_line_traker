import requests
from typing import Any, Dict, Optional

from .config import WEATHER_API_KEY, WEATHER_LAT, WEATHER_LON


def get_current_weather(
    lat: float = WEATHER_LAT,
    lon: float = WEATHER_LON,
    api_key: str = WEATHER_API_KEY,
) -> Dict[str, Optional[Any]]:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric", 
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return {
            "temperature": None,
            "feels_like": None,
            "humidity": None,
            "wind_speed": None,
            "wind_direction": None,
            "clouds": None,
            "visibility": None,
            "weather_main": None,
            "weather_description": None,
            "is_raining": False,
            "rain_intensity": None,
        }

    main = data.get("main", {})
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})
    weather_list = data.get("weather", [])
    weather_obj = weather_list[0] if weather_list else {}

    rain = data.get("rain", {}) or {}
    rain_intensity = rain.get("1h") or rain.get("3h")

    return {
        "temperature": main.get("temp"),
        "humidity": main.get("humidity"),
        "wind_speed": wind.get("speed"),
        "wind_direction": wind.get("deg"),
        "clouds": clouds.get("all"),
        "visibility": data.get("visibility"),
        "weather_description": weather_obj.get("description"),
        "rain_intensity": rain_intensity,
    }
 
