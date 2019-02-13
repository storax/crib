"""
Directions service
"""
import abc
import logging
from typing import Any, Dict, Iterable, Type, TypeVar

import cmocean  # type: ignore
import numpy  # type: ignore
import requests
from matplotlib.colors import rgb2hex  # type: ignore

import crib
from crib import exceptions, injection, plugins
from crib.domain.direction import Location

log = logging.getLogger(__name__)


class DirectionsService(plugins.Plugin):
    directions_repository = injection.Dependency()

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

    def fetch_map_to_work(self, mode: str) -> Iterable[Dict]:
        for i, ll in list(enumerate(self.raster_map())):
            log.info("Fetching #%s", i)
            yield self.to_work(Location(**ll), mode)

    def raster_map(self) -> Iterable[Dict]:
        ne = self.config["search-area"]["northEast"]
        sw = self.config["search-area"]["southWest"]
        latdelta = ne["lat"] - sw["lat"]
        lngdelta = ne["lng"] - sw["lng"]
        for lat in frange(sw["lat"], ne["lat"], latdelta / 100):
            for lng in frange(sw["lng"], ne["lng"], lngdelta / 100):
                yield {"latitude": lat, "longitude": lng}

    def to_work_durations(
        self, colormap: str = "thermal_r"
    ) -> Iterable[Dict[str, Any]]:
        try:
            cmap = cmocean.cm.cmap_d[colormap]
        except KeyError:
            raise ValueError(f"Invalid color map {colormap}")

        durations = list(self.directions_repository.get_to_work_durations())
        sortkey = lambda d: d["durationValue"]
        maxD = max(durations, key=sortkey)["durationValue"]
        minD = min(durations, key=sortkey)["durationValue"]

        colors = self._color_values(minD, maxD, cmap)

        offset = minD + 1
        for d in durations:
            v = d.pop("durationValue")
            d["color"] = colors[v - offset]
        log.debug("Fetched %s durations", len(durations))

        return durations

    def colormaps(self) -> Iterable[str]:
        return list(cmocean.cm.cmap_d.keys())

    @staticmethod
    def _color_values(minV, maxV, colormap):
        delta = maxV - minV
        colormap = colormap._resample(delta)
        rgb_values = colormap(numpy.arange(delta))[:, :-1]
        hex_values = [rgb2hex(rgb) for rgb in rgb_values]
        return hex_values


class GoogleDirections(DirectionsService):
    _URL = "https://maps.googleapis.com/maps/api/directions/json"

    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        schema = super(GoogleDirections, cls).config_schema()
        schema.update({"api-key": {"type": "string", "required": True}})
        return schema

    def to_work(self, origin: Location, mode: str) -> Dict:
        log.info("Fetching route to work: %s, %s", origin.latitude, origin.longitude)
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
            if data["status"] == "ZERO_RESULTS":
                return {}
            raise exceptions.DirectionsError(data)
        route = data["routes"][0]["legs"][0]
        route["overview_polyline"] = data["routes"][0]["overview_polyline"]

        return route


DS = TypeVar("DS", bound=DirectionsService)
TDS = Type[DS]


@crib.hookimpl
def crib_add_directions_services() -> Iterable[TDS]:
    return [GoogleDirections]


def frange(x, y, jump=1.0):
    """Range for floats

    Credit: https://gist.github.com/axelpale/3e780ebdde4d99cbb69ffe8b1eada92c
    """
    i = 0.0
    x = float(x)  # Prevent yielding integers.
    x0 = x
    epsilon = jump / 2.0
    yield x  # yield always first value
    while x + epsilon < y:
        i += 1.0
        x = x0 + i * jump
        yield x
