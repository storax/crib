import logging

from crib import exceptions, injection, plugins

log = logging.getLogger(__name__)


class PropertyService(plugins.Plugin):
    directions_service = injection.Dependency()
    property_repository = injection.Dependency()

    def find(self, max_price=None, favorite=None, area=None, limit=None):
        try:
            props = list(
                self.property_repository.find(
                    max_price=max_price, favorite=favorite, area=area, limit=limit
                )
            )
        except exceptions.InvalidQuery as err:
            raise ValueError(str(err))

        return props

    async def to_work(self, prop_id: str, mode: str, refresh: bool = False):
        prop = self.property_repository.get(prop_id)

        if prop.toWork and not refresh:
            return prop.toWork

        origin = prop.location

        route = await self.directions_service.to_work(origin, mode)

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

    def clear_properties(self, banned=False, favorites=False):
        self.property_repository.clear(banned=banned, favorites=favorites)

    def save_search_area(self, name: str, geojson):
        self.property_repository.set_search_area(name, geojson)

    def get_search_areas(self):
        return self.property_repository.get_search_areas()
