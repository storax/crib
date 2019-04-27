"""
Server for crib.
"""
import os

import flask  # type: ignore
from flask_cors import CORS  # type: ignore

from crib import injection

from . import auth, directions, properties


class Flask(injection.Component, flask.Flask):
    _crib_config = injection.Infrastructure("config")
    user_repository = injection.Dependency()
    property_repository = injection.Dependency()
    directions_service = injection.Dependency()
    directions_repository = injection.Dependency()
    property_service = injection.Dependency()
    auth_service = injection.Dependency()


def create_app(container):
    # create and configure the app
    app = Flask("server", container, __name__)
    app.config.from_mapping(
        JWT_SECRET_KEY="dev",
        JWT_BLACKLIST_ENABLED=True,
        JWT_BLACKLIST_TOKEN_CHECKS=["access", "refresh"],
    )
    CORS(app)
    app.config.from_mapping(app._crib_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(properties.bp)
    app.register_blueprint(directions.bp)
    auth.init_app(app)

    return app
