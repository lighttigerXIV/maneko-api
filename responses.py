from flask import jsonify


class HTTP_CODES:
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    CONFLICT = 409
    INTERNAL_ERROR = 500


def ok_response(content):
    return jsonify(content), HTTP_CODES.OK


def bad_request_response(message=None):
    return jsonify(
        {"error_type": "Bad Request", "message": message if message else "Something went wrong"}
    ), HTTP_CODES.BAD_REQUEST


def missing_fields_reponse(fields):
    return bad_request_response(f"The following fields are required: {fields}")


def invalid_field_response(field):
    return bad_request_response(f"The field [{field}] is invalid")


def unauthorized_response(message):
    return jsonify({"error_type": "Unhauthorized", "message": message}), HTTP_CODES.UNAUTHORIZED


def conflict_response(message):
    return jsonify({"error_type": "Conflict", "message": message}), HTTP_CODES.CONFLICT


def internal_error_response(exception):
    return jsonify({"error_type": "Internal Error", "message": str(exception)}), HTTP_CODES.INTERNAL_ERROR


def database_error_reponse():
    return jsonify(
        {"error_type": "Internal Error", "message": "Failed to get data from database"}
    ), HTTP_CODES.INTERNAL_ERROR
