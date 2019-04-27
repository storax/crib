import pytest  # type: ignore

from crib import app, config, injection


def make_app(cfg=None):
    cfg = cfg or {}

    class Container(app.AppContainer):
        config = injection.SingletonProvider(config.MemoryConfiguration)
        config_overrides = injection.ObjectProvider(cfg)

    return Container


@pytest.fixture
def testapp():
    return make_app(
        {
            "property_repository": {"type": "MemoryPropertyRepo"},
            "user_repository": {"type": "MemoryUserRepo"},
            "directions_repository": {"type": "MemoryDirectionsRepo"},
        }
    )
