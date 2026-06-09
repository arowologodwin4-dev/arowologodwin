import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_url = os.environ.get("SUPABASE_URL", "")
_key = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(_url, _key)

# AUTH
def sign_up(email, password, full_name, role="staff"):
    return supabase.auth.sign_up({
        "email":    email,
        "password": password,
        "options":  {"data": {"full_name": full_name, "role": role}},
    })

def sign_in(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def sign_out():
    supabase.auth.sign_out()

# PATIENTS
def create_patient(data):
    return supabase.table("patients").insert(data).execute()

def get_all_patients():
    return supabase.table("patients").select("*").order("registered_at", desc=True).execute()

def get_patient(patient_id):
    return supabase.table("patients").select("*").eq("patient_id", patient_id).single().execute()

def update_patient(patient_id, data):
    return supabase.table("patients").update(data).eq("patient_id", patient_id).execute()

def discharge_patient(patient_id):
    return supabase.table("patients").update({"status": "Discharged"}).eq("patient_id", patient_id).execute()

def archive_patient(patient_id):
    return supabase.table("patients").update({"status": "Archived"}).eq("patient_id", patient_id).execute()

def search_patients(query):
    return supabase.table("patients").select("*").ilike("name", f"%{query}%").execute()

# DOCTORS
def create_doctor(data):
    return supabase.table("doctors").insert(data).execute()

def get_all_doctors():
    return supabase.table("doctors").select("*").order("name").execute()

def get_doctor(doctor_id):
    return supabase.table("doctors").select("*").eq("doctor_id", doctor_id).single().execute()

# APPOINTMENTS
def create_appointment(data):
    return supabase.table("appointments").insert(data).execute()

def get_all_appointments():
    return supabase.table("appointments").select("*, patients(name), doctors(name, specialisation)").order("date").execute()

def get_appointments_for_patient(patient_id):
    return supabase.table("appointments").select("*, doctors(name, specialisation)").eq("patient_id", patient_id).execute()

def update_appointment_status(appointment_id, status):
    return supabase.table("appointments").update({"status": status}).eq("appointment_id", appointment_id).execute()

# BILLS
def create_bill(data):
    return supabase.table("bills").insert(data).execute()

def get_all_bills():
    return supabase.table("bills").select("*, patients(name)").order("created_at", desc=True).execute()

def get_bill(bill_id):
    return supabase.table("bills").select("*").eq("bill_id", bill_id).single().execute()

def get_bills_for_patient(patient_id):
    return supabase.table("bills").select("*").eq("patient_id", patient_id).execute()

def mark_bill_paid(bill_id):
    return supabase.table("bills").update({"paid": True}).eq("bill_id", bill_id).execute()

# EMERGENCY QUEUE
def add_to_queue(data):
    return supabase.table("emergency_queue").insert(data).execute()

def get_queue():
    return supabase.table("emergency_queue").select("*, patients(name)").order("priority_level").order("arrived_at").execute()

def remove_from_queue(patient_id):
    return supabase.table("emergency_queue").delete().eq("patient_id", patient_id).execute()

def queue_entry_exists(patient_id):
    res = supabase.table("emergency_queue").select("patient_id").eq("patient_id", patient_id).execute()
    return len(res.data) > 0