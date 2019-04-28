"""
Model base class
"""
from datetime import datetime
from typing import Dict, Type, TypeVar

import attr
import cattr  # type: ignore

from crib.exceptions import InvalidData

converter = cattr.Converter()
converter.register_unstructure_hook(datetime, lambda dt: dt)
converter.register_structure_hook(datetime, lambda ts, _: ts)

T = TypeVar("T", bound="Model")


@attr.s
class Model:
    @classmethod
    def fromdict(cls: Type[T], data: Dict) -> T:
        try:
            return converter.structure(data, cls)
        except (ValueError, TypeError) as err:
            raise InvalidData("Invalid data", {"unknown": str(err)})

    def asdict(self) -> Dict:
        return converter.unstructure(self)

    def replace(self: T, **changes) -> T:
        return attr.evolve(self, **changes)
