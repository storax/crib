"""
Module to help writing plugins.
"""
from typing import Any, Dict

import cerberus  # type: ignore

from crib import exceptions, injection


class PluginComponent(injection.Component):
    """A component that is classified as a plugin."""

    @classmethod
    def plugin_type(cls) -> str:
        return cls.__name__


class Plugin(PluginComponent):
    """Component which has a config that is validated.

    If the configuration has a key "type" in it (e.g. for the
    ConfiguredPluginProvider) it is removed before validation.

    """

    _config = injection.Infrastructure("config")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        schema = self.config_schema()
        validator = cerberus.Validator(schema)
        cfg = self._config.copy()
        cfg.pop("type", None)

        if not validator.validate(cfg):
            raise exceptions.ConfigError(
                f"Invalid config for {self.name()}", validator.errors
            )
        self.config = validator.document

    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        return {}
