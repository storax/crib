"""
Property model
"""
from collections.abc import Mapping
from typing import Any, Dict, Iterator, List, Union

import cerberus  # type: ignore

from crib.exceptions import InvalidPropertyData


class Property(Mapping):
    schema: Dict[str, Dict[str, Union[str, Dict]]] = {
        "bedrooms": {"type": "integer"},
        "displayAddress": {"type": "string"},
        "featuredProperty": {"type": "boolean"},
        "feesApply": {"type": "boolean"},
        "feesApplyText": {"type": "string"},
        "firstVisibleDate": {"type": "datetime"},
        "id": {"type": "string"},
        "location": {
            "type": "dict",
            "schema": {"latitude": {"type": "float"}, "longitude": {"type": "float"}},
        },
        "price": {
            "type": "dict",
            "schema": {
                "amount": {"type": "integer"},
                "currencyCode": {"type": "string"},
                "frequency": {"type": "string"},
            },
        },
        "propertyImages": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {"order": {"type": "integer"}, "url": {"type": "string"}},
            },
        },
        "propertySubType": {"type": "string"},
        "propertyTypeFullDescription": {"type": "string"},
        "propertyUrl": {"type": "string"},
        "students": {"type": "boolean"},
        "summary": {"type": "string"},
        "transactionType": {"type": "string"},
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        data = dict(*args, **kwargs)
        self._storage = self._validate(data)

    def _validate(self, data: Dict) -> Dict[str, Any]:
        validator = cerberus.Validator(self.schema)
        if not validator.validate(data):
            raise InvalidPropertyData(f"Invalid property data", validator.errors)
        return validator.document

    def __getitem__(self, key: str):
        return self._storage[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._storage)

    def __len__(self) -> int:
        return len(self._storage)
