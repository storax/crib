"""
Property data
"""
import logging

import cmocean
import numpy
from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore
from matplotlib.colors import rgb2hex

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
    args = request.args.copy()
    try:
        cmname = args.get("colormap", "thermal_r")
        colormap = cmocean.cm.cmap_d[cmname]
    except KeyError:
        return jsonify({"msg": "Invalid color map"}), 400

    durations = list(current_app.directions_repo.get_to_work_durations())
    sortkey = lambda d: d["durationValue"]
    maxD = max(durations, key=sortkey)["durationValue"]
    minD = min(durations, key=sortkey)["durationValue"]

    colors = color_values(minD, maxD, colormap)

    offset = minD + 1
    for d in durations:
        v = d.pop("durationValue")
        d["color"] = colors[v - offset]
    log.debug("Fetched %s durations", len(durations))
    return jsonify(durations)


def color_values(minV, maxV, colormap):
    delta = maxV - minV
    colormap = colormap._resample(delta)
    rgb_values = colormap(numpy.arange(delta))[:, :-1]
    hex_values = [rgb2hex(rgb) for rgb in rgb_values]
    return hex_values


def fetch_map_to_work(mode):
    for route in current_app.directions_service.fetch_map_to_work(mode):
        try:
            d = Direction(route)
        except Exception as err:
            print(err)
            continue
        current_app.directions_repo.insert(d)
