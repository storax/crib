"""
Browse scraped properties
"""
import itertools
from typing import Any, Dict, Iterable

import cerberus  # type: ignore

from crib import exceptions, plugins
from crib.domain.property import Property
from crib.repositories.properties import PropertyRepo


class Browser:
    _config_schema: Dict[str, Any] = {
        "repository": {
            "type": "dict",
            "schema": {"type": {"type": "string"}},
            "allow_unknown": True,
        }
    }

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__()
        self.config = self._validate_config(config)
        self._hook = plugins.hook
        self.repository: PropertyRepo = self._open_repository()

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        validator = cerberus.Validator(self._config_schema, allow_unknown=True)
        if not validator.validate(config):
            raise exceptions.ConfigError(f"Invalid config", validator.errors)
        return validator.document

    def _open_repository(self) -> PropertyRepo:
        repo_config = self.config["repository"].copy()
        repo_type = repo_config.pop("type")
        repo_plugins = self._hook.crib_add_property_repos()
        for repo in itertools.chain(*repo_plugins):
            if repo.name() == repo_type:
                return repo(repo_config)
        raise exceptions.PluginNotFound("Repository {repo_type} plugin not found")

    def find(self, query) -> Iterable[Property]:
        for prop in self.repository._props.find(query):
            yield prop
