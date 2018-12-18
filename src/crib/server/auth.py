import functools

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from crib import exceptions
from crib.domain.user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        repo = current_app.user_repo
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        user = User(username=username, password=generate_password_hash(password))
        try:
            repo.add_user(user)
        except exceptions.DuplicateUser:
            error = f"User {username} is already registered."
        else:
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        repo = current_app.user_repo
        error = None
        try:
            user = repo.get_user(username)
        except exceptions.EntityNotFound:
            error = "Incorrect username"
        else:
            if not check_password_hash(user["password"], password):
                error = "Incorrect password"

        if error is None:
            session.clear()
            session["username"] = user["username"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    repo = current_app.user_repo
    username = session.get("username")

    if username is None:
        g.user = None
    else:
        g.user = repo.get_user(username)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
