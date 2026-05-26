import datetime
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
from validation_utils import body_has_fields, get_body, is_valid_string, is_valid_timestamp, is_valid_UUID

subcategories_blueprint = Blueprint("subcategories_blueprint", __name__)


@subcategories_blueprint.route("/subcategories", methods=["GET", "PUT", "POST"])
@subcategories_blueprint.route("/subcategories/<string:id>", methods=["GET", "DELETE"])
@authenticated
def subcategories(id=None):
    try:
        if request.method == "GET":
            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT c.user_id, category_id, sc.name, sc.icon, sc.last_modified
                FROM sub_category sc
                LEFT JOIN category c ON c.id = category_id
                WHERE NOT sc.deleted AND sc.id = %s
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Sub Category not found")

            user_id = g.user_id
            subcategory_user_id = row["user_id"]

            if user_id != subcategory_user_id:
                return unauthorized_response("Can't access another user subcategory")

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
                SELECT c.user_id, category_id, sc.name, sc.icon, sc.last_modified
                FROM sub_category sc
                LEFT JOIN category c ON c.id = category_id
                WHERE NOT sc.deleted AND sc.id = %s
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Sub Category not found")

            if row["user_id"] != g.user_id:
                return unauthorized_response("Can't modify another user sub category")

            name = body["name"] if "name" in body else row["name"]
            icon = body["icon"] if "icon" in body else row["icon"]
            last_modified = (
                body["last_modified"] if "last_modified" in body else (datetime.now(timezone.utc).timestamp() * 1000)
            )

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_string(icon):
                return invalid_field_response("icon")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            cursor.execute(
                """
                UPDATE sub_category
                SET name=%s, icon=%s, last_modified=%s
                WHERE id = %s
                """,
                [name, icon, last_modified, id],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Sub Category updated successfully"})
            else:
                return database_error_reponse()

        if request.method == "POST":
            body = get_body()

            fields = ["id", "category_id", "name", "icon", "last_modified"]

            if not body_has_fields(body, fields):
                return missing_fields_reponse(fields)

            id = body["id"]
            category_id = body["category_id"]
            name = body["name"]
            icon = body["icon"]
            last_modified = body["last_modified"]

            if not is_valid_UUID(id):
                return invalid_field_response("id")

            if not is_valid_UUID(category_id):
                return invalid_field_response("category_id")

            if not is_valid_string(name):
                return invalid_field_response("name")

            if not is_valid_string(icon):
                return invalid_field_response("icon")

            if not is_valid_timestamp(last_modified):
                return invalid_field_response("last_modified")

            conn, cursor = get_db()

            cursor.execute(
                """
                INSERT INTO sub_category (id, category_id, name, icon, last_modified)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [id, category_id, name, icon, last_modified],
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()
            cursor.close()

            if success:
                return ok_response({"message": "Sub Category added successfully"})
            else:
                return database_error_reponse()

        if request.method == "DELETE":
            conn, cursor = get_db()

            cursor.execute(
                """
                SELECT c.user_id
                FROM sub_category sc
                LEFT JOIN category c ON c.id = sc.category_id
                WHERE sc.id = %s AND NOT sc.deleted
                """,
                [id],
            )

            row = cursor.fetchone()

            if not row:
                return not_found_response("Sub Category not found")

            if g.user_id != row["user_id"]:
                return unauthorized_response("Can't delete sub category from another user")

            cursor.execute(
                """
                UPDATE sub_category
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
                return ok_response({"message": "Sub Category deleted successfully"})
            else:
                return database_error_reponse()
        return bad_request_response()
    except Exception as e:
        return internal_error_response(e)
