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
from validation_utils import body_has_fields, get_body, get_put_field, is_valid_UUID

transfers_blueprint = Blueprint("transfers_blueprint", __name__)


@transfers_blueprint.route("/transfers", methods=["PUT", "POST"])
@authenticated
def transfer():
    try:
        if request.method == "PUT":
            body = get_body()

            id = body["id"]

            if not id:
                return missing_fields_reponse("id")

            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT user_id, t.from_account_id, t.to_account_id, t.last_modified
                FROM transfer t
                LEFT JOIN account a ON a.id = t.from_account_id
                WHERE t.id = %s
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Transfer not found")

            if row["user_id"] != g.user_id:
                return unauthorized_response("Can't modify another user transfer")

            from_account_id = get_put_field(body, row, "from_account_id")
            to_account_id = get_put_field(body, row, "to_account_id")
            last_modified = get_put_field(body, row, "last_modified")

            if not is_valid_UUID(from_account_id):
                return invalid_field_response("from_account_id")

            if not is_valid_UUID(to_account_id):
                return invalid_field_response("to_account_id")

            if from_account_id == to_account_id:
                return bad_request_response("The accounts can't be the same!")

            cursor.execute(
                """
                UPDATE transfer
                SET from_account_id = %s, to_account_id = %s, last_modified = %s
                WHERE id = %s
                """,
                [from_account_id, to_account_id, last_modified, id],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Transfer updated successfully"})

            return database_error_reponse()

        if request.method == "POST":
            body = get_body()

            fields = ["id", "from_account_id", "to_account_id", "last_modified"]

            if not body_has_fields(body, fields):
                return missing_fields_reponse(fields)

            id = body["id"]
            from_account_id = body["from_account_id"]
            to_account_id = body["to_account_id"]
            last_modified = body["last_modified"]

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_UUID(from_account_id):
                return invalid_field_response("from_account_id")

            if not is_valid_UUID(to_account_id):
                return invalid_field_response("to_account_id")

            if from_account_id == to_account_id:
                return bad_request_response("The accounts can't be the same!")

            conn, cursor = get_db()

            cursor.execute(
                """
                INSERT INTO transfer (id, from_account_id, to_account_id, last_modified)
                VALUES (%s, %s, %s, %s)
                """,
                [id, from_account_id, to_account_id, last_modified],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Transfer added successfully"})

            return database_error_reponse()

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
