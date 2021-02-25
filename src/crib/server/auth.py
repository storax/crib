from typing import Set

from flask_jwt_extended import (  # type: ignore
    JWTManager,
    create_access_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from quart import Blueprint, current_app, jsonify, request  # type: ignore

bp = Blueprint("auth", __name__, url_prefix="/auth")

blacklist: Set = set()

jwt = JWTManager()


def init_app(app):
    app.register_blueprint(bp)
    jwt.init_app(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_header["jti"]
    return jti in blacklist


@bp.route("/login", methods=["POST"], endpoint="login")
async def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    json = await request.json
    username = json.get("username", None)
    password = json.get("password", None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    tokens = current_app.auth_service.get_tokens(username, password)
    if not tokens:
        invalid_msg = jsonify({"msg": "Invalid Credentials"}), 401
        return invalid_msg

    return jsonify(tokens), 200


@bp.route("/refresh", methods=["POST"], endpoint="refresh")
@jwt_required(refresh=True)
async def refresh():
    current_user = get_jwt_identity()
    ret = {"access_token": create_access_token(identity=current_user)}
    return jsonify(ret), 200


# Endpoint for revoking the current users access token
@bp.route("/logout", methods=["DELETE"], endpoint="logout")
@jwt_required
async def logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


# Endpoint for revoking the current users refresh token
@bp.route("/logout2", methods=["DELETE"], endpoint="logout2")
@jwt_required(refresh=True)
async def logout2():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200
