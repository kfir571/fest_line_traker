import psycopg2
from typing import Any, Mapping
from .config import POSTGRES_DSN

def get_connection():
    return psycopg2.connect(POSTGRES_DSN)

def insert_raw_sample(sample: Mapping[str, Any]) -> None:
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw_samples (
                    measured_at, weekday, price, is_holiday, holiday_sector
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    sample["measured_at"],
                    sample["weekday"],
                    sample["price"],
                    sample["is_holiday"],
                    sample["holiday_sector"],
                ),
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

