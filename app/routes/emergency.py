from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth_utils import login_required, get_current_user
from ..supabase_client import (add_to_queue, get_queue, remove_from_queue,
                                queue_entry_exists, get_all_patients)
from ..models import EmergencyQueueEntry, Priority, emergency_queue
from datetime import datetime

emergency_bp = Blueprint("emergency", __name__, url_prefix="/emergency")

PRIORITY_LABELS = {
    "EMERGENCY": "🔴 Emergency",
    "URGENT":    "🟡 Urgent",
    "NORMAL":    "🟢 Normal",
}

@emergency_bp.route("/")
@login_required
def queue_view():
    try:
        entries = get_queue().data or []
    except Exception:
        entries = []
        flash("Could not load queue.", "danger")
    return render_template("emergency/queue.html",
                           entries=entries,
                           priority_labels=PRIORITY_LABELS,
                           user=get_current_user())

@emergency_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    patients = get_all_patients().data or []
    admitted = [p for p in patients if p.get("status") == "Admitted"]
    if request.method == "POST":
        patient_id    = request.form.get("patient_id", "")
        priority_name = request.form.get("priority", "NORMAL")
        reason        = request.form.get("reason", "").strip()
        if not patient_id or not reason:
            flash("Patient and reason are required.", "danger")
            return render_template("emergency/add.html",
                                   patients=admitted, user=get_current_user())
        try:
            priority = Priority[priority_name]
        except KeyError:
            priority = Priority.NORMAL
        patient_name = next((p["name"] for p in admitted
                             if p["patient_id"] == patient_id), "Unknown")
        entry = EmergencyQueueEntry(patient_id, patient_name, priority, reason)
        emergency_queue.enqueue(entry)
        if not queue_entry_exists(patient_id):
            add_to_queue({
                "patient_id":     patient_id,
                "priority":       priority_name,
                "priority_level": priority.value,
                "reason":         reason,
                "arrived_at":     datetime.utcnow().isoformat(),
            })
        flash(f"Patient added as {PRIORITY_LABELS[priority_name]}.", "success")
        return redirect(url_for("emergency.queue_view"))
    return render_template("emergency/add.html",
                           patients=admitted, user=get_current_user())

@emergency_bp.route("/remove/<patient_id>", methods=["POST"])
@login_required
def remove(patient_id):
    try:
        remove_from_queue(patient_id)
        emergency_queue.remove_by_patient_id(patient_id)
        flash("Patient removed from emergency queue.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("emergency.queue_view"))