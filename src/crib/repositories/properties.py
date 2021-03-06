"""
Simple crud repository base class
"""
import abc
import itertools
from typing import Any, Dict, Iterable, Type, TypeVar

import geopandas
import pymongo  # type: ignore
from shapely import geometry

import crib
from crib import exceptions, plugins
from crib.domain import Property

from . import mongo


class PropertyRepo(plugins.Plugin):
    @abc.abstractmethod
    def insert(self, prop: Property) -> None:
        pass

    @abc.abstractmethod
    def update(self, prop: Property) -> None:
        pass

    @abc.abstractmethod
    def get(self, identity: str) -> Property:
        pass

    @abc.abstractmethod
    def exists(self, identity: str) -> bool:
        pass

    @abc.abstractmethod
    def get_all(self) -> Iterable[Property]:
        pass

    @abc.abstractmethod
    def delete(self, identity: str) -> None:
        pass

    @abc.abstractmethod
    def clear(self, banned=False, favorites=False) -> None:
        pass

    @abc.abstractmethod
    def count(self) -> int:
        pass

    @abc.abstractmethod
    def find(
        self, max_price=None, favorite=None, area=None, limit=None
    ) -> Iterable[Property]:
        pass


class MemoryPropertyRepo(PropertyRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._storage: Dict[str, Property] = {}

    def insert(self, prop: Property) -> None:
        if prop.id in self._storage:
            raise exceptions.DuplicateProperty(prop)
        self._storage[prop.id] = prop

    def update(self, prop: Property) -> None:
        if prop.id not in self._storage:
            raise exceptions.EntityNotFound(prop.id)
        self._storage[prop.id] = prop

    def exists(self, identity: str) -> bool:
        return identity in self._storage

    def get(self, identity: str) -> Property:
        return self._storage.get(identity)

    def get_all(self) -> Iterable[Property]:
        for p in self._storage.values():
            yield p

    def delete(self, identity: str) -> None:
        try:
            del self._storage[identity]
        except KeyError:
            raise exceptions.EntityNotFound(identity)

    def clear(self, banned=False, favorites=False) -> None:
        if banned and favorites:
            self._storage = {}

        self._storage = {
            k: v
            for k, v in self._storage.items()
            if not ((banned and v.banned) or (favorites and v.favorite))
        }

    def count(self) -> int:
        return len(self._storage)

    def find(
        self, max_price=None, favorite=None, area=None, limit=None
    ) -> Iterable[Property]:
        limit = limit or 1000
        max_price = max_price or 1450
        predicate = (
            lambda p: p.price.amount <= max_price
            and (favorite is None or p.favorite == favorite)
            and (
                area is None
                or area.contains(
                    geometry.Point(p.location.longitude, p.location.latitude)
                )
            )
        )

        props = (p for p in self._storage.values() if predicate(p))
        return itertools.islice(props, limit)


class MongoPropertyRepo(PropertyRepo, mongo.MongoRepo):
    @property
    def _props(self):
        return self.db.properties

    @property
    def _search_areas(self):
        return self.db.search_areas

    def _to_prop(self, data: Dict[str, Any]) -> Property:
        data.pop("_id")
        coords = data["location"]["coordinates"]
        data["location"] = {"longitude": coords[0], "latitude": coords[1]}
        return Property.fromdict(data)

    def _to_storage(self, prop: Property) -> Dict[str, Any]:
        p = prop.asdict()
        p["_id"] = prop.id
        p["location"] = {
            "type": "Point",
            "coordinates": [p["location"]["longitude"], p["location"]["latitude"]],
        }
        return p

    def exists(self, identity: str) -> bool:
        return bool(self._props.find_one({"_id": identity}))

    def insert(self, prop: Property) -> None:
        p = self._to_storage(prop)
        try:
            self._props.insert_one(p)
        except pymongo.errors.DuplicateKeyError:
            raise exceptions.DuplicateProperty(p)

    def update(self, prop: Property) -> None:
        p = self._to_storage(prop)
        result = self._props.replace_one({"_id": prop.id}, p)
        if result.matched_count == 0:
            raise exceptions.EntityNotFound(prop.id)
        assert result.matched_count == 1, "Duplicate IDs"

    def get(self, identity: str) -> Property:
        data = self._props.find_one({"_id": identity})
        return self._to_prop(data) if data else None

    def get_all(self):
        for data in self._props.find():
            yield self._to_prop(data)

    def find(
        self, max_price=None, favorite=None, area=None, limit=None
    ) -> Iterable[Property]:
        max_price = max_price or 1450
        limit = limit or 5000
        params = {
            "propertyImages.3": {"$exists": True},
            "banned": {"$ne": True},
            "students": {"$ne": True},
            "price.amount": {"$lte": max_price},
        }
        if favorite is not None:
            params["favorite"] = {"$eq": favorite}

        if area is not None:
            geoarea = geopandas.GeoSeries(area).__geo_interface__["features"][0][
                "geometry"
            ]
            params["location"] = {"$geoWithin": {"$geometry": geoarea}}

        queried_props = self._props.find(params)
        order_by = [("firstVisibleDate", pymongo.DESCENDING)]
        queried_props = queried_props.sort(order_by)
        queried_props = queried_props.limit(limit)

        for data in queried_props:
            yield self._to_prop(data)

    def delete(self, identity: str) -> None:
        result = self._props.delete_one({"_id": identity})
        if result.deleted_count == 0:
            raise exceptions.EntityNotFound(identity)

    def clear(self, banned=False, favorites=False) -> None:
        qfilter: Dict = {}
        if not banned:
            expressions = qfilter.setdefault("$and", [])
            expressions.append({"banned": {"$ne": True}})
        if not favorites:
            expressions = qfilter.setdefault("$and", [])
            expressions.append({"favorite": {"$ne": True}})
        self._props.delete_many(qfilter)

    def count(self) -> int:
        return self._props.count()

    def set_search_area(self, name: str, geojson) -> None:
        self._search_areas.save({"_id": name, "name": name, "geojson": geojson})

    def get_search_areas(self):
        return [
            {"name": a["name"], "geojson": a["geojson"]}
            for a in self._search_areas.find({})
        ]


PR = TypeVar("PR", bound=PropertyRepo)
TPR = Type[PR]


@crib.hookimpl
def crib_add_property_repos() -> Iterable[TPR]:
    return [MemoryPropertyRepo, MongoPropertyRepo]
