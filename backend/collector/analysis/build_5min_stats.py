import psycopg2
from backend.collector.config import POSTGRES_DSN, AGG_INTERVAL_MINUTES

REFRESH_STATS_SQL = """
BEGIN;

TRUNCATE TABLE price_5min_stats;

INSERT INTO price_5min_stats (
    weekday,
    hour,
    minute_bucket,
    is_holiday,
    holiday_sector,
    avg_price,
    min_price,
    max_price,
    sample_count,
    last_updated
)
SELECT
    rs.weekday,
    EXTRACT(HOUR FROM rs.measured_at) AS hour,
    FLOOR(EXTRACT(MINUTE FROM rs.measured_at) / 5) * 5 AS minute_bucket,
    rs.is_holiday,
    rs.holiday_sector,
    AVG(rs.price) AS avg_price,
    MIN(rs.price) AS min_price,
    MAX(rs.price) AS max_price,
    COUNT(*)      AS sample_count,
    NOW()         AS last_updated
FROM raw_samples AS rs
WHERE
    rs.status = 'ok'
    AND rs.price IS NOT NULL
GROUP BY
    rs.weekday,
    EXTRACT(HOUR FROM rs.measured_at),
    FLOOR(EXTRACT(MINUTE FROM rs.measured_at) / 5) * 5,
    rs.is_holiday,
    rs.holiday_sector;

COMMIT;
"""


def rebuild_5min_stats():
    print(f"[analytics] connecting to DB: {POSTGRES_DSN!r}")
    conn = psycopg2.connect(POSTGRES_DSN)
    try:
        with conn:
            with conn.cursor() as cur:
                print("[analytics] refreshing price_5min_stats ...")
                cur.execute(REFRESH_STATS_SQL)
                print("[analytics] done.")
    finally:
        conn.close()


if __name__ == "__main__":
    rebuild_5min_stats()
