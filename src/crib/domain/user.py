"""
User model
"""
from crib.domain.model import Model, SchemaType
from crib.validation import vstr


class User(Model):
    schema: SchemaType = {"username": vstr(), "password": vstr()}
