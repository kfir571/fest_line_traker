# backend/collector_job/config.py
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_DSN = os.getenv("DATABASE_URL", "")
if not POSTGRES_DSN:
    raise ValueError("DATABASE_URL is not set")

FASTLANE_URL = os.getenv(
    "FASTLANE_URL",
    "https://fastlane.co.il/PageMethodsService.asmx/GetCurrentPrice",
)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY is not set")

WEATHER_LAT = float(os.getenv("WEATHER_LAT", "32.07256"))
WEATHER_LON = float(os.getenv("WEATHER_LON", "34.83687"))

AGG_INTERVAL_MINUTES = int(os.getenv("AGG_INTERVAL_MINUTES", "5"))


