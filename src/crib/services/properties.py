import logging
from typing import Dict

from crib import exceptions, injection, plugins

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

        if prop.toWork and not refresh:
            return prop.toWork

        origin = prop.location

        route = self.directions_service.to_work(origin, mode)

        prop = prop.replace(toWork=route)
        self.property_repository.update(prop)

        return route

    def favorite(self, prop_id: str, val: bool):
        prop = self.property_repository.get(prop_id)
        if prop.favorite != val:
            prop = prop.replace(favorite=val)
            self.property_repository.update(prop)

    def ban(self, prop_id: str, val: bool):
        prop = self.property_repository.get(prop_id)
        if prop.banned != val:
            prop = prop.replace(banned=val)
            self.property_repository.update(prop)
