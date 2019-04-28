"""
User model
"""
import attr
from werkzeug.security import check_password_hash  # type: ignore

from .model import Model


def _cred_validator(instance, attribute: attr.Attribute, value: str) -> None:
    if len(value) < 3:
        raise ValueError(f"{attribute} must be longer than 3 characters.")


@attr.s(frozen=True)
class User(Model):
    username: str = attr.ib(validator=_cred_validator)
    password: str = attr.ib(validator=_cred_validator)

    def is_password_valid(self, password: str):
        return check_password_hash(self.password, password)
