# backend/collector_job/sampler.py
from datetime import datetime
from typing import Optional
import json
import requests

from .config import FASTLANE_URL


def get_current_price() -> Optional[float]:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://fastlane.co.il",
        "Referer": "https://fastlane.co.il/",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
    }

    resp = requests.post(FASTLANE_URL, headers=headers, data="", timeout=10)

    try:
        data = resp.json()
    except requests.exceptions.JSONDecodeError:
        print("⚠ Not JSON, raw response:")
        print(resp.text)
        return None

    inner_json = json.loads(data["d"])
    raw_price = inner_json["Price"]

    try:
        return float(raw_price)
    except ValueError:
        print("⚠ Invalid price format:", raw_price)
        return None


def build_sample_row() -> Optional[dict]:
    price = get_current_price()
    if price is None:
        return None

    now = datetime.now()
    weekday = now.weekday()

    return {
        "measured_at": now,
        "weekday": weekday,
        "price": price,
        "is_holiday": False,
        "holiday_sector": "none",
    }
