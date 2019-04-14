"""
User model
"""
from werkzeug.security import check_password_hash  # type: ignore

from crib.domain.model import Model, SchemaType

_CRED_SCHEMA = {"type": "string", "required": True, "minlength": 3}


class User(Model):
    schema: SchemaType = {"username": _CRED_SCHEMA, "password": _CRED_SCHEMA}

    def is_password_valid(self, password):
        return check_password_hash(self["password"], password)
