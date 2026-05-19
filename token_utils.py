from datetime import datetime, timezone
from functools import wraps

from flask import g, request

from db import get_db
from responses import unauthorized_response


def authenticated(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = get_token()

        conn, cursor = get_db()

        cursor.execute(
            """
SELECT user_id, expiration_date
FROM token
WHERE token = %s
        """,
            [token],
        )

        row = cursor.fetchone()

        conn.close()
        cursor.close()

        if not row:
            return unauthorized_response("The token is invalid")

        user_id, expiration_millis = row["user_id"], row["expiration_date"]

        now_millis = (datetime.now(timezone.utc)).timestamp() * 1000

        if expiration_millis - now_millis <= 0:
            return unauthorized_response("The token has expired")

        g.user_id = user_id
        g.token_expiration_date = expiration_millis
        g.token = token

        return f(*args, **kwargs)

    return decorator


def get_token():
    header = request.headers.get("Authorization")

    if not header:
        return None

    header_blocks = header.split(" ")

    if len(header_blocks) != 2:
        return None

    if header_blocks[0] != "Bearer":
        return None

    return header_blocks[1]
