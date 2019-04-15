"""
Property data
"""
import logging

from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore

bp = Blueprint("directions", __name__, url_prefix="/directions")
log = logging.getLogger(__name__)


@bp.route("/raster_map", methods=("GET",))
@jwt_required
def raster_map():
    raster = list(current_app.directions_service.raster_map())
    return jsonify(raster)


@bp.route("/colormaps", methods=("GET",))
@jwt_required
def colormaps():
    maps = list(current_app.directions_service.colormaps())
    return jsonify(maps)


@bp.route("/to_work_durations", methods=("GET",))
@jwt_required
def to_work_durations():
    maxDuration = request.args.get("maxDuration", 3000, int)
    colormap = request.args.get("colormap", "thermal_r")
    try:
        durations = current_app.directions_service.to_work_durations(
            colormap=colormap, maxDuration=maxDuration
        )
        return jsonify(durations)
    except ValueError as err:
        return jsonify({"msg": str(err)}), 400
