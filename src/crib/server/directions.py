"""
Property data
"""
import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from crib import exceptions

bp = Blueprint("directions", __name__, url_prefix="/directions")


@bp.route("/get", methods=("GET",))
def get():
    args = request.args.copy()
    args["key"] = current_app.config["GOOGLE_MAPS_APIKEY"]
    URL = "https://maps.googleapis.com/maps/api/directions/json"
    dir_response = requests.get(URL, args)
    return jsonify(dir_response.json()), dir_response.status_code
