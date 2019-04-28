"""
Simple crud repository base class
"""
import abc
from typing import Any, Dict, Iterable, Type, TypeVar

import pymongo  # type: ignore

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
        try:
            return self._storage[identity]
        except KeyError:
            raise exceptions.EntityNotFound(identity)

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


class MongoPropertyRepo(PropertyRepo, mongo.MongoRepo):
    @property
    def _props(self):
        return self.db.properties

    def _to_prop(self, data: Dict[str, Any]) -> Property:
        data.pop("_id")
        return Property.fromdict(data)

    def exists(self, identity: str) -> bool:
        return bool(self._props.find_one({"_id": identity}))

    def insert(self, prop: Property) -> None:
        p = prop.asdict()
        p["_id"] = prop.id
        try:
            self._props.insert_one(p)
        except pymongo.errors.DuplicateKeyError:
            raise exceptions.DuplicateProperty(p)

    def update(self, prop: Property) -> None:
        p = prop.asdict()
        p["_id"] = prop.id
        result = self._props.replace_one({"_id": prop.id}, p)
        if result.matched_count == 0:
            raise exceptions.EntityNotFound(prop.id)
        assert result.matched_count == 1, "Duplicate IDs"

    def get(self, identity: str) -> Property:
        data = self._props.find_one({"_id": identity})
        if data is None:
            raise exceptions.EntityNotFound(identity)

        prop = self._to_prop(data)
        return prop

    def get_all(self):
        for data in self._props.find():
            yield self._to_prop(data)

    def find(self, order_by=(), limit=1000) -> Iterable[Property]:
        queried_props = self._props.find(
            {
                "propertyImages.3": {"$exists": True},
                "banned": {"$ne": True},
                "students": {"$ne": True},
                "price.amount": {"$lt": 1420},
            }
        )
        if order_by:
            order_by = [(field, self._to_order(i)) for field, i in order_by]
            queried_props = queried_props.sort(order_by)
        if limit:
            queried_props = queried_props.limit(limit)

        for data in queried_props:
            yield self._to_prop(data)

    @staticmethod
    def _to_order(x):
        if x == 1:
            return pymongo.ASCENDING
        elif x == -1:
            return pymongo.DESCENDING
        else:
            raise exceptions.UnknownOrder(
                "Order has to be either 1 for ascending or -1 for descending."
            )

    def delete(self, identity: str) -> None:
        result = self._props.delete_one({"_id": identity})
        if result.deleted_count == 0:
            raise exceptions.EntityNotFound(identity)

    def clear(self, banned=False, favorites=False) -> None:
        qfilter = {}
        if not banned:
            expressions = qfilter.setdefault("$and", [])
            expressions.append({"banned": {"$ne": True}})
        if not favorites:
            expressions = qfilter.setdefault("$and", [])
            expressions.append({"favorite": {"$ne": True}})
        self._props.delete_many(qfilter)

    def count(self) -> int:
        return self._props.count()


PR = TypeVar("PR", bound=PropertyRepo)
TPR = Type[PR]


@crib.hookimpl
def crib_add_property_repos() -> Iterable[TPR]:
    return [MemoryPropertyRepo, MongoPropertyRepo]
