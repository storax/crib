"""
Scrape properties
"""
from flask_jwt_extended import jwt_required  # type: ignore
from quart import Blueprint, current_app, jsonify, request  # type: ignore

from crib import exceptions

bp = Blueprint("scrape", __name__, url_prefix="/scrape")


@bp.route("/scrape", methods=["POST"], endpoint="scrape")
@jwt_required
async def scrape():
    json = await request.json
    search = json.get("search")

    current_app.scrape_service.scrape(search)

    try:
        pass
    except ValueError as err:
        return jsonify({"msg": str(err)}), 400
    return jsonify({})
