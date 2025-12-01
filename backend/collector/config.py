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
