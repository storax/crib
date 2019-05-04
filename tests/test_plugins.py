"""Test for plugins.
"""
from typing import Any, Dict

import pytest  # type: ignore

from crib import exceptions, injection
from crib.plugins import Plugin


class NoConfig(Plugin):
    pass


class WithConfig(Plugin):
    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        return {"foo": {"type": "string", "required": True}}


@pytest.fixture
def testapp():
    class Container:
        config = injection.ObjectProvider(
            {"withconfig": {"foo": "test", "type": "WithConfig"}, "noconfig": {}}
        )
        withconfig = injection.SingletonProvider(WithConfig)
        noconfig = injection.SingletonProvider(NoConfig)

    return Container()


def test_config(testapp):
    """Test that the config is properly loaded."""
    assert testapp.withconfig.config["foo"] == "test"


def test_plugin_type(testapp):
    """Test getting the plugin type."""
    assert testapp.noconfig.plugin_type() == "NoConfig"


def test_invalid_config():
    """Test loading an invalid config."""

    class Container:
        config = injection.ObjectProvider({"withconfig": {"bar": "test"}})
        withconfig = injection.SingletonProvider(WithConfig)

    ct = Container()

    with pytest.raises(exceptions.ConfigError):
        ct.withconfig


def test_type_is_stripped_from_config(testapp):
    """Test that the type config is stripped."""
    assert "type" not in testapp.withconfig.config
