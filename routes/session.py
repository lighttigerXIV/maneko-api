import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from flask import Blueprint, g

from db import get_db
from responses import (
    internal_error_response,
    invalid_field_response,
    missing_fields_reponse,
    ok_response,
    unauthorized_response,
)
from token_utils import authenticated
from validation_utils import body_has_fields, get_body, is_valid_email, is_valid_string

session_blueprint = Blueprint("session_blueprint", __name__)


def generate_token_and_date():
    token = secrets.token_urlsafe(32)
    expiration_epoch_seconds = (datetime.now(timezone.utc) + timedelta(weeks=2)).timestamp()
    expiration_millis = int(expiration_epoch_seconds * 1000)

    return token, expiration_millis


@session_blueprint.route("/login", methods=["POST"])
def login():
    try:
        body = get_body()

        fields = ["email", "password"]

        if not body_has_fields(body, fields):
            return missing_fields_reponse(fields)

        email = body["email"]
        raw_password = body["password"]

        if not is_valid_email(email):
            return invalid_field_response("email")

        if not is_valid_string(raw_password):
            return invalid_field_response("password")

        conn, cursor = get_db()

        cursor.execute(
            """
SELECT id, password
FROM "user"
WHERE email = %s
        """,
            [email],
        )

        row = cursor.fetchone()

        if not row:
            return unauthorized_response("Invalid email or password")

        password_bytes = raw_password.encode("utf-8")
        hash_bytes = row["password"].encode("utf-8")
        correct_password = bcrypt.checkpw(password_bytes, hash_bytes)

        if not correct_password:
            return unauthorized_response("Invalid email or password")

        user_id = row["id"]

        token, expiration_millis = generate_token_and_date()

        cursor.execute(
            """
INSERT INTO token (user_id, token, expiration_date)
VALUES (%s, %s, %s)
        """,
            [user_id, token, expiration_millis],
        )

        conn.commit()
        cursor.close()

        return ok_response({"token": token})

    except Exception as e:
        return internal_error_response(e)


@session_blueprint.route("/token-login", methods=["POST"])
@authenticated
def token_login():
    try:
        token, new_expiration_millis = generate_token_and_date()

        conn, cursor = get_db()

        cursor.execute(
            """
UPDATE token
SET token = %s, expiration_date = %s
WHERE token = %s
        """,
            [token, new_expiration_millis, g.token],
        )

        conn.commit()
        conn.close()
        cursor.close()

        return ok_response({"token": token})
    except Exception as e:
        return internal_error_response(e)


@session_blueprint.route("/logout", methods=["POST"])
@authenticated
def logout():
    token = g.token

    conn, cursor = get_db()

    cursor.execute(
        """
DELETE FROM token
WHERE token = %s
    """,
        [token],
    )

    conn.commit()
    conn.close()
    cursor.close()

    return ok_response({"message": "Session token was cleared"})
