from datetime import datetime, timezone

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
    is_valid_number,
    is_valid_string,
    is_valid_timestamp,
    is_valid_UUID,
)

accounts_blueprint = Blueprint("accounts_blueprint", __name__)


@accounts_blueprint.route("/accounts", methods=["POST", "PUT"])
@accounts_blueprint.route("/accounts/<string:id>", methods=["DELETE"])
@authenticated
def accounts(id=None):
    try:
        if request.method == "PUT":
            body = get_body()

            id = body["id"]

            if not id:
                return missing_fields_reponse("id")

            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT a.user_id, a.name, a.icon, a.balance, a.last_modified
                FROM account a
                LEFT JOIN "user" u ON u.id = a.user_id
                WHERE a.id = %s AND NOT a.deleted
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Account not found")

            if row["user_id"] != g.user_id:
                return unauthorized_response("Can't modify another user account")

            name = body["name"] if "name" in body else row["name"]
            icon = body["icon"] if "icon" in body else row["icon"]
            balance = body["balance"] if "balance" in body else row["balance"]
            last_modified = (
                body["last_modified"] if "last_modified" in body else (datetime.now(timezone.utc).timestamp() * 1000)
            )

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_string(icon):
                return invalid_field_response("icon")

            if not is_valid_number(balance):
                return invalid_field_response("balance")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            cursor.execute(
                """
                UPDATE account
                SET name=%s, icon=%s, balance=%s, last_modified=%s
                WHERE id = %s
                """,
                [name, icon, balance, last_modified, id],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Account updated successfully"})
            else:
                return database_error_reponse()

        if request.method == "POST":
            body = get_body()

            fields = ["id", "name", "icon", "balance", "last_modified"]

            if not body_has_fields(body, fields):
                return missing_fields_reponse(fields)

            id = body["id"]
            name = body["name"]
            icon = body["icon"]
            balance = body["balance"]
            last_modified = body["last_modified"]

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_string(icon):
                return invalid_field_response("icon")

            if not is_valid_number(balance):
                return invalid_field_response("balance")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            user_id = g.user_id

            conn, cursor = get_db()

            cursor.execute(
                """
                INSERT INTO account (id, user_id, name, icon, balance, last_modified)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [id, user_id, name, icon, balance, last_modified],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Account addedd successfully"})
            else:
                return database_error_reponse()

        if request.method == "DELETE":
            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT user_id
                FROM account
                WHERE id = %s AND NOT deleted
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Account not found")

            if g.user_id != row["user_id"]:
                return unauthorized_response("Can't delete account from another user")

            cursor.execute(
                """
                UPDATE account
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
                return ok_response({"message": "Account deleted successfully"})
            else:
                return database_error_reponse()

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
