import os

import psycopg2
from psycopg2.extras import RealDictCursor  # Return rows as dictionary so it has column names


def get_db():
    host = os.environ.get("DB_HOST")
    name = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")

    conn_str = f"host={host} dbname={name} user={user} password={password}"
    conn = psycopg2.connect(conn_str)

    return conn, conn.cursor(cursor_factory=RealDictCursor)
