import psycopg2
from backend.collector.config import POSTGRES_DSN

REFRESH_WEEKLY_SQL = """
BEGIN;

TRUNCATE TABLE weekly_stats;

INSERT INTO weekly_stats (
    weekday,
    hour,
    minute_bucket,
    is_holiday,
    holiday_sector,
    avg_price,
    min_price,
    max_price,
    sample_count,
    days_count,
    last_updated
)
SELECT
    ds.weekday,
    ds.hour,
    ds.minute_bucket,
    ds.is_holiday,
    ds.holiday_sector,
    SUM(ds.avg_price * ds.sample_count) / SUM(ds.sample_count) AS avg_price,
    MIN(ds.min_price) AS min_price,
    MAX(ds.max_price) AS max_price,
    SUM(ds.sample_count) AS sample_count,
    COUNT(DISTINCT ds.date) AS days_count,
    NOW() AS last_updated
FROM daily_stats AS ds
GROUP BY
    ds.weekday,
    ds.hour,
    ds.minute_bucket,
    ds.is_holiday,
    ds.holiday_sector;

COMMIT;
"""


def rebuild_weekly_stats():
    print(f"[analytics] connecting to DB: {POSTGRES_DSN!r}")
    conn = psycopg2.connect(POSTGRES_DSN)
    try:
        with conn:
            with conn.cursor() as cur:
                print("[analytics] refreshing weekly_stats ...")
                cur.execute(REFRESH_WEEKLY_SQL)
                print("[analytics] done.")
    finally:
        conn.close()


if __name__ == "__main__":
    rebuild_weekly_stats()
