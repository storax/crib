from typing import List, Type, TypeVar

import pluggy  # type: ignore

from crib import config, exceptions, plugins
from crib.injection import AbstractProvider, Component, Container
from crib.repositories import directions as dirrepo
from crib.repositories import properties, user
from crib.services import directions

hookspec = pluggy.HookspecMarker("crib")


PR = TypeVar("PR", bound=properties.PropertyRepo)
TPR = Type[PR]
UR = TypeVar("UR", bound=user.UserRepo)
TUR = Type[UR]
DR = TypeVar("DR", bound=dirrepo.DirectionsRepo)
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


class PluginsProvider(AbstractProvider):
    """Provides a list of components through a plugin hook.
    """

    def __init__(self, hook):
        super().__init__()
        self._hook = hook
        self._plugins = None

    def __get__(self, container: Container, T) -> List[Component]:
        if self._plugins is None:
            self._plugins = self._load_plugins()
        return self._plugins

    def _load_plugins(self) -> List[Component]:
        plugins = [plugin for plugins in self._hook() for plugin in plugins]
        return plugins


class ConfiguredPluginProvider(PluginsProvider):
    """Provides a plugin which matches the 'type' in the configuration.

    This requires a feature called 'config'.
    """

    def __init__(self, hook):
        super().__init__(hook)
        self._component = None

    def __get__(self, container: Container, T) -> plugins.PluginComponent:
        if self._component is None:
            plugins = super().__get__(container, T)
            self._component = self._load_component(container, plugins)
        return self._component

    def _load_component(
        self, container: Container, plugins: List[Component]
    ) -> Component:
        plugin_config = container.config[self.feature]
        plugin_type = plugin_config["type"]
        for plugin in plugins:
            if plugin.plugin_type() == plugin_type:
                return plugin(self.feature, container)
        raise exceptions.PluginNotFound(f"{plugin_type} plugin not found")
