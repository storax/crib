"""
Config loader
"""
import abc
import io
import os
from typing import IO, Any, Dict, List

import chardet  # type: ignore
import yaml
from pkg_resources import Requirement, resource_string

import crib
from crib import exceptions, injection


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
        return yaml.safe_load(cfginput)


def _load(loaders: List[AbstractConfigLoader], config: IO[str]) -> Dict[str, Any]:
    if not config:
        return {}
    for loader in loaders:
        if loader.can_handle(config):
            return loader.load(config)

    supported = [ext for loader in loaders for ext in loader.extensions()]
    errors = {"Given": config.name, "Supported": supported}
    raise exceptions.ConfigError("Unknown config format extension.", errors)


def _default_config() -> IO[str]:
    req = Requirement.parse("crib")
    content_bytes = resource_string(req, "crib/resources/config.yaml")
    try:
        contents = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        detected_info: Dict = chardet.detect(content_bytes)
        contents = content_bytes.decode(detected_info["encoding"])

    default_config = io.StringIO(contents)
    default_config.name = "config.yaml"
    return default_config


def _load_default(loaders: List[AbstractConfigLoader]) -> Dict:
    default_config = _default_config()
    cfg = _load(loaders, default_config)
    return cfg


def _merge_config(default: Dict, override: Dict) -> Dict:
    config = {s: cfg.copy() for s, cfg in default.items()}
    for override_section, configuration in override.items():
        section = config.setdefault(override_section, {})
        section.update(configuration)
    return config


class DefaultConfiguration(injection.Component):
    """Default configuration of crib."""

    config_loaders = injection.Dependency()

    def __init__(self, name, container):
        super().__init__(name, container)
        self._cfg = None

    def __getitem__(self, key):
        if self._cfg is None:
            self._cfg = self.load()
        return self._cfg.get(key, {})

    def load(self):
        default = _load_default(self.config_loaders)
        user_cfg = self.load_usercfg()
        cfg = _merge_config(default, user_cfg)
        return cfg

    def load_usercfg(self):
        return {}


class LoadedConfiguration(DefaultConfiguration):
    """Configuration which is loaded through a config loader component."""

    config_file = injection.Dependency()

    def load_usercfg(self):
        if self.config_file:
            with open(self.config_file, "r") as fp:
                return _load(self.config_loaders, fp)
        else:
            return {}


class MemoryConfiguration(DefaultConfiguration):
    """Canned config which is merged with the default config."""

    config_overrides = injection.Dependency()

    def load_usercfg(self):
        return self.config_overrides


@crib.hookimpl
def crib_add_config_loaders() -> List[AbstractConfigLoader]:
    return [YamlLoader()]
