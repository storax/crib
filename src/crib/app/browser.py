"""
Browse scraped properties
"""
import itertools

import cerberus

from crib import exceptions, plugins


class Browser:
    _config_schema = {
        "repository": {
            "type": "dict",
            "schema": {"type": {"type": "string"}},
            "allow_unknown": True,
        }
    }

    def __init__(self, config: dict):
        super().__init__()
        self.config = self._validate_config(config)
        self._hook = plugins.hook
        self.repository = self._open_repository()

    def _validate_config(self, config):
        validator = cerberus.Validator(self._config_schema, allow_unknown=True)
        if not validator.validate(config):
            raise exceptions.ConfigError(f"Invalid config", validator.errors)
        return validator.document

    def _open_repository(self):
        repo_config = self.config["repository"].copy()
        repo_type = repo_config.pop("type")
        repo_plugins = self._hook.crib_add_property_repos()
        for repo in itertools.chain(*repo_plugins):
            if repo.name() == repo_type:
                return repo(repo_config)
        raise exceptions.PluginNotFound("Repository {repo_type} plugin not found")

    def find(self, query):
        for prop in self.repository._props.find(query):
            yield prop
