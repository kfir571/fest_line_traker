import psycopg2
from typing import Any, Mapping
from .config import POSTGRES_DSN

def get_connection():
    return psycopg2.connect(POSTGRES_DSN)
    
def insert_raw_sample(sample: Mapping[str, Any]) -> None:
    """
    sample contains:
    Base fields:
        - measured_at: datetime
        - weekday: int
        - price: float | None
        - status: str ("ok" / "error")
        - error_message: str | None
        - is_holiday: bool
        - holiday_sector: str

    Weather fields:
        - temperature: float | None
        - humidity: int | None
        - wind_speed: float | None
        - wind_direction: int | None
        - clouds: int | None
        - visibility: int | None
        - weather_description: str | None
        - rain_intensity: float | None
    """
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw_samples (
                    measured_at,
                    weekday,
                    price,
                    status,
                    error_message,
                    is_holiday,
                    holiday_sector,

                    temperature,
                    humidity,
                    wind_speed,
                    wind_direction,
                    clouds,
                    visibility,
                    weather_description,
                    rain_intensity
                )
                VALUES (
                    %(measured_at)s,
                    %(weekday)s,
                    %(price)s,
                    %(status)s,
                    %(error_message)s,
                    %(is_holiday)s,
                    %(holiday_sector)s,

                    %(temperature)s,
                    %(humidity)s,
                    %(wind_speed)s,
                    %(wind_direction)s,
                    %(clouds)s,
                    %(visibility)s,
                    %(weather_description)s,
                    %(rain_intensity)s
                )
                """,
                sample,
            )
    finally:
        conn.close()


def get_all_raw_samples() -> list[tuple]:
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM raw_samples ORDER BY measured_at DESC LIMIT 50")
            return cur.fetchall()
    finally:
        conn.close()

def clear_old_raw_samples():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw_samples;")
        conn.commit()
        print("✅ All rows in raw_samples have been deleted.")
    finally:
        conn.close()



