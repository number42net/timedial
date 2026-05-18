"""Settings blueprint for the webaccount sidecar."""

from flask import Blueprint

from login import login_required

settings_bp: Blueprint = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/")
@login_required
def settings() -> str:
    """Render the settings page."""
    return "Welcome to your settings."
