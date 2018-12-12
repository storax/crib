"""
Generic scraper
"""
import abc

import cerberus

from crib.exceptions import ConfigError


class Scraper(metaclass=abc.ABCMeta):
    def __init__(self, config):
        super().__init__()
        schema = self.config_schema()
        validator = cerberus.Validator(schema)
        if not validator.validate(config):
            raise ConfigError(f"Invalid config for {self.name()}", validator.errors)
        self.config = validator.document

    @classmethod
    @abc.abstractmethod
    def config_schema(cls):
        return {}

    @classmethod
    def name(cls):
        return cls.__name__

    @abc.abstractmethod
    def scrape(self):
        pass

    def __str__(self):
        name = type(self).__name__
        return f"{name}"
