from typing import List, Type, TypeVar

import pluggy  # type: ignore

from crib import config
from crib.repositories import directions as dirrepo
from crib.repositories import properties, user
from crib.services import directions

hookspec = pluggy.HookspecMarker("crib")


PR = TypeVar("PR", bound=properties.PropertyRepo)
TPR = Type[PR]
UR = TypeVar("UR", bound=user.UserRepo)
TUR = Type[UR]
DR = TypeVar("DR", bound=direpo.DirectionsRepo)
TDR = Type[DR]
DS = TypeVar("DS", bound=directions.DirectionsService)
TDS = Type[DS]


class CribSpec:
    @hookspec
    def crib_add_property_repos(self) -> List[TPR]:
        """Add property repo plugins

        :return: a list of PropertyRepos
        """
        return []

    @hookspec
    def crib_add_user_repos(self) -> List[TUR]:
        """Add user repo plugins

        :return: a list of UserRepos
        """
        return []

    @hookspec
    def crib_add_directions_repos(self) -> List[TDR]:
        """Add directions repo plugins

        :return: a list of DirectionsRepos
        """
        return []

    @hookspec
    def crib_add_config_loaders(self) -> List[config.AbstractConfigLoader]:
        """Add config loaders

        :return: a list of AbstractConfigLoader
        """
        return []

    @hookspec
    def crib_add_directions_services(self) -> List[TDS]:
        """Add DirectionsServices

        :return: a list of DirectionsService
        """
        return []


def _init_plugin_manager() -> pluggy.PluginManager:
    pm = pluggy.PluginManager("crib")
    pm.add_hookspecs(CribSpec)
    pm.load_setuptools_entrypoints("crib")
    pm.register(config)
    pm.register(properties)
    pm.register(user)
    pm.register(directions)
    pm.register(dirrepo)
    return pm


_plugin_manager = _init_plugin_manager()
hook = _plugin_manager.hook
