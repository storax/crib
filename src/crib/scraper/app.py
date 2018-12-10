"""
Scraper application.
"""
import itertools
import logging

import pluggy

from crib import hookspecs
from .plugins import rightmove


_log = logging.getLogger(__name__)


def _get_plugin_manager():
    pm = pluggy.PluginManager("crib")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("crib")
    pm.register(rightmove)
    return pm


class Scrapp():
    def __init__(self, config :dict):
        super().__init__()
        self.config = config
        self._hook = _get_plugin_manager().hook
        self._scraper_plugins = None
        self._scrapers = None

    @property
    def scraper_plugins(self):
        if self._scraper_plugins is None:
            results = self._hook.crib_add_scrapers()
            plugs = {}
            for plug in itertools.chain(*results):
                plugs[plug.name()] = plug
            self._scraper_plugins = plugs
        return self._scraper_plugins

    @property
    def scrapers(self):
        if self._scrapers is None:
            self.load_scrapers()
        return self._scrapers

    def load_scrapers(self):
        scraper_config = self.config.get('scrapers', [])
        self._scrapers = []
        for cfg in scraper_config:
            cfg = cfg.copy()
            name = cfg.pop('name')
            try:
                scraper = self.scraper_plugins[name]
            except KeyError:
                _log.error(f'Scraper not found {name}')
            else:
                self._scrapers.append(scraper(cfg))
