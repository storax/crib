"""
Mixin class for MongoDB repositories
"""
from typing import Any, Dict

import pymongo

from crib import exceptions, plugins


class MongoRepo(plugins.Plugin):
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
    def db(self):
        return self._db
