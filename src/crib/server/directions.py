"""
Property data
"""
from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore

from crib.services import directions

bp = Blueprint("directions", __name__, url_prefix="/directions")


@bp.route("/to_work", methods=("GET",))
@jwt_required
def to_work():
    args = request.args.copy()
    if "origin" not in args:
        return jsonify({"msg": "origin missing"}), 400
    if "mode" not in args:
        return jsonify({"msg": "mode missing"}), 400

    orig = args["origin"].split(",")

    origin = directions.Location(orig[0], orig[1])
    routes = current_app.directions_service.to_work(origin, args["mode"])
    return jsonify(routes)
