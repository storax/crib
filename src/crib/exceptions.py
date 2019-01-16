"""
Exceptions
"""

from typing import Dict


class ValidationError(Exception):
    def __init__(self, msg: str, errors: Dict) -> None:
        super().__init__(msg, errors)
        self.msg = msg
        self.errors = errors

    def __str__(self) -> str:
        errors = "\n".join(
            f"\t{field}: {reasons}" for field, reasons in self.errors.items()
        )
        return f"{self.msg}:\n{errors}"


class InvalidPropertyData(ValidationError):
    pass


class InvalidUserData(ValidationError):
    pass


class ConfigError(ValidationError):
    pass


class EntityNotFound(Exception):
    pass


class PluginNotFound(Exception):
    pass


class DuplicateProperty(Exception):
    pass


class DuplicateUser(Exception):
    pass


class InvalidQuery(Exception):
    pass


class UnknownOrder(InvalidQuery):
    pass


class DirectionsError(Exception):
    pass
