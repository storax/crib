"""
Property data
"""
from flask import Blueprint, current_app, jsonify

bp = Blueprint("properties", __name__, url_prefix="/properties")


@bp.route("/locations", methods=("GET",))
def locations():
    locations = [
        [p["location"]["latitude"], p["location"]["longitude"]]
        for p in current_app.prop_repo.get_all()
    ]
    return jsonify(locations)
