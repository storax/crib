"""
Model base class
"""
from collections.abc import Mapping
from typing import Any, Callable, Dict, Iterator, Union

import cerberus  # type: ignore

from crib.exceptions import InvalidData

SchemaType = Dict[str, Dict[str, Union[str, bool, Dict, Callable]]]


class Model(Mapping):
    schema: SchemaType = {}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        data = dict(*args, **kwargs)
        self._storage = self._validate(data)

    def _validate(self, data: Dict) -> Dict[str, Any]:
        validator = cerberus.Validator(self.schema)
        if not validator.validate(data):
            raise InvalidData(f"Invalid data", validator.errors)
        return validator.document

    def __getitem__(self, key: str):
        return self._storage[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._storage)

    def __len__(self) -> int:
        return len(self._storage)

    def __str__(self) -> str:
        return f"{self._storage}"
