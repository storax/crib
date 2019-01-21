"""
Property data
"""
import logging

from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore

from crib import exceptions
from crib.domain.direction import Direction
from crib.domain.property import Property
from crib.services import directions

bp = Blueprint("directions", __name__, url_prefix="/directions")
log = logging.getLogger(__name__)


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

    route = current_app.directions_service.to_work(origin, args["mode"])

    prop_d = dict(prop)
    prop_d["toWork"] = route
    current_app.prop_repo.update(Property(prop_d))

    return jsonify(route)


@bp.route("/raster_map", methods=("GET",))
@jwt_required
def raster_map():
    raster = list(current_app.directions_service.raster_map())
    return jsonify(raster)


@bp.route("/to_work_durations", methods=("GET",))
@jwt_required
def to_work_durations():
    durations = list(current_app.directions_repo.get_to_work_durations())
    maxD = max(durations, key=lambda d: d["duration"])["duration"]
    minD = min(durations, key=lambda d: d["duration"])["duration"]
    log.info("Fetched %s durations", len(durations))
    return jsonify({"durations": durations, "minDuration": minD, "maxDuration": maxD})


def fetch_map_to_work(mode):
    for route in current_app.directions_service.fetch_map_to_work(mode):
        try:
            d = Direction(route)
        except Exception as err:
            print(err)
            continue
        current_app.directions_repo.insert(d)
