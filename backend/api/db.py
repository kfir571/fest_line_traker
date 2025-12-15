import psycopg2


def get_db_connection():
    POSTGRES_DSN = os.getenv("DATABASE_URL", "")
    if not POSTGRES_DSN:
        raise ValueError("DATABASE_URL is not set")

    conn = psycopg2.connect(POSTGRES_DSN)
    return conn
