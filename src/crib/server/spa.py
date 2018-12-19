"""
Test single page app
"""
from flask import Blueprint, render_template

bp = Blueprint("spa", __name__, url_prefix="/spa")


@bp.route("/", methods=("GET",))
def index():
    return render_template("spa/index.html")
