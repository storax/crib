"""
Property data
"""
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required

bp = Blueprint("properties", __name__, url_prefix="/properties")


@bp.route("/locations", methods=("GET",))
@jwt_required
def locations():
    locations = [
        dict(p) for p in current_app.prop_repo.get_x(100)
    ]
    return jsonify(locations)
