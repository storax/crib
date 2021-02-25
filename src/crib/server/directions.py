"""
Direction endpoints
"""
import logging

import geopandas  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore
from quart import Blueprint, current_app, jsonify, request  # type: ignore

bp = Blueprint("directions", __name__, url_prefix="/directions")
log = logging.getLogger(__name__)


@bp.route("/raster_map", methods=["GET"], endpoint="raster_map")
@jwt_required
async def raster_map():
    raster = list(current_app.directions_service.raster_map())
    return jsonify(raster)


@bp.route("/colormaps", methods=["GET"], endpoint="colormaps")
@jwt_required
async def colormaps():
    maps = list(current_app.directions_service.colormaps())
    return jsonify(maps)


@bp.route("/to_work_durations", methods=["GET"], endpoint="to_work_durations")
@jwt_required
async def to_work_durations():
    maxDuration = request.args.get("maxDuration", 3000, int)
    colormap = request.args.get("colormap", "thermal_r")
    try:
        durations = current_app.directions_service.to_work_durations(
            colormap=colormap, maxDuration=maxDuration
        )
        return jsonify(durations)
    except ValueError as err:
        return jsonify({"msg": str(err)}), 400


@bp.route("/get_area", methods=["GET"], endpoint="get_area")
@jwt_required
async def get_area():
    maxDuration = request.args.get("maxDuration", 42 * 60)
    alpha = request.args.get("alpha", None)
    hullbuffer = request.args.get("hullbuffer", None)
    try:
        maxDuration = maxDuration and int(maxDuration)
        alpha = alpha and int(alpha)
        hullbuffer = hullbuffer and int(hullbuffer)
    except (TypeError, ValueError):
        return jsonify({"msg": "Invalid parameter"}), 400

    area = current_app.directions_service.get_area(
        max_duration=maxDuration, alpha=alpha, hullbuffer=hullbuffer
    )
    return geopandas.GeoSeries(area).to_json()
