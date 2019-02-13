"""
Property data
"""
import logging

from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore

from crib import exceptions
from crib.domain.direction import Direction, Location
from crib.domain.property import Property

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
    try:
        durations = current_app.directions_service.to_work_durations(**request.args)
        return jsonify(durations)
    except ValueError as err:
        return jsonify({"msg": str(err)}), 400


def fetch_map_to_work(mode):
    for route in current_app.directions_service.fetch_map_to_work(mode):
        try:
            d = Direction(route)
        except Exception as err:
            print(err)
            continue
        current_app.directions_repository.insert(d)
