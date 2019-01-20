"""
Directions service
"""
import abc
from typing import Any, Dict, Iterable, List, NamedTuple, Type, TypeVar

import cerberus  # type: ignore
import requests

import crib
from crib import exceptions, plugins


class Location(NamedTuple):
    latitude: float
    longitude: float


class DirectionsService(plugins.Plugin):
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
            },
            "arrival-time": {"type": "integer", "required": True},
            "search-area": {
                "type": "dict",
                "required": True,
                "schema": {
                    "northEast": {
                        "type": "dict",
                        "required": True,
                        "schema": {
                            "lat": {"type": "float", "required": True},
                            "lng": {"type": "float", "required": True},
                        },
                    },
                    "southWest": {
                        "type": "dict",
                        "required": True,
                        "schema": {
                            "lat": {"type": "float", "required": True},
                            "lng": {"type": "float", "required": True},
                        },
                    },
                },
            },
        }

    @abc.abstractmethod
    def to_work(self, origin: Location, mode: str) -> Dict:
        return {}

    @abc.abstractmethod
    def map_to_work(self, mode: str) -> List[Dict]:
        return []


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
            "arrival_time": self.config["arrival-time"],
            "mode": mode,
        }
        response = requests.get(self._URL, args)
        response.raise_for_status()

        data = response.json()
        if data["status"] != "OK":
            raise exceptions.DirectionsError(
                data.get("error_message", "Invalid request")
            )
        route = data["routes"][0]["legs"][0]
        route["overview_polyline"] = data["routes"][0]["overview_polyline"]

        return route

    def map_to_work(self, mode: str) -> List[Dict]:
        return []


DS = TypeVar("DS", bound=DirectionsService)
TDS = Type[DS]


@crib.hookimpl
def crib_add_directions_services() -> Iterable[TDS]:
    return [GoogleDirections]
