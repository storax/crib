"""
Server for crib.
"""
import os

import quart.flask_patch  # noqa: F401
from quart import Quart
from quart_cors import cors  # type: ignore

from crib import injection

from . import auth, directions, properties, scrape


class Flask(injection.Component, Quart):
    _crib_config = injection.Infrastructure("config")
    user_repository = injection.Dependency()
    property_repository = injection.Dependency()
    directions_service = injection.Dependency()
    directions_repository = injection.Dependency()
    property_service = injection.Dependency()
    auth_service = injection.Dependency()
    scrape_service = injection.Dependency()

    def __init__(self, *args, **kwargs):
        self._name = None
        super(Flask, self).__init__(*args, **kwargs)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


def create_app(container):
    # create and configure the app
    app = Flask("server", container, __name__)
    app.config.from_mapping(
        JWT_SECRET_KEY="dev",
        JWT_BLACKLIST_ENABLED=True,
        JWT_BLACKLIST_TOKEN_CHECKS=["access", "refresh"],
    )
    app = cors(app)
    app.config.from_mapping(app._crib_config)

    app.register_blueprint(properties.bp)
    app.register_blueprint(directions.bp)
    app.register_blueprint(scrape.bp)
    auth.init_app(app)

    return app
