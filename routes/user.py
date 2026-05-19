import bcrypt
from flask import Blueprint, request

from db import get_db
from responses import (
    bad_request_response,
    conflict_response,
    database_error_reponse,
    internal_error_response,
    invalid_field_response,
    missing_fields_reponse,
    ok_response,
)
from validation_utils import body_has_fields, get_body, is_valid_email, is_valid_string

user_blueprint = Blueprint("user_blueprint", __name__)


@user_blueprint.route("/user", methods=["GET", "POST"])
def user():
    try:
        if request.method == "GET":
            pass

        if request.method == "POST":
            body = get_body()

            required_fields = ["name", "email", "password"]

            if not body_has_fields(body, required_fields):
                return missing_fields_reponse(required_fields)

            name = body["name"]
            email = body["email"]
            raw_password = body["password"]

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_email(email):
                return invalid_field_response("email")

            if not is_valid_string(raw_password):
                return invalid_field_response("password")

            conn, cursor = get_db()

            cursor.execute(
                """
SELECT NOT EXISTS (
	SELECT 1
	FROM "user"
	WHERE email = %s
) as "can_register"
            """,
                [email],
            )

            row = cursor.fetchone()

            if not row:
                return database_error_reponse()

            can_register = row["can_register"]

            if not can_register:
                return conflict_response(f"There's already a user registered with the email: [{email}]")

            password_bytes = raw_password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed_bytes = bcrypt.hashpw(password_bytes, salt)
            encrypted_password = hashed_bytes.decode("utf-8")

            cursor.execute(
                """
INSERT INTO "user" (email, name, password)
VALUES (%s, %s, %s)
            """,
                [email, name, encrypted_password],
            )

            conn.commit()
            conn.close()
            cursor.close()

            return ok_response({"message": "Successfully registred"})

        return bad_request_response()

    except Exception as e:
        return internal_error_response(e)
