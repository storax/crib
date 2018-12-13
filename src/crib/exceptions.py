"""
Exceptions
"""


class ValidationError(Exception):
    def __init__(self, msg, errors):
        super().__init__(msg, errors)
        self.msg = msg
        self.errors = errors

    def __str__(self):
        errors = "\n".join(
            f"\t{field}: {reasons}" for field, reasons in self.errors.items()
        )
        return f"{self.msg}:\n{errors}"


class InvalidPropertyData(ValidationError):
    pass


class ConfigError(ValidationError):
    pass


class EntityNotFound(Exception):
    pass


class PluginNotFound(Exception):
    pass


class DuplicateProperty(Exception):
    pass