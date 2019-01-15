"""
Server for crib.
"""
import os

import flask
from flask_cors import CORS

from . import auth, directions, properties, spa


def create_app(config):
    # create and configure the app
    app = flask.Flask(__name__)
    app.config.from_mapping(
        JWT_SECRET_KEY="dev",
        JWT_BLACKLIST_ENABLED=True,
        JWT_BLACKLIST_TOKEN_CHECKS=["access", "refresh"],
    )
    cors = CORS(app)
    app.config.from_mapping(config["server"])

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(properties.bp)
    app.register_blueprint(directions.bp)
    app.register_blueprint(spa.bp)
    app.add_url_rule("/", endpoint="spa.index")
    auth.init_app(app)

    return app
