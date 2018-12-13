import pluggy

from crib.scraper.plugins import rightmove
from crib.repositories import properties

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


def _init_plugin_manager():
    pm = pluggy.PluginManager("crib")
    pm.add_hookspecs(CribSpec)
    pm.load_setuptools_entrypoints("crib")
    pm.register(rightmove)
    pm.register(properties)
    return pm


_plugin_manager = _init_plugin_manager()
hook = _plugin_manager.hook
