from flask import Blueprint, render_template
from ..auth_utils import login_required, get_current_user

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def home():
    from ..supabase_client import (get_all_patients, get_all_doctors,
                                    get_all_appointments, get_queue, get_all_bills)
    try:
        patients     = get_all_patients().data     or []
        doctors      = get_all_doctors().data      or []
        appointments = get_all_appointments().data or []
        queue        = get_queue().data            or []
        bills        = get_all_bills().data        or []
        admitted     = [p for p in patients if p.get("status") == "Admitted"]
        discharged   = [p for p in patients if p.get("status") == "Discharged"]
        unpaid_bills = [b for b in bills if not b.get("paid")]
        stats = {
            "total_patients": len(patients),
            "admitted":       len(admitted),
            "discharged":     len(discharged),
            "total_doctors":  len(doctors),
            "appointments":   len(appointments),
            "queue_size":     len(queue),
            "unpaid_bills":   len(unpaid_bills),
        }
        recent_patients    = patients[:5]
        today_appointments = appointments[:5]
        emergency_entries  = queue[:5]
    except Exception:
        stats = {}
        recent_patients = today_appointments = emergency_entries = []
    return render_template("dashboard.html",
                           user=get_current_user(),
                           stats=stats,
                           recent_patients=recent_patients,
                           today_appointments=today_appointments,
                           emergency_entries=emergency_entries)