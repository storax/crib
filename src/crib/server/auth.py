from typing import Set

from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import (  # type: ignore
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_raw_jwt,
    jwt_refresh_token_required,
    jwt_required,
)
from werkzeug.security import (  # type: ignore
    check_password_hash,
    generate_password_hash,
)

from crib import exceptions
from crib.domain.user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

blacklist: Set = set()

jwt = JWTManager()


def init_app(app):
    app.register_blueprint(bp)
    jwt.init_app(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token["jti"]
    return jti in blacklist


@bp.route("/login", methods=("POST",))
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    tokens = current_app.auth_service.get_tokens(username, password)
    if not tokens:
        invalid_msg = jsonify({"msg": "Invalid Credentials"}), 401
        return invalid_msg

    return jsonify(tokens, 200)


@bp.route("/refresh", methods=("POST",))
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {"access_token": create_access_token(identity=current_user)}
    return jsonify(ret), 200


# Endpoint for revoking the current users access token
@bp.route("/logout", methods=("DELETE",))
@jwt_required
def logout():
    jti = get_raw_jwt()["jti"]
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


# Endpoint for revoking the current users refresh token
@bp.route("/logout2", methods=("DELETE",))
@jwt_refresh_token_required
def logout2():
    jti = get_raw_jwt()["jti"]
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200
