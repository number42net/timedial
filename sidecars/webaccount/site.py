from typing import Any, Callable, Optional, TypeVar

import bcrypt
from flask import Flask, redirect, render_template, request, session, url_for
from login import login_required, load_user
from mail_bp import mail_bp
from werkzeug.wrappers import Response as WerkzeugResponse

app: Flask = Flask(__name__)
app.secret_key = "supersecretkey"  # Replace with a secure key in production

app.register_blueprint(mail_bp)

# Type variable for decorator


@app.route("/")
@login_required
def home() -> str:
    return "Hello, World!"


@app.route("/login", methods=["GET", "POST"])
def login() -> str | WerkzeugResponse:
    if "username" in session:
        return redirect(url_for("home"))

    error: Optional[str] = None

    if request.method == "POST":
        username: str = request.form["username"]
        password: bytes = request.form["password"].encode("utf-8")

        user_data: Optional[dict[str, Any]] = load_user(username)

        if user_data is None:
            error = "User not found."
        else:
            password_hash: bytes = user_data.get("password_hash", "").encode("utf-8")
            if bcrypt.checkpw(password, password_hash):
                session["username"] = username
                return redirect(url_for("home"))
            error = "Invalid password."

    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout() -> WerkzeugResponse:
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
