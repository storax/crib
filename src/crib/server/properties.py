"""
Property data
"""
from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore

from crib import exceptions

bp = Blueprint("properties", __name__, url_prefix="/properties")


@bp.route("/find", methods=("POST",))
@jwt_required
def find(order_by=None,):
    json = request.json
    limit = json.get("limit", 100)
    order_by = json.get("order_by", {})
    try:
        props = [
            dict(p) for p in current_app.prop_repo.find(order_by=order_by, limit=limit)
        ]
    except exceptions.InvalidQuery as err:
        return jsonify({"msg": str(err)}), 400

    return jsonify(props)
