"""
Repository for route data
"""
import abc
from typing import Any, Dict, Iterable, Type, TypeVar

import pymongo  # type: ignore

import crib
from crib import exceptions, plugins
from crib.domain.property import Property

from . import mongo


class DirectionsRepo(plugins.Plugin):
    pass


class MemoryDirectionsRepo(DirectionsRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._storage: Dict[str, Dict] = {}


class MongoDirectionsRepo(DirectionsRepo, mongo.MongoRepo):
    @property
    def _directions(self):
        return self.db.directions


DR = TypeVar("DR", bound=DirectionsRepo)
TDR = Type[DR]


@crib.hookimpl
def crib_add_directions_repos() -> Iterable[TDR]:
    return [MemoryDirectionsRepo, MongoDirectionsRepo]
