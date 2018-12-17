"""
Property model
"""
from collections.abc import Mapping
from typing import Any, Dict, Iterator, List, Union

import cerberus  # type: ignore

from crib.exceptions import InvalidPropertyData


class Property(Mapping):
    schema: Dict[str, Dict[str, Union[str, Dict]]] = {
        "bedrooms": {"type": "integer", "required": True},
        "displayAddress": {"type": "string", "required": True},
        "featuredProperty": {"type": "boolean"},
        "feesApply": {"type": "boolean", "required": True},
        "feesApplyText": {"type": "string"},
        "firstVisibleDate": {"type": "datetime", "required": True},
        "id": {"type": "string", "required": True},
        "location": {
            "type": "dict",
            "schema": {
                "latitude": {"type": "float", "required": True},
                "longitude": {"type": "float", "required": True},
            },
            "required": True,
        },
        "price": {
            "type": "dict",
            "schema": {
                "amount": {"type": "integer", "required": True},
                "currencyCode": {"type": "string", "required": True},
                "frequency": {"type": "string", "required": True},
            },
            "required": True,
        },
        "propertyImages": {
            "type": "list",
            "schema": {"type": "string"},
            "required": True,
        },
        "floorplanImages": {
            "type": "list",
            "schema": {"type": "string"},
            "required": True,
        },
        "propertySubType": {"type": "string", "required": True},
        "propertyTypeFullDescription": {"type": "string", "required": True},
        "propertyUrl": {"type": "string", "required": True},
        "students": {"type": "boolean", "required": True},
        "summary": {"type": "string", "required": True},
        "transactionType": {"type": "string", "required": True},
        "keyFeatures": {"type": "list", "schema": {"type": "string"}, "required": True},
        "lettingInformation": {"type": "dict", "required": True},
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

    def __str__(self) -> str:
        return f"{self._storage}"
