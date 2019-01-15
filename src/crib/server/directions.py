"""
Property data
"""
import requests
from flask import Blueprint, current_app, jsonify, request  # type: ignore
from flask_jwt_extended import jwt_required  # type: ignore

bp = Blueprint("directions", __name__, url_prefix="/directions")


@bp.route("/get", methods=("GET",))
@jwt_required
def get():
    args = request.args.copy()
    args["key"] = current_app.config["GOOGLE_MAPS_APIKEY"]
    URL = "https://maps.googleapis.com/maps/api/directions/json"
    dir_response = requests.get(URL, args)
    return jsonify(dir_response.json()), dir_response.status_code
