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
from validation_utils import body_has_fields, get_body, is_valid_number, is_valid_timestamp, is_valid_UUID

movements_blueprint = Blueprint("movements_blueprint", __name__)


@movements_blueprint.route("/movements", methods=["PUT", "POST"])
@movements_blueprint.route("/movements/<string:id>", methods=["DELETE"])
@authenticated
def movements(id=None):
    try:
        if request.method == "PUT":
            pass

        if request.method == "POST":
            body = get_body()

            fields = [
                "id",
                "user_id",
                "amount",
                "movement_date",
                "description",
                "expense_id",
                "income_id",
                "transfer_id",
                "last_modified",
            ]

            if not body_has_fields(body, fields):
                return missing_fields_reponse(fields)

            id = body["id"]
            user_id = body["user_id"]
            amount = body["amount"]
            movement_date = body["movement_date"]
            description = body["description"]
            expense_id = body["expense_id"]
            income_id = body["income_id"]
            transfer_id = body["transfer_id"]
            last_modified = body["last_modified"]

            if expense_id is None and income_id is None and transfer_id is None:
                return bad_request_response("There must be at least one type of movement")

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_UUID(user_id):
                return invalid_field_response("user_id")

            if not is_valid_number(amount):
                return invalid_field_response("amount")

            if not is_valid_timestamp(movement_date):
                return invalid_field_response("movement_date")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            user_id = g.user_id

            conn, cursor = get_db()

            cursor.execute(
                """
                INSERT INTO movement (id, user_id, amount, movement_date, description, expense_id, income_id, transfer_id, last_modified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [id, user_id, amount, movement_date, description, expense_id, income_id, transfer_id, last_modified],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Movement added successfully"})
            else:
                return database_error_reponse()

        if request.method == "DELETE":
            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT user_id
                FROM movement
                WHERE id = %s AND NOT deleted
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Movement not found")

            if g.user_id != row["user_id"]:
                return unauthorized_response("Can't delete movement from another user")

            cursor.execute(
                """
                UPDATE movement
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
                return ok_response({"message": "Movement deleted successfully"})
            else:
                return database_error_reponse()

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
