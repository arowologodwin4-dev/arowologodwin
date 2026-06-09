"""
app/auth_utils.py
Session helpers shared across all blueprints.
"""
from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Decorator — redirects to login if no active session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "access_token" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """Return basic user info stored in the Flask session."""
    return {
        "email":     session.get("user_email", ""),
        "full_name": session.get("user_name", "Staff"),
        "role":      session.get("user_role", "staff"),
    }