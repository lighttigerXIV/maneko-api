import os

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db():
    if os.environ.get("USE_LOCAL_DB") == "True":
        conn = psycopg2.connect(dbname=os.environ.get("LOCAL_DB_NAME"), user=os.environ.get("LOCAL_DB_USER"))

    else:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
        )

    return conn, conn.cursor(
        cursor_factory=RealDictCursor  # Return rows as dictionary so it has column names
    )
