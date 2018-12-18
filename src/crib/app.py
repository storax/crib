"""
Crib application
"""
import itertools
from typing import IO, TYPE_CHECKING, Dict

from crib import config as _cfg
from crib import exceptions, plugins

if TYPE_CHECKING:
    from crib.repositories.properties import PropertyRepo
    from crib.repositories.users import UserRepo


def get_property_repository(config: Dict) -> "PropertyRepo":
    repo_config = config["property_repository"].copy()
    repo_type = repo_config.pop("type")
    repo_plugins = plugins.hook.crib_add_property_repos()
    for repo in itertools.chain(*repo_plugins):
        if repo.name() == repo_type:
            return repo(repo_config)
    raise exceptions.PluginNotFound(f"Repository {repo_type} plugin not found")


def get_user_repository(config: Dict) -> "UserRepo":
    repo_config = config["user_repository"].copy()
    repo_type = repo_config.pop("type")
    repo_plugins = plugins.hook.crib_add_user_repos()
    for repo in itertools.chain(*repo_plugins):
        if repo.name() == repo_type:
            return repo(repo_config)
    raise exceptions.PluginNotFound(f"Repository {repo_type} plugin not found")


def load_config(config: IO[str]) -> Dict:
    loaders = [l for loaders in plugins.hook.crib_add_config_loaders() for l in loaders]
    cfg = _cfg.load(loaders, config)
    return cfg
