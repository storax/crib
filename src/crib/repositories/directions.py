"""
Repository for route data
"""
import abc
from typing import Dict, Iterable, List, Type, TypeVar

import geopandas
from shapely.geometry import shape

import crib
from crib import plugins
from crib.domain.direction import Direction

from . import mongo


class DirectionsRepo(plugins.Plugin):
    @abc.abstractmethod
    def insert(self, direction: Direction) -> None:
        pass

    @abc.abstractmethod
    def get_all(self) -> Iterable[Direction]:
        pass

    @abc.abstractmethod
    def get_to_work_durations(self) -> Iterable[Dict]:
        pass

    def insert_to_work_area(self, max_duration: int, area):
        pass

    def get_to_work_area(self, max_duration: int):
        pass


class MemoryDirectionsRepo(DirectionsRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._storage: List[Direction] = []
        self._work_areas: Dict[int, any] = {}

    def insert(self, direction: Direction) -> None:
        self._storage.append(direction)

    def get_all(self) -> Iterable[Direction]:
        for d in self._storage:
            yield d

    def get_to_work_durations(self) -> Iterable[Dict]:
        for d in self._storage:
            yield {
                "location": {
                    "latitude": d.start_location.lat,
                    "longitude": d.start_location.lng,
                },
                "duration": d.duration.value,
            }

    def insert_to_work_area(self, max_duration: int, area):
        self._work_areas[max_duration] = area

    def get_to_work_area(self, max_duration: int):
        return self._work_areas.get(max_duration)


class MongoDirectionsRepo(DirectionsRepo, mongo.MongoRepo):
    @property
    def _directions(self):
        return self.db.directions

    @property
    def _work_areas(self):
        return self.db.work_areas

    def insert(self, direction: Direction) -> None:
        d = direction.asdict()
        self._directions.insert_one(d)

    def get_all(self) -> Iterable[Direction]:
        for d in self._directions.find():
            d.pop("_id")
            yield Direction.fromdict(d)

    def get_to_work_durations(self) -> Iterable[Dict]:
        for d in self._directions.find():
            yield {
                "location": [d["start_location"]["lat"], d["start_location"]["lng"]],
                "durationValue": d["duration"]["value"],
                "duration": d["duration"]["text"],
            }

    def insert_to_work_area(self, max_duration: int, area):
        areajson = geopandas.GeoSeries(area).__geo_interface__
        if not areajson["features"]:
            return
        areadata = areajson["features"][0]["geometry"]
        self._work_areas.insert_one({"max_duration": max_duration, "area": areadata})

    def get_to_work_area(self, max_duration: int):
        result = next(self._work_areas.find({"max_duration": max_duration}), None)
        if not result:
            return None
        data = result["area"]
        area = shape(data)
        return area


DR = TypeVar("DR", bound=DirectionsRepo)
TDR = Type[DR]


@crib.hookimpl
def crib_add_directions_repos() -> Iterable[TDR]:
    return [MemoryDirectionsRepo, MongoDirectionsRepo]
