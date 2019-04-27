"""
Model base class
"""
from datetime import datetime

import attr
import cattr  # type: ignore

from crib.exceptions import InvalidData

converter = cattr.Converter()
converter.register_unstructure_hook(datetime, lambda dt: dt)
converter.register_structure_hook(datetime, lambda ts, _: ts)


@attr.s
class Model:
    @classmethod
    def fromdict(cls, data):
        try:
            return converter.structure(data, cls)
        except (ValueError, TypeError) as err:
            raise InvalidData("Invalid data", {"unknown": str(err)})

    def asdict(self):
        return converter.unstructure(self)
