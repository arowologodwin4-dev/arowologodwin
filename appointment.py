import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth_utils import login_required, get_current_user
from ..supabase_client import (create_appointment, get_all_appointments,
                                get_all_patients, get_all_doctors,
                                update_appointment_status)
from ..models import Appointment

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointments_bp.route("/")
@login_required
def list_appointments():
    try:
        appts = get_all_appointments().data or []
    except Exception:
        appts = []
        flash("Could not load appointments.", "danger")
    return render_template("appointments/list.html", appointments=appts, user=get_current_user())


@appointments_bp.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule():
    patients = get_all_patients().data or []
    doctors  = get_all_doctors().data  or []

    if request.method == "POST":
        f = request.form
        appt = Appointment(
            appointment_id = "APT-" + str(uuid.uuid4())[:8].upper(),
            patient_id     = f.get("patient_id", ""),
            doctor_id      = f.get("doctor_id", ""),
            date           = f.get("date", ""),
            time           = f.get("time", ""),
            reason         = f.get("reason", "").strip(),
        )
        try:
            create_appointment(appt.to_dict())
            flash("Appointment scheduled successfully.", "success")
            return redirect(url_for("appointments.list_appointments"))
        except Exception as e:
            flash(f"Failed: {str(e)}", "danger")

    return render_template("appointments/schedule.html",
                           patients=patients, doctors=doctors,
                           user=get_current_user())


@appointments_bp.route("/<appointment_id>/status", methods=["POST"])
@login_required
def update_status(appointment_id):
    status = request.form.get("status", "")
    try:
        update_appointment_status(appointment_id, status)
        flash(f"Appointment marked as {status}.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("appointments.list_appointments"))