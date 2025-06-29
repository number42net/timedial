import json
import os
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

import bcrypt
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.wrappers import Response as WerkzeugResponse

ResponseType = str | WerkzeugResponse

F = TypeVar("F", bound=Callable[..., ResponseType])
USER_DATA_DIR: str = os.path.abspath("/data/guests")


def load_user(username: str) -> Optional[dict[str, Any]]:
    """Load user data from a file."""
    user_file: str = os.path.join(USER_DATA_DIR, f"{username}.json")
    if not os.path.isfile(user_file):
        return None
    try:
        with open(user_file, encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))
    except Exception:
        return None


def login_required(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ResponseType:
        if "username" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return cast(F, wrapper)
