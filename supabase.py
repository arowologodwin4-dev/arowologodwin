"""
supabase_client.py
──────────────────
Single Supabase client + all database helper functions.
Every table operation lives here — views stay clean.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_url: str = os.environ.get("SUPABASE_URL", "")
_key: str = os.environ.get("SUPABASE_KEY", "")

if not _url or not _key:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(_url, _key)


# ══════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════

def sign_up(email: str, password: str, full_name: str, role: str = "staff"):
    res = supabase.auth.sign_up({
        "email":    email,
        "password": password,
        "options":  {"data": {"full_name": full_name, "role": role}},
    })
    return res


def sign_in(email: str, password: str):
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return res


def sign_out(jwt: str):
    supabase.auth.sign_out()


def get_user(jwt: str):
    return supabase.auth.get_user(jwt)


# ══════════════════════════════════════════════════════════════
#  PATIENTS
# ══════════════════════════════════════════════════════════════

def create_patient(data: dict):
    return supabase.table("patients").insert(data).execute()


def get_all_patients():
    return supabase.table("patients").select("*").order("registered_at", desc=True).execute()


def get_patient(patient_id: str):
    return supabase.table("patients").select("*").eq("patient_id", patient_id).single().execute()


def update_patient(patient_id: str, data: dict):
    return supabase.table("patients").update(data).eq("patient_id", patient_id).execute()


def discharge_patient(patient_id: str):
    return supabase.table("patients").update({
        "status": "Discharged",
        "discharged_at": "now()",
    }).eq("patient_id", patient_id).execute()


def archive_patient(patient_id: str):
    return supabase.table("patients").update({"status": "Archived"}).eq("patient_id", patient_id).execute()


def search_patients(query: str):
    return supabase.table("patients").select("*").ilike("name", f"%{query}%").execute()


# ══════════════════════════════════════════════════════════════
#  DOCTORS
# ══════════════════════════════════════════════════════════════

def create_doctor(data: dict):
    return supabase.table("doctors").insert(data).execute()


def get_all_doctors():
    return supabase.table("doctors").select("*").order("name").execute()


def get_doctor(doctor_id: str):
    return supabase.table("doctors").select("*").eq("doctor_id", doctor_id).single().execute()


# ══════════════════════════════════════════════════════════════
#  APPOINTMENTS
# ══════════════════════════════════════════════════════════════

def create_appointment(data: dict):
    return supabase.table("appointments").insert(data).execute()


def get_all_appointments():
    return (supabase.table("appointments")
            .select("*, patients(name), doctors(name, specialisation)")
            .order("date", desc=False)
            .execute())


def get_appointments_for_patient(patient_id: str):
    return (supabase.table("appointments")
            .select("*, doctors(name, specialisation)")
            .eq("patient_id", patient_id)
            .order("date", desc=True)
            .execute())


def update_appointment_status(appointment_id: str, status: str):
    return supabase.table("appointments").update({"status": status}).eq("appointment_id", appointment_id).execute()


# ══════════════════════════════════════════════════════════════
#  BILLS
# ══════════════════════════════════════════════════════════════

def create_bill(data: dict):
    return supabase.table("bills").insert(data).execute()


def get_bills_for_patient(patient_id: str):
    return supabase.table("bills").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()


def get_bill(bill_id: str):
    return supabase.table("bills").select("*").eq("bill_id", bill_id).single().execute()


def mark_bill_paid(bill_id: str):
    return supabase.table("bills").update({"paid": True}).eq("bill_id", bill_id).execute()


def get_all_bills():
    return (supabase.table("bills")
            .select("*, patients(name)")
            .order("created_at", desc=True)
            .execute())


# ══════════════════════════════════════════════════════════════
#  EMERGENCY QUEUE (persisted to Supabase)
# ══════════════════════════════════════════════════════════════

def add_to_queue(data: dict):
    return supabase.table("emergency_queue").insert(data).execute()


def get_queue():
    return (supabase.table("emergency_queue")
            .select("*, patients(name)")
            .order("priority_level", desc=False)
            .order("arrived_at", desc=False)
            .execute())


def remove_from_queue(patient_id: str):
    return supabase.table("emergency_queue").delete().eq("patient_id", patient_id).execute()


def queue_entry_exists(patient_id: str):
    res = supabase.table("emergency_queue").select("patient_id").eq("patient_id", patient_id).execute()
    return len(res.data) > 0