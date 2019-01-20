"""
Crib application
"""
import itertools
from typing import IO, TYPE_CHECKING, Callable, Dict

from crib import config as _cfg
from crib import exceptions, plugin_loader

if TYPE_CHECKING:
    from crib.repositories.properties import PropertyRepo
    from crib.repositories.user import UserRepo
    from crib.services.directions import DirectionsService


def _load_plugin(config: Dict, config_section: str, hook: Callable):
    plugin_config = config[config_section].copy()
    plugin_type = plugin_config.pop("type")
    loaded_plugins = hook()
    for plugin in itertools.chain(*loaded_plugins):
        if plugin.name() == plugin_type:
            return plugin(plugin_config)
    raise exceptions.PluginNotFound(f"{plugin_type} plugin not found")


def get_property_repository(config: Dict) -> "PropertyRepo":
    return _load_plugin(
        config, "property_repository", plugin_loader.hook.crib_add_property_repos
    )


def get_user_repository(config: Dict) -> "UserRepo":
    return _load_plugin(
        config, "user_repository", plugin_loader.hook.crib_add_user_repos
    )


def get_direction_service(config: Dict) -> "DirectionsService":
    return _load_plugin(
        config, "directions_service", plugin_loader.hook.crib_add_directions_services
    )


def load_config(config: IO[str]) -> Dict:
    loaders = [
        l for loaders in plugin_loader.hook.crib_add_config_loaders() for l in loaders
    ]
    default = _cfg.load_default(loaders)
    user_cfg = _cfg.load(loaders, config)
    cfg = _cfg.merge_config(default, user_cfg)
    return cfg
