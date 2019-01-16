"""
Directions service
"""
import abc
from typing import Any, Dict, Iterable, NamedTuple, Type, TypeVar

import cerberus  # type: ignore
import requests

import crib
from crib import exceptions


class Location(NamedTuple):
    latitude: float
    longitude: float


class DirectionsService(metaclass=abc.ABCMeta):
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
        return {
            "work-location": {
                "type": "dict",
                "required": True,
                "schema": {
                    "latitude": {"type": "float", "required": True},
                    "longitude": {"type": "float", "required": True},
                },
            }
        }

    @abc.abstractmethod
    def to_work(self, origin: Location, mode: str) -> Dict:
        return {}


class GoogleDirections(DirectionsService):
    _URL = "https://maps.googleapis.com/maps/api/directions/json"

    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        schema = super(GoogleDirections, cls).config_schema()
        schema.update({"api-key": {"type": "string", "required": True}})
        return schema

    def to_work(self, origin: Location, mode: str) -> Dict:
        key = self.config["api-key"]
        work = Location(**self.config["work-location"])
        args = {
            "key": key,
            "origin": ",".join((str(origin.latitude), str(origin.longitude))),
            "destination": ",".join((str(work.latitude), str(work.longitude))),
            "mode": mode,
        }
        response = requests.get(self._URL, args)
        response.raise_for_status()
        return response.json()


DS = TypeVar("DS", bound=DirectionsService)
TDS = Type[DS]


@crib.hookimpl
def crib_add_directions_services() -> Iterable[TDS]:
    return [GoogleDirections]