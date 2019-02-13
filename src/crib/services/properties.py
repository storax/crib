import logging
from typing import Dict

from crib import exceptions, injection, plugins
from crib.domain.direction import Location
from crib.domain.property import Property

log = logging.getLogger(__name__)


class PropertyService(plugins.Plugin):
    directions_service = injection.Dependency()
    property_repository = injection.Dependency()

    def find(self, order_by: Dict[str, int] = None, limit=100):
        order_by = order_by or {}
        try:
            props = list(self.property_repository.find(order_by=order_by, limit=limit))
        except exceptions.InvalidQuery as err:
            raise ValueError(str(err))

        return props

    def to_work(self, prop_id: str, mode: str, refresh: bool = False):
        prop = self.property_repository.get(prop_id)

        if prop["toWork"] and not refresh:
            return prop["toWork"]

        origin = Location(**prop["location"])

        route = self.directions_service.to_work(origin, mode)

        prop_d = dict(prop)
        prop_d["toWork"] = route

        self.property_repository.update(Property(prop_d))

        return route
