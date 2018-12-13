"""
Simple crud repository base class
"""
import abc

import cerberus
import pymongo

import crib
from crib import exceptions
from crib.domain.property import Property


class PropertyRepo(metaclass=abc.ABCMeta):
    def __init__(self, config):
        super().__init__()
        schema = self.config_schema()
        validator = cerberus.Validator(schema)
        if not validator.validate(config):
            raise exceptions.ConfigError(
                f"Invalid config for {self.name()}", validator.errors
            )
        self.config = validator.document

    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def config_schema(cls):
        return {}

    @abc.abstractmethod
    def insert(self, prop):
        pass

    @abc.abstractmethod
    def get(self, identity: str):
        pass

    @abc.abstractmethod
    def get_all(self):
        pass

    @abc.abstractmethod
    def delete(self, identity: str):
        pass

    @abc.abstractmethod
    def count(self):
        pass


class MemoryPropertyRepo(PropertyRepo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._storage = {}

    def insert(self, prop):
        if prop["id"] in self._storage:
            raise exceptions.DuplicateProperty(prop)
        self._storage[prop["id"]] = prop

    def get(self, identity: str):
        try:
            return self._storage[identity]
        except KeyError:
            raise exceptions.EntityNotFound(identity)

    def get_all(self):
        for p in self._storage.values():
            yield p

    def delete(self, identity: str):
        try:
            del self._storage[identity]
        except KeyError:
            raise exceptions.EntityNotFound(identity)

    def count(self):
        return len(self._storage)


class MongoPropertyRepo(PropertyRepo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = pymongo.MongoClient(**self.config["connection"])
        self._db = self._client[self.config["database"]]

    @classmethod
    def config_schema(cls):
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

    def _to_prop(self, data):
        data.pop("_id")
        return Property(data)

    def insert(self, prop):
        prop = dict(prop)
        prop["_id"] = prop["id"]
        try:
            self._props.insert_one(prop)
        except pymongo.errors.DuplicateKeyError:
            raise exceptions.DuplicateProperty(prop)

    def get(self, identity: str):
        data = self._props.find_one({"_id": identity})
        prop = self._to_prop(data)
        if prop is None:
            raise EntityNotFound(identity)
        return prop

    def get_all(self):
        for data in self._props.find():
            yield self._to_prop(data)

    def delete(self, identity: str):
        result = self._props.delete_one({"_id": identity})
        if result.deleted_count == 0:
            raise EntityNotFound(identity)

    def count(self):
        return self._props.count()


@crib.hookimpl
def crib_add_property_repos():
    return [MemoryPropertyRepo, MongoPropertyRepo]
