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

# Mapping weekday index → Hebrew name
# Monday = 0 ... Sunday = 6
WEEKDAY_NAMES_HE = [
    "שני",     # 0
    "שלישי",   # 1
    "רביעי",   # 2
    "חמישי",   # 3
    "שישי",    # 4
    "שבת",     # 5
    "ראשון"    # 6
]

# Default constraints for recommendation endpoint
DEFAULT_FROM_HOUR = 6       # 06:00
DEFAULT_TO_HOUR = 22        # 22:00
DEFAULT_MAX_RESULTS = 3     # return top 3 slots by default

# Minimal sample_count required to trust a slot for recommendation
MIN_SAMPLE_COUNT_FOR_RECOMMENDATION = 1