# backend/collector_job/sampler.py
from datetime import datetime
from typing import Optional, Tuple
import json
import requests
import holidays

from .config import FASTLANE_URL


def get_current_price() -> Tuple[Optional[float], str, Optional[str]]:
    """
    retrun:
    (price, status, error_message)

    status: "ok" / "error"
    price: float or None
    error_message: messege or None
    """
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

    try:
        resp = requests.post(FASTLANE_URL, headers=headers, data="", timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        # תקלה ברשת / HTTP
        return None, "error", f"request_error: {e}"

    try:
        data = resp.json()
    except ValueError as e:
        return None, "error", f"json_decode_error: {e}; body_start={resp.text[:200]!r}"

    try:
        inner_json = json.loads(data["d"])
        raw_price = inner_json["Price"]
    except (KeyError, TypeError, ValueError) as e:
        return None, "error", f"parse_error: {e}; data_d={data.get('d')!r}"

    try:
        price = float(raw_price)
    except (TypeError, ValueError) as e:
        return None, "error", f"invalid_price: {raw_price!r}; error={e}"

    # אם הגענו לפה – הכול בסדר
    return price, "ok", None


def get_holiday_info(d: date) -> Tuple[bool, str]:
    """
    return:
    - is_holiday: bool
    - holiday_sector: "jewish" / "muslim" / "christian" / "none"
    """

    il_holidays = holidays.country_holidays("IL", years=[d.year])

    holiday_name = il_holidays.get(d)
    if not holiday_name:
        return False, "none"

    name_lower = holiday_name.lower()

    if any(k in name_lower for k in ["eid", "fitr", "adha", "ramadan"]):
        sector = "muslim"
    elif any(k in name_lower for k in ["christmas", "easter", "orthodox"]):
        sector = "christian"
    else:
        sector = "jewish"

    return True, sector


def build_sample_row() -> dict:
    """
    - measured_at
    - weekday
    - price
    - status
    - error_message
    - is_holiday
    - holiday_sector
    """
    now = datetime.now()
    weekday = now.weekday()

    price, status, error_message = get_current_price()
    is_holiday, holiday_sector = get_holiday_info(now.date())

    return {
        "measured_at": now,
        "weekday": weekday,
        "price": price,               
        "status": status,             
        "error_message": error_message,
        "is_holiday": is_holiday,
        "holiday_sector": holiday_sector,
    }
