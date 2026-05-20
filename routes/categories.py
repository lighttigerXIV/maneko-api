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
    is_valid_color,
    is_valid_string,
    is_valid_timestamp,
    is_valid_UUID,
)

categories_blueprint = Blueprint("categories_blueprint", __name__)


@categories_blueprint.route("/categories", methods=["GET", "PUT", "POST"])
@categories_blueprint.route("/categories/<string:id>", methods=["GET", "DELETE"])
@authenticated
def categories(id=None):
    try:
        if request.method == "GET":
            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT user_id, name, icon, color, last_modified
                FROM category
                WHERE NOT deleted AND id = %s
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Category not found")

            user_id = g.user_id
            category_user_id = row["user_id"]

            if user_id != category_user_id:
                return unauthorized_response("Can't access another user category")

            conn.close()
            cursor.close()

            del row["user_id"]

            return ok_response(row)

        if request.method == "PUT":
            body = get_body()

            id = body["id"]

            if not id:
                return missing_fields_reponse("id")

            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT user_id, name, icon, color, last_modified
                FROM category
                WHERE NOT deleted AND id = %s
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Category not found")

            if row["user_id"] != g.user_id:
                return unauthorized_response("Can't modify another user category")

            name = body["name"] if "name" in body else row["name"]
            icon = body["icon"] if "icon" in body else row["icon"]
            color = body["color"] if "color" in body else row["color"]
            last_modified = (
                body["last_modified"] if "last_modified" in body else (datetime.now(timezone.utc).timestamp() * 1000)
            )

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_string(icon):
                return invalid_field_response("icon")

            if not is_valid_color(color):
                return invalid_field_response("color")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            cursor.execute(
                """
                UPDATE category
                SET name=%s, icon=%s, color=%s, last_modified=%s
                WHERE id = %s
                """,
                [name, icon, color, last_modified, id],
            )

            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Category updated successfully"})
            else:
                return database_error_reponse()

        if request.method == "POST":
            body = get_body()

            fields = ["id", "name", "icon", "color", "last_modified"]

            if not body_has_fields(body, fields):
                return missing_fields_reponse(fields)

            id = body["id"]
            name = body["name"]
            icon = body["icon"]
            color = body["color"]
            last_modified = body["last_modified"]

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_string(icon):
                return invalid_field_response("icon")

            if not is_valid_color(color):
                return invalid_field_response("color")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            user_id = g.user_id

            conn, cursor = get_db()

            cursor.execute(
                """
                INSERT INTO category (id, user_id, name, icon, color, last_modified)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                [id, user_id, name, icon, color, last_modified],
            )

            conn.commit()
            conn.close()

            success = cursor.rowcount > 0

            cursor.close()

            if success:
                return ok_response({"message": "Category added successfully"})
            else:
                return database_error_reponse()

        if request.method == "DELETE":
            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT user_id
                FROM category
                WHERE id = %s AND NOT deleted
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Category not found")

            if g.user_id != row["user_id"]:
                return unauthorized_response("Can't delete category from another user")

            cursor.execute(
                """
                UPDATE category
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
                return ok_response({"message": "Category deleted successfully"})
            else:
                return database_error_reponse()

        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
