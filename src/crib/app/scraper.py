"""
Scraper application.
"""
import itertools
import logging

import cerberus

from crib import plugins
from crib.exceptions import ConfigError, DuplicateProperty, PluginNotFound

_log = logging.getLogger(__name__)


class Scrapp:
    _config_schema = {
        "scrapers": {"type": "list", "required": True},
        "repository": {
            "type": "dict",
            "schema": {"type": {"type": "string", "required": True}},
            "allow_unknown": True,
            "required": True,
        },
    }

    def __init__(self, config: dict):
        super().__init__()
        self.config = self._validate_config(config)
        self._hook = plugins.hook
        self._scraper_plugins = None
        self._scrapers = None
        self.repository = self._open_repository()

    def _validate_config(self, config):
        validator = cerberus.Validator(self._config_schema, allow_unknown=True)
        if not validator.validate(config):
            raise ConfigError(f"Invalid config", validator.errors)
        return validator.document

    def _open_repository(self):
        repo_config = self.config["repository"].copy()
        repo_type = repo_config.pop("type")
        repo_plugins = self._hook.crib_add_property_repos()
        for repo in itertools.chain(*repo_plugins):
            if repo.name() == repo_type:
                return repo(repo_config)
        raise PluginNotFound("Repository {repo_type} plugin not found")

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
            self._load_scrapers()
        return self._scrapers

    def _load_scrapers(self):
        scraper_config = self.config["scrapers"]
        self._scrapers = []
        for cfg in scraper_config:
            cfg = cfg.copy()
            name = cfg.pop("name")
            try:
                scraper = self.scraper_plugins[name]
            except KeyError:
                _log.error(f"Scraper not found {name}")
                continue

            try:
                self._scrapers.append(scraper(cfg))
            except ConfigError as exc:
                _log.error(f"{exc}")

    def scrape(self):
        for scraper in self.scrapers:
            for p in scraper.scrape():
                _log.debug(f"{scraper}: property scraped")
                try:
                    self.repository.insert(p)
                except DuplicateProperty:
                    pass
