"""
Config loader
"""
import abc

import yaml


class AbstractConfigLoader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(self, cfginput):
        """Return the configuration

        Returns:
            dict.
        """
        pass


class YamlLoader(AbstractConfigLoader):
    def load(self, cfginput):
        return yaml.load(cfginput)
