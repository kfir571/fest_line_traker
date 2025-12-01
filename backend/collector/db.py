import psycopg2
from typing import Any, Mapping
from .config import POSTGRES_DSN

def get_connection():
    return psycopg2.connect(POSTGRES_DSN)

def insert_raw_sample(sample: Mapping[str, Any]) -> None:
    """
    sample:
    - measured_at: datetime
    - weekday: int
    - price: float | None
    - status: str ("ok" / "error")
    - error_message: str | None
    - is_holiday: bool
    - holiday_sector: str
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
                    holiday_sector
                )
                VALUES (
                    %(measured_at)s,
                    %(weekday)s,
                    %(price)s,
                    %(status)s,
                    %(error_message)s,
                    %(is_holiday)s,
                    %(holiday_sector)s
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

