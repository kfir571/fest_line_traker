import psycopg2
from collector.config import POSTGRES_DSN


def get_db_connection():
    conn = psycopg2.connect(POSTGRES_DSN)
    return conn
