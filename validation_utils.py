import re

from flask import request


def get_body():
    return request.json


def body_has_fields(body, fields) -> bool:
    for field in fields:
        if field not in body:
            return False

    return True


def is_valid_string(field) -> bool:
    return len(field.strip()) > 0


def is_valid_number(field) -> bool:
    return isinstance(field, (int, float)) and not isinstance(field, bool)


def is_valid_email(field) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", field))
