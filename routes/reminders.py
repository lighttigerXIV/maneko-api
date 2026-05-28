from flask import Blueprint, g, request

from db import get_db
from responses import (
    bad_request_response,
    database_error_reponse,
    internal_error_response,
    invalid_field_response,
    missing_fields_reponse,
    not_found_response,
    ok_response,
    unauthorized_response,
)
from token_utils import authenticated
from validation_utils import (
    body_has_fields,
    get_body,
    get_put_field,
    is_valid_number,
    is_valid_string,
    is_valid_timestamp,
    is_valid_UUID,
)

reminders_blueprint = Blueprint("reminders_blueprint", __name__)


@reminders_blueprint.route("/reminders", methods=["PUT", "POST"])
@reminders_blueprint.route("/reminders/<string:id>", methods=["DELETE"])
@authenticated
def reminders(id=None):
    try:
        if request.method == "PUT":
            body = get_body()

            id = body["id"]

            if not id:
                return missing_fields_reponse("id")

            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT user_id, name, hour, minute, last_modified
                FROM reminder
                WHERE NOT deleted AND id = %s
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Reminder not found")

            if row["user_id"] != g.user_id:
                return unauthorized_response("Can't modify another user category")

            name = get_put_field(body, row, "name")
            hour = get_put_field(body, row, "hour")
            minute = get_put_field(body, row, "minute")
            last_modified = get_put_field(body, row, "last_modified")

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_number(hour):
                return invalid_field_response("hour")

            if not is_valid_number(minute):
                return invalid_field_response("minute")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            cursor.execute(
                """
                UPDATE reminder
                SET name=%s, hour=%s, minute=%s, last_modified=%s
                WHERE id = %s
                """,
                [name, hour, minute, last_modified, id],
            )

            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Reminder updated successfully"})

            return database_error_reponse()

        if request.method == "POST":
            body = get_body()

            fields = ["id", "name", "hour", "minute", "last_modified"]

            if not body_has_fields(body, fields):
                return missing_fields_reponse(fields)

            id = body["id"]
            name = body["name"]
            hour = body["hour"]
            minute = body["minute"]
            last_modified = body["last_modified"]

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_number(hour):
                return invalid_field_response("hour")

            if not is_valid_number(minute):
                return invalid_field_response("minute")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            user_id = g.user_id

            conn, cursor = get_db()

            cursor.execute(
                """
                INSERT INTO reminder (id, user_id, name, hour, minute, last_modified)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [id, user_id, name, hour, minute, last_modified],
            )

            conn.commit()
            conn.close()

            success = cursor.rowcount > 0

            cursor.close()

            if success:
                return ok_response({"message": "Category added successfully"})

            return database_error_reponse()

        if request.method == "DELETE":
            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT user_id
                FROM reminder
                WHERE id = %s AND NOT deleted
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Reminder not found")

            if g.user_id != row["user_id"]:
                return unauthorized_response("Can't delete reminder from another user")

            cursor.execute(
                """
                UPDATE reminder
                SET deleted = true
                WHERE id = %s
                """,
                [id],
            )

            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Reminder deleted successfully"})

            return database_error_reponse()

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
