"""
Generic scraper
"""
import abc

import cerberus


class Scraper:
    def __init__(self, config):
        super().__init__()
        schema = self.config_schema()
        validator = cerberus.Validator(schema)
        if not validator.validate(config):
            raise ConfigError(f"Invalid config for {self.name()}", validator.errors)

    @classmethod
    @abc.abstractmethod
    def config_schema(cls):
        return {}

    @classmethod
    def name(cls):
        return cls.__name__

    def __repr__(self):
        name = type(self).__name__
        return f"{name}()"


class ConfigError(Exception):
    def __init__(self, msg, errors):
        super().__init__(msg, errors)
        self.msg = msg
        self.errors = errors

    def __str__(self):
        errors = "\n".join(
            f"\t{field}: {reasons}" for field, reasons in self.errors.items()
        )
        return f"{self.msg}:\n{errors}"
