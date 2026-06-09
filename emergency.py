import uuid, json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth_utils import login_required, get_current_user
from ..supabase_client import (create_bill, get_all_bills, get_bill,
                                get_bills_for_patient, mark_bill_paid,
                                get_all_patients)
from ..models import (Bill, ConsultationFee, MedicationFee,
                      LaboratoryFee, WardFee, SurgeryFee)

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def _build_bill_from_form(patient_id: str, form) -> Bill:
    """
    Instantiate the correct BillItem subclass for each service selected.
    This triggers polymorphism: each subclass knows its own calculate() logic.
    """
    bill = Bill(bill_id="BILL-" + str(uuid.uuid4())[:8].upper(), patient_id=patient_id)

    if form.get("consultation") == "on":
        qty = int(form.get("consultation_qty", 1))
        bill.add_item(ConsultationFee(quantity=qty))

    if form.get("ward") == "on":
        days = int(form.get("ward_days", 1))
        bill.add_item(WardFee(days=days))

    if form.get("lab") == "on":
        test_name = form.get("lab_test_name", "General Test")
        qty       = int(form.get("lab_qty", 1))
        bill.add_item(LaboratoryFee(test_name=test_name, quantity=qty))

    if form.get("medication") == "on":
        med_name   = form.get("med_name", "Medication")
        unit_price = float(form.get("med_unit_price", 0))
        qty        = int(form.get("med_qty", 1))
        bill.add_item(MedicationFee(medication_name=med_name, unit_price=unit_price, quantity=qty))

    if form.get("surgery") == "on":
        surgery_name = form.get("surgery_name", "Surgery")
        cost         = float(form.get("surgery_cost", 0))
        bill.add_item(SurgeryFee(surgery_name=surgery_name, base_cost=cost))

    return bill


@billing_bp.route("/")
@login_required
def list_bills():
    try:
        bills = get_all_bills().data or []
        # Parse items JSON string if needed
        for b in bills:
            if isinstance(b.get("items"), str):
                b["items"] = json.loads(b["items"])
    except Exception:
        bills = []
        flash("Could not load bills.", "danger")
    return render_template("billing/list.html", bills=bills, user=get_current_user())


@billing_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    patients = get_all_patients().data or []

    if request.method == "POST":
        patient_id = request.form.get("patient_id", "")
        if not patient_id:
            flash("Please select a patient.", "danger")
            return render_template("billing/create.html", patients=patients, user=get_current_user())

        bill = _build_bill_from_form(patient_id, request.form)

        if not bill._items:
            flash("Please select at least one service.", "danger")
            return render_template("billing/create.html", patients=patients, user=get_current_user())

        data = bill.to_dict()
        data["items"] = json.dumps(data["items"])   # Supabase stores as JSONB/text
        try:
            create_bill(data)
            flash(f"Bill {bill.bill_id} created. Total: ₦{bill.total():,.2f}", "success")
            return redirect(url_for("billing.list_bills"))
        except Exception as e:
            flash(f"Failed: {str(e)}", "danger")

    return render_template("billing/create.html", patients=patients, user=get_current_user())


@billing_bp.route("/<bill_id>")
@login_required
def detail(bill_id):
    try:
        bill = get_bill(bill_id).data
        if isinstance(bill.get("items"), str):
            bill["items"] = json.loads(bill["items"])
        total = sum(i.get("amount", 0) for i in bill.get("items", []))
    except Exception:
        flash("Bill not found.", "danger")
        return redirect(url_for("billing.list_bills"))
    return render_template("billing/detail.html", bill=bill, total=total, user=get_current_user())


@billing_bp.route("/<bill_id>/pay", methods=["POST"])
@login_required
def mark_paid(bill_id):
    try:
        mark_bill_paid(bill_id)
        flash("Bill marked as paid.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("billing.detail", bill_id=bill_id))