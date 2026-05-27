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
    is_valid_string,
    is_valid_timestamp,
    is_valid_UUID,
)

incomes_blueprint = Blueprint("incomes_blueprint", __name__)


@incomes_blueprint.route("/incomes", methods=["POST", "PUT"])
@authenticated
def incomes():
    try:
        if request.method == "PUT":
            body = get_body()

            id = body["id"]

            if not id:
                return missing_fields_reponse("id")

            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT a.user_id, e.account_id, e.category_id, e.sub_category_id, e.info, e.last_modified
                FROM income e
                LEFT JOIN account a ON a.id = e.account_id
                WHERE e.id = %s
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Income not found")

            if row["user_id"] != g.user_id:
                return unauthorized_response("Can't modify another user income")

            account_id = get_put_field(body, row, "account_id")
            category_id = get_put_field(body, row, "category_id")
            sub_category_id = get_put_field(body, row, "sub_category_id")
            info = get_put_field(body, row, "info")
            last_modified = get_put_field(body, row, "last_modified")

            print(account_id, category_id, sub_category_id, info, last_modified)

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_UUID(account_id):
                return invalid_field_response("account_id")

            if not is_valid_UUID(sub_category_id):
                return invalid_field_response("sub_category_id")

            if not is_valid_string(info):
                return invalid_field_response("info")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            cursor.execute(
                """
                UPDATE income
                SET account_id = %s, category_id = %s, sub_category_id = %s, info = %s, last_modified = %s
                WHERE id = %s
                """,
                [account_id, category_id, sub_category_id, info, last_modified, id],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Income updated successfully"})
            else:
                return database_error_reponse()

        if request.method == "POST":
            body = get_body()

            fields = ["id", "account_id", "category_id", "sub_category_id", "info", "last_modified"]

            if not body_has_fields(body, fields):
                return missing_fields_reponse(fields)

            id = body["id"]
            account_id = body["account_id"]
            category_id = body["category_id"]
            sub_category_id = body["sub_category_id"]
            info = body["info"]
            last_modified = body["last_modified"]

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_UUID(account_id):
                return invalid_field_response("account_id")

            if not is_valid_UUID(sub_category_id):
                return invalid_field_response("sub_category_id")

            if not is_valid_string(info):
                return invalid_field_response("info")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            conn, cursor = get_db()

            cursor.execute(
                """
                INSERT INTO income (id, account_id, category_id, sub_category_id, info, last_modified)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [id, account_id, category_id, sub_category_id, info, last_modified],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Income added successfully"})

            return database_error_reponse()

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
