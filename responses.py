from flask import jsonify


class HTTP_CODES:
    OK = 200
    INTERNAL_ERROR = 500


def ok_response(content):
    return jsonify(content), HTTP_CODES.OK


def internal_error_response(exception):
    return jsonify({"api_error": str(exception)}), HTTP_CODES.INTERNAL_ERROR
