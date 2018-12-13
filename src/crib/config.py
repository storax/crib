"""
Config loader
"""
import abc
import itertools
import os

import yaml

import crib
from crib import exceptions


class AbstractConfigLoader(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def extensions(cls):
        return []

    @classmethod
    def can_handle(cls, cfgfile):
        _, ext = os.path.splitext(cfgfile.name)
        if not ext:
            return False

        ext = ext.lstrip(os.extsep)
        return any(ext == supported for supported in cls.extensions(cls))

    @abc.abstractmethod
    def load(self, cfginput):
        """Return the configuration

        Returns:
            dict.
        """
        pass


class YamlLoader(AbstractConfigLoader):
    def extensions(cls):
        return ["yml", "yaml"]

    def load(self, cfginput):
        return yaml.load(cfginput)


def load(loaders, config):
    if not config:
        return {}
    for loader in loaders:
        if loader.can_handle(config):
            return loader.load(config)

    supported = [ext for loader in loaders for ext in loader.extensions()]
    errors = {"Given": config.name, "Supported": supported}
    raise exceptions.ConfigError("Unknown config format extension.", errors)


@crib.hookimpl
def crib_add_config_loaders():
    return [YamlLoader]
