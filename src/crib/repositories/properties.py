"""
Simple crud repository base class
"""
import abc
from typing import Any, Dict, Iterable, Type, TypeVar

import cerberus  # type: ignore
import pymongo  # type: ignore

import crib
from crib import exceptions
from crib.domain.property import Property


class PropertyRepo(metaclass=abc.ABCMeta):
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
        return {}

    @abc.abstractmethod
    def insert(self, prop: Property) -> None:
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
    def count(self) -> int:
        pass


class MemoryPropertyRepo(PropertyRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._storage: Dict[str, Property] = {}

    def insert(self, prop: Property) -> None:
        if prop["id"] in self._storage:
            raise exceptions.DuplicateProperty(prop)
        self._storage[prop["id"]] = prop

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

    def count(self) -> int:
        return len(self._storage)


class MongoPropertyRepo(PropertyRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._client = pymongo.MongoClient(**self.config["connection"])
        self._db = self._client[self.config["database"]]

    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        return {
            "connection": {
                "type": "dict",
                "required": True,
                "schema": {
                    "host": {"type": "string", "required": True},
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                    "authSource": {"type": "string"},
                    "authMechanism": {"type": "string"},
                },
            },
            "database": {"type": "string", "required": True},
        }

    @property
    def _props(self):
        return self._db.properties

    def _to_prop(self, data: Dict[str, Any]) -> Property:
        data.pop("_id")
        return Property(data)

    def exists(self, identity: str) -> bool:
        return bool(self._props.find_one({"_id": identity}))

    def insert(self, prop: Property) -> None:
        p = dict(prop)
        p["_id"] = p["id"]
        try:
            self._props.insert_one(p)
        except pymongo.errors.DuplicateKeyError:
            raise exceptions.DuplicateProperty(p)

    def get(self, identity: str) -> Property:
        data = self._props.find_one({"_id": identity})
        if data is None:
            raise exceptions.EntityNotFound(identity)

        prop = self._to_prop(data)
        return prop

    def get_all(self) -> Iterable[Property]:
        for data in self._props.find():
            yield self._to_prop(data)

    def get_x(self, x) -> Iterable[Property]:
        for data in self._props.find().limit(x):
            yield self._to_prop(data)

    def delete(self, identity: str) -> None:
        result = self._props.delete_one({"_id": identity})
        if result.deleted_count == 0:
            raise exceptions.EntityNotFound(identity)

    def count(self) -> int:
        return self._props.count()


PR = TypeVar("PR", bound=PropertyRepo)
TPR = Type[PR]


@crib.hookimpl
def crib_add_property_repos() -> Iterable[TPR]:
    return [MemoryPropertyRepo, MongoPropertyRepo]
