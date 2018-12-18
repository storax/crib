"""
Server for crib.
"""
import os

import flask

from . import auth, browse, properties


def create_app(config):
    # create and configure the app
    app = flask.Flask(__name__)
    app.config.from_mapping(SECRET_KEY="dev")

    app.config.from_mapping(config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(auth.bp)
    app.register_blueprint(browse.bp)
    app.register_blueprint(properties.bp)
    app.add_url_rule("/", endpoint="index")

    return app
