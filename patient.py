import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth_utils import login_required, get_current_user
from ..supabase_client import (create_patient, get_all_patients, get_patient,
                                update_patient, discharge_patient, archive_patient,
                                get_appointments_for_patient, get_bills_for_patient,
                                search_patients)
from ..models import Patient

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patients_bp.route("/")
@login_required
def list_patients():
    q = request.args.get("q", "").strip()
    try:
        if q:
            result = search_patients(q).data or []
        else:
            result = get_all_patients().data or []
    except Exception:
        result = []
        flash("Could not load patients.", "danger")
    return render_template("patients/list.html", patients=result,
                           user=get_current_user(), query=q)


@patients_bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        f = request.form
        patient = Patient(
            patient_id      = "PAT-" + str(uuid.uuid4())[:8].upper(),
            name            = f.get("name", "").strip(),
            age             = int(f.get("age", 0)),
            gender          = f.get("gender", ""),
            blood_type      = f.get("blood_type", ""),
            contact         = f.get("contact", "").strip(),
            medical_history = f.get("medical_history", "").strip(),
        )
        try:
            create_patient(patient.to_dict())
            flash(f"Patient {patient.name} registered successfully (ID: {patient.patient_id}).", "success")
            return redirect(url_for("patients.list_patients"))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")

    return render_template("patients/register.html", user=get_current_user())


@patients_bp.route("/<patient_id>")
@login_required
def detail(patient_id):
    try:
        patient      = get_patient(patient_id).data
        appointments = get_appointments_for_patient(patient_id).data or []
        bills        = get_bills_for_patient(patient_id).data or []
    except Exception:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients.list_patients"))
    return render_template("patients/detail.html", patient=patient,
                           appointments=appointments, bills=bills,
                           user=get_current_user())


@patients_bp.route("/<patient_id>/discharge", methods=["POST"])
@login_required
def discharge(patient_id):
    try:
        discharge_patient(patient_id)
        flash("Patient discharged successfully.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("patients.detail", patient_id=patient_id))


@patients_bp.route("/<patient_id>/archive", methods=["POST"])
@login_required
def archive(patient_id):
    try:
        archive_patient(patient_id)
        flash("Patient record archived.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("patients.list_patients"))


@patients_bp.route("/<patient_id>/update-history", methods=["POST"])
@login_required
def update_history(patient_id):
    new_history = request.form.get("medical_history", "").strip()
    try:
        update_patient(patient_id, {"medical_history": new_history})
        flash("Medical history updated.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("patients.detail", patient_id=patient_id))