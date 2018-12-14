"""
Generic scraper
"""
import abc
from typing import Dict, Iterable

import cerberus  # type: ignore

from crib.domain.property import Property
from crib.exceptions import ConfigError


class Scraper(metaclass=abc.ABCMeta):
    def __init__(self, config) -> None:
        super().__init__()
        schema = self.config_schema()
        validator = cerberus.Validator(schema)
        if not validator.validate(config):
            raise ConfigError(f"Invalid config for {self.name()}", validator.errors)
        self.config = validator.document

    @classmethod
    @abc.abstractmethod
    def config_schema(cls) -> Dict:
        return {}

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @abc.abstractmethod
    def scrape(self) -> Iterable[Property]:
        pass

    def __str__(self) -> str:
        name = type(self).__name__
        return f"{name}"
