from .db import get_connection

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw_samples (
    id              SERIAL PRIMARY KEY,
    measured_at     TIMESTAMP NOT NULL,
    weekday         SMALLINT  NOT NULL,
    price           NUMERIC(6, 2) NOT NULL,
    is_holiday      BOOLEAN NOT NULL DEFAULT FALSE,
    holiday_sector  VARCHAR(32) NOT NULL DEFAULT 'none'
);
"""

def main() -> None:
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
        print("Table raw_samples created (or already exists).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
