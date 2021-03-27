"""
Property endpoints
"""
from flask_jwt_extended import jwt_required  # type: ignore
from quart import Blueprint, current_app, jsonify, request  # type: ignore
from shapely.geometry import shape
from shapely.ops import unary_union

from crib import exceptions

bp = Blueprint("properties", __name__, url_prefix="/properties")


@bp.route("/find", methods=["POST"], endpoint="find")
@jwt_required()
async def find():
    json = await request.json
    limit = json.get("limit")
    max_price = json.get("max_price")
    favorite = json.get("favorite")
    max_duration = json.get("max_duration")

    area = current_app.directions_service.get_area(max_duration)
    userarea = _geo_json_to_shape(json.get("area"))
    if area:
        if userarea:
            area = area.intersection(userarea)
    else:
        area = userarea

    try:
        props = [
            p.asdict()
            for p in current_app.property_service.find(
                max_price=max_price, favorite=favorite, area=area, limit=limit
            )
        ]
    except ValueError as err:
        return jsonify({"msg": str(err)}), 400
    return jsonify(props)


@bp.route("/to_work", methods=["GET"], endpoint="to_work")
@jwt_required()
async def to_work():
    args = request.args
    prop_id = args.get("prop_id")
    mode = args.get("mode")
    refresh = args.get("refresh", False)
    if not prop_id:
        return jsonify({"msg": "prop_id missing"}), 400
    if not mode:
        return jsonify({"msg": "mode missing"}), 400

    try:
        route = await current_app.property_service.to_work(
            prop_id, mode, refresh=refresh
        )
    except exceptions.EntityNotFound as err:
        return jsonify({"msg": str(err)}), 400

    return jsonify(route)


@bp.route("/favorite", methods=["PUT"], endpoint="favorite")
@jwt_required()
async def favorite():
    json = await request.json
    prop_id = json.get("prop_id")
    favorite = json.get("favorite")
    if prop_id is None:
        return jsonify({"msg": "prop_id is missing"}), 400
    if favorite is None:
        return jsonify({"msg": "favorite is missing"}), 400

    try:
        current_app.property_service.favorite(prop_id, favorite)
    except exceptions.EntityNotFound as err:
        return jsonify({"msg": str(err)}), 400

    return jsonify({"msg": "success"}), 200


@bp.route("/ban", methods=["PUT"], endpoint="ban")
@jwt_required()
async def ban():
    json = await request.json
    prop_id = json.get("prop_id")
    banned = json.get("banned")
    if prop_id is None:
        return jsonify({"msg": "prop_id is missing"}), 400
    if banned is None:
        return jsonify({"msg": "banned is missing"}), 400

    try:
        current_app.property_service.ban(prop_id, banned)
    except exceptions.EntityNotFound as err:
        return jsonify({"msg": str(err)}), 400

    return jsonify({"msg": "success"}), 200


def _geo_json_to_shape(data):
    if data and data["features"]:
        return unary_union([shape(f["geometry"]) for f in data["features"]])


@bp.route("/save_search_area", methods=["POST"], endpoint="save_search_area")
@jwt_required()
async def save_search_area():
    json = await request.json
    name = json.get("name")
    geojson = json.get("geojson")
    if name is None:
        return jsonify({"msg": "name is missing"}), 400
    if geojson is None:
        return jsonify({"msg": "geojson is missing"}), 400

    current_app.property_service.save_search_area(name, geojson)

    return jsonify({"msg": "success"}), 200


@bp.route("/get_search_areas", methods=["GET"], endpoint="get_search_areas")
@jwt_required()
async def get_search_areas():
    areas = current_app.property_service.get_search_areas()

    return jsonify({"areas": areas}), 200
