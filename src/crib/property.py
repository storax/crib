"""
Property model
"""
from collections.abc import Mapping

import cerberus


class Property(Mapping):
    schema = {
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

    def __init__(self, *args, **kwargs):
        super().__init__()
        data = dict(*args, **kwargs)
        self._storage = self._validate(data)

    def _validate(self, data):
        validator = cerberus.Validator(self.schema)
        if not validator.validate(data):
            raise InvalidPropertyData(f"Invalid property data", validator.errors)
        return validator.document

    def __getitem__(self, key):
        return self._storage[key]

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)


class InvalidPropertyData(Exception):
    def __init__(self, msg, errors):
        super().__init__(msg, errors)
        self.msg = msg
        self.errors = errors

    def __str__(self):
        errors = "\n".join(
            f"\t{field}: {reasons}" for field, reasons in self.errors.items()
        )
        return f"{self.msg}:\n{errors}"
