"""
Config loader
"""
import abc
import itertools
import os
from typing import IO, Any, Dict, List

import yaml

import crib
from crib import exceptions


class AbstractConfigLoader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def extensions(self) -> List[str]:
        return []

    def can_handle(self, cfgfile: IO[str]) -> bool:
        _, ext = os.path.splitext(cfgfile.name)
        if not ext:
            return False

        ext = ext.lstrip(os.extsep)
        return any(ext == supported for supported in self.extensions())

    @abc.abstractmethod
    def load(self, cfginput: IO[str]) -> Dict[str, Any]:
        """Return the configuration

        Returns:
            dict.
        """
        pass


class YamlLoader(AbstractConfigLoader):
    def extensions(self) -> List[str]:
        return ["yml", "yaml"]

    def load(self, cfginput: IO[str]) -> Dict[str, Any]:
        return yaml.load(cfginput)


def load(loaders: List[AbstractConfigLoader], config: IO[str]) -> Dict[str, Any]:
    if not config:
        return {}
    for loader in loaders:
        if loader.can_handle(config):
            return loader.load(config)

    supported = [ext for loader in loaders for ext in loader.extensions()]
    errors = {"Given": config.name, "Supported": supported}
    raise exceptions.ConfigError("Unknown config format extension.", errors)


@crib.hookimpl
def crib_add_config_loaders() -> List[AbstractConfigLoader]:
    return [YamlLoader()]
