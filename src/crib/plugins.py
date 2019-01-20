"""
Module to help writing plugins.
"""
import abc
from typing import Any, Dict

import cerberus  # type: ignore

from crib import exceptions


class Plugin(metaclass=abc.ABCMeta):
    def __init__(self, config: Dict) -> None:
        super().__init__()
        schema = self.config_schema()
        validator = cerberus.Validator(schema)
        if not validator.validate(config):
            raise exceptions.ConfigError(
                f"Invalid config for {self.name()}", validator.errors
            )
        self.config = validator.document

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        return {}
