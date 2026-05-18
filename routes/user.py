from flask import Blueprint

from db import get_db
from responses import internal_error_response, ok_response

user_blueprint = Blueprint("user_blueprint", __name__)


@user_blueprint.route("/user", methods=["GET", "POST"])
def user():
    try:
        conn, cursor = get_db()

        cursor.execute("""SELECT * FROM testing""")
        rows = cursor.fetchall()

        return ok_response(rows)
    except Exception as e:
        return internal_error_response(e)
