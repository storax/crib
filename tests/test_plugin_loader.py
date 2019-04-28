"""Test for plugin loaders.
"""
import gc

import pytest

from crib import exceptions
from crib.plugin_loader import PluginsProvider

from .conftest import make_app


def test_loading(testapp):
    """Test loading a plugin."""
    repo = testapp.property_repository
    assert repo.plugin_type() == "MemoryPropertyRepo"

    repo2 = testapp.property_repository
    assert repo is repo2


def test_plugin_not_found():
    """Test trying to load an unkown plugin."""
    testapp = make_app({"property_repository": {"type": "ThisPluginDoesNotExist"}})()

    with pytest.raises(exceptions.PluginNotFound):
        repo = testapp.property_repository


def test_plugins_provider_uninitialized():
    """Test accessing a plugin provider on a class.
    """
    testapp = make_app()
    assert isinstance(testapp.config_loaders, PluginsProvider)


def test_plugins_provider_cache(testapp):
    """Test accessing plugins multiple times.
    """
    plugins = testapp.config_loaders
    plugins2 = testapp.config_loaders
    assert plugins is plugins2


def test_plugins_provider_cache_per_instance(testapp):
    """Test plugins cache is per container instance.
    """
    testapp2 = make_app()()
    plugins = testapp.config_loaders
    plugins2 = testapp2.config_loaders
    assert plugins is not plugins2


def test_plugins_provider_cache_weakref(testapp):
    """Test plugins cache doesn't cause memory leaks.
    """
    container = make_app()
    testapp2 = container()
    plugins = testapp2.config_loaders
    gc.collect()
    assert testapp2 in container.config_loaders._plugins
    assert len(container.config_loaders._plugins.keyrefs()) == 2
    del testapp2
    gc.collect()
    assert len(container.config_loaders._plugins.keyrefs()) == 1
