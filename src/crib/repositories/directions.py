"""
Repository for route data
"""
import abc
from typing import Dict, Iterable, List, Type, TypeVar

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


class MemoryDirectionsRepo(DirectionsRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._storage: List[Direction] = []

    def insert(self, direction: Direction) -> None:
        self._storage.append(direction)

    def get_all(self) -> Iterable[Direction]:
        for d in self._storage:
            yield d

    def get_to_work_durations(self) -> Iterable[Dict]:
        for d in self._storage:
            yield {
                "location": {
                    "latitude": d["start_location"]["lat"],
                    "longitude": d["start_location"]["lng"],
                },
                "duration": d["duration"]["value"],
            }


class MongoDirectionsRepo(DirectionsRepo, mongo.MongoRepo):
    @property
    def _directions(self):
        return self.db.directions

    def insert(self, direction: Direction) -> None:
        d = dict(direction)
        self._directions.insert_one(d)

    def get_all(self) -> Iterable[Direction]:
        for d in self._directions.find():
            d.pop("_id")
            yield Direction(d)

    def get_to_work_durations(self) -> Iterable[Dict]:
        for d in self._directions.find():
            yield {
                "location": [d["start_location"]["lat"], d["start_location"]["lng"]],
                "durationValue": d["duration"]["value"],
                "duration": d["duration"]["text"],
            }


DR = TypeVar("DR", bound=DirectionsRepo)
TDR = Type[DR]


@crib.hookimpl
def crib_add_directions_repos() -> Iterable[TDR]:
    return [MemoryDirectionsRepo, MongoDirectionsRepo]
