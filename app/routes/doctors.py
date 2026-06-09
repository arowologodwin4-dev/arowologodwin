import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth_utils import login_required, get_current_user

doctors_bp = Blueprint("doctors", __name__, url_prefix="/doctors")

@doctors_bp.route("/")
@login_required
def list_doctors():
    from ..supabase_client import get_all_doctors
    try:
        doctors = get_all_doctors().data or []
    except Exception:
        doctors = []
        flash("Could not load doctors.", "danger")
    return render_template("doctors/list.html", doctors=doctors, user=get_current_user())

@doctors_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_doctor():
    from ..supabase_client import create_doctor
    from ..models import Doctor
    if request.method == "POST":
        f = request.form
        doctor = Doctor(
            doctor_id      = "DOC-" + str(uuid.uuid4())[:8].upper(),
            name           = f.get("name", "").strip(),
            specialisation = f.get("specialisation", "").strip(),
            contact        = f.get("contact", "").strip(),
        )
        try:
            create_doctor(doctor.to_dict())
            flash(f"Dr. {doctor.name} added successfully.", "success")
            return redirect(url_for("doctors.list_doctors"))
        except Exception as e:
            flash(f"Failed: {str(e)}", "danger")
    return render_template("doctors/add.html", user=get_current_user())