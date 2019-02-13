"""
Property data
"""
from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore

from crib import exceptions

bp = Blueprint("properties", __name__, url_prefix="/properties")


@bp.route("/find", methods=("POST",))
@jwt_required
def find():
    json = request.json
    limit = json.get("limit", 100)
    order_by = json.get("order_by", {})
    try:
        props = [
            dict(p)
            for p in current_app.property_service.find(order_by=order_by, limit=limit)
        ]
    except ValueError as err:
        return jsonify({"msg": str(err)}), 400

    return jsonify(props)


@bp.route("/to_work", methods=("GET",))
@jwt_required
def to_work():
    args = request.args
    prop_id = args.get("prop_id")
    mode = args.get("mode")
    refresh = args.get("refresh", False)
    if not prop_id:
        return jsonify({"msg": "prop_id missing"}), 400
    if not mode:
        return jsonify({"msg": "mode missing"}), 400

    try:
        route = current_app.property_service.to_work(prop_id, mode, refresh=refresh)
    except exceptions.EntityNotFound as err:
        return jsonify({"msg": str(err)}), 400

    return jsonify(route)
