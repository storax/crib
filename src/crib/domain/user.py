"""
User model
"""
from collections.abc import Mapping
from typing import Any, Dict, Iterator, Union

import cerberus  # type: ignore

from crib.exceptions import InvalidUserData


class User(Mapping):
    schema: Dict[str, Dict[str, Union[str, Dict]]] = {
        "username": {"type": "string", "required": True},
        "password": {"type": "string", "required": True},
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        data = dict(*args, **kwargs)
        self._storage = self._validate(data)

    def _validate(self, data: Dict) -> Dict[str, Any]:
        validator = cerberus.Validator(self.schema)
        if not validator.validate(data):
            raise InvalidUserData(f"Invalid user data", validator.errors)
        return validator.document

    def __getitem__(self, key: str):
        return self._storage[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._storage)

    def __len__(self) -> int:
        return len(self._storage)

    def __str__(self) -> str:
        return f"{self._storage}"
