import psycopg2
from backend.collector.config import POSTGRES_DSN

REFRESH_DAILY_SQL = """
BEGIN;

TRUNCATE TABLE daily_stats;

INSERT INTO daily_stats (
    date,
    weekday,
    hour,
    minute_bucket,
    avg_price,
    min_price,
    max_price,
    sample_count,
    is_holiday,
    holiday_sector,
    last_updated
)
SELECT
    DATE(rs.measured_at) AS date,
    rs.weekday,
    EXTRACT(HOUR FROM rs.measured_at) AS hour,
    CASE
        WHEN EXTRACT(HOUR FROM rs.measured_at) BETWEEN 6 AND 10
            THEN FLOOR(EXTRACT(MINUTE FROM rs.measured_at) / 30) * 30
        ELSE 0
    END AS minute_bucket,
    AVG(rs.price) AS avg_price,
    MIN(rs.price) AS min_price,
    MAX(rs.price) AS max_price,
    COUNT(*)      AS sample_count,
    BOOL_OR(rs.is_holiday) AS is_holiday,
    MODE() WITHIN GROUP (ORDER BY rs.holiday_sector) AS holiday_sector,
    NOW()         AS last_updated
FROM raw_samples AS rs
WHERE
    rs.status = 'ok'
    AND rs.price IS NOT NULL
GROUP BY
    DATE(rs.measured_at),
    rs.weekday,
    EXTRACT(HOUR FROM rs.measured_at),
    CASE
        WHEN EXTRACT(HOUR FROM rs.measured_at) BETWEEN 6 AND 10
            THEN FLOOR(EXTRACT(MINUTE FROM rs.measured_at) / 30) * 30
        ELSE 0
    END;

COMMIT;
"""


def rebuild_daily_stats():
    print(f"[analytics] connecting to DB: {POSTGRES_DSN!r}")
    conn = psycopg2.connect(POSTGRES_DSN)
    try:
        with conn:
            with conn.cursor() as cur:
                print("[analytics] refreshing daily_stats ...")
                cur.execute(REFRESH_DAILY_SQL)
                print("[analytics] done.")
    finally:
        conn.close()


if __name__ == "__main__":
    rebuild_daily_stats()
