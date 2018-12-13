import pluggy

from crib import config
from crib.repositories import properties
from crib.scraper.plugins import rightmove

hookspec = pluggy.HookspecMarker("crib")


class CribSpec:
    @hookspec
    def crib_add_scrapers():
        """Add scraper plugins

        :return: a list of scrapers
        """

    @hookspec
    def crib_add_property_repos():
        """Add scraper plugins

        :return: a list of PropertyRepos
        """

    @hookspec
    def crib_add_config_loaders():
        """Add config loaders

        :return: a list or AbstractConfigLoader
        """


def _init_plugin_manager():
    pm = pluggy.PluginManager("crib")
    pm.add_hookspecs(CribSpec)
    pm.load_setuptools_entrypoints("crib")
    pm.register(config)
    pm.register(rightmove)
    pm.register(properties)
    return pm


_plugin_manager = _init_plugin_manager()
hook = _plugin_manager.hook
