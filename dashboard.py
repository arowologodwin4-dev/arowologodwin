from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..supabase_client import sign_in, sign_up

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def index():
    if "access_token" in session:
        return redirect(url_for("dashboard.home"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "access_token" in session:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            res = sign_in(email, password)
            user = res.user
            session["access_token"] = res.session.access_token
            session["user_email"]   = user.email
            session["user_name"]    = user.user_metadata.get("full_name", "Staff")
            session["user_role"]    = user.user_metadata.get("role", "staff")
            flash(f"Welcome back, {session['user_name']}!", "success")
            return redirect(url_for("dashboard.home"))
        except Exception as e:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if "access_token" in session:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email     = request.form.get("email", "").strip()
        password  = request.form.get("password", "")
        confirm   = request.form.get("confirm_password", "")
        role      = request.form.get("role", "staff")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("auth/signup.html")

        try:
            sign_up(email, password, full_name, role)
            flash("Account created! Please check your email to confirm, then log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            flash(f"Signup failed: {str(e)}", "danger")

    return render_template("auth/signup.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))