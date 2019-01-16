"""
Property data
"""
from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore

from crib import exceptions
from crib.domain.property import Property
from crib.services import directions

bp = Blueprint("directions", __name__, url_prefix="/directions")


@bp.route("/to_work", methods=("GET",))
@jwt_required
def to_work():
    args = request.args.copy()
    if "prop_id" not in args:
        return jsonify({"msg": "prop_id missing"}), 400
    if "mode" not in args:
        return jsonify({"msg": "mode missing"}), 400

    try:
        prop = current_app.prop_repo.get(args["prop_id"])
    except exceptions.EntityNotFound as err:
        return jsonify({"msg": str(err)}), 400

    if prop["toWork"] and not args.get("refresh", False):
        return jsonify(prop["toWork"])

    origin = directions.Location(**prop["location"])

    routes = current_app.directions_service.to_work(origin, args["mode"])

    prop_d = dict(prop)
    prop_d["toWork"] = routes
    current_app.prop_repo.update(Property(prop_d))

    return jsonify(routes)
