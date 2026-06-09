"""
models.py
─────────────────────────────────────────────────────────────────
Core OOP classes for the Hospital Patient Management System.
Demonstrates:
  • OOP         — classes with encapsulation & properties
  • Polymorphism — BillItem base class with subclasses per service
  • Queue        — PriorityQueue for emergency triage
─────────────────────────────────────────────────────────────────
"""

import heapq
from datetime import datetime
from enum import Enum


# ══════════════════════════════════════════════════════════════
#  ENUMS
# ══════════════════════════════════════════════════════════════

class Priority(Enum):
    EMERGENCY = 1   # highest priority (lowest heap number)
    URGENT    = 2
    NORMAL    = 3


class PatientStatus(Enum):
    ADMITTED   = "Admitted"
    DISCHARGED = "Discharged"
    ARCHIVED   = "Archived"


# ══════════════════════════════════════════════════════════════
#  PATIENT
# ══════════════════════════════════════════════════════════════

class Patient:
    """
    Represents a registered hospital patient.
    Encapsulates personal + medical information.
    """
    def __init__(self, patient_id: str, name: str, age: int,
                 gender: str, blood_type: str, contact: str,
                 medical_history: str = "", status: str = "Admitted"):
        self._patient_id      = patient_id
        self._name            = name
        self._age             = age
        self._gender          = gender
        self._blood_type      = blood_type
        self._contact         = contact
        self._medical_history = medical_history
        self._status          = status
        self._registered_at   = datetime.utcnow().isoformat()

    # ── Properties ────────────────────────────────────────────
    @property
    def patient_id(self):      return self._patient_id
    @property
    def name(self):            return self._name
    @property
    def age(self):             return self._age
    @property
    def gender(self):          return self._gender
    @property
    def blood_type(self):      return self._blood_type
    @property
    def contact(self):         return self._contact
    @property
    def medical_history(self): return self._medical_history
    @property
    def status(self):          return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    @medical_history.setter
    def medical_history(self, value: str):
        self._medical_history = value

    def to_dict(self) -> dict:
        return {
            "patient_id":      self._patient_id,
            "name":            self._name,
            "age":             self._age,
            "gender":          self._gender,
            "blood_type":      self._blood_type,
            "contact":         self._contact,
            "medical_history": self._medical_history,
            "status":          self._status,
            "registered_at":   self._registered_at,
        }

    def __repr__(self):
        return f"<Patient {self._patient_id}: {self._name}>"


# ══════════════════════════════════════════════════════════════
#  DOCTOR
# ══════════════════════════════════════════════════════════════

class Doctor:
    """Represents a hospital doctor with specialisation."""

    def __init__(self, doctor_id: str, name: str,
                 specialisation: str, contact: str):
        self._doctor_id      = doctor_id
        self._name           = name
        self._specialisation = specialisation
        self._contact        = contact

    @property
    def doctor_id(self):      return self._doctor_id
    @property
    def name(self):           return self._name
    @property
    def specialisation(self): return self._specialisation
    @property
    def contact(self):        return self._contact

    def to_dict(self) -> dict:
        return {
            "doctor_id":      self._doctor_id,
            "name":           self._name,
            "specialisation": self._specialisation,
            "contact":        self._contact,
        }

    def __repr__(self):
        return f"<Doctor {self._doctor_id}: Dr. {self._name}>"


# ══════════════════════════════════════════════════════════════
#  APPOINTMENT
# ══════════════════════════════════════════════════════════════

class Appointment:
    """Links a Patient to a Doctor for a scheduled visit."""

    def __init__(self, appointment_id: str, patient_id: str,
                 doctor_id: str, date: str, time: str,
                 reason: str, status: str = "Scheduled"):
        self._appointment_id = appointment_id
        self._patient_id     = patient_id
        self._doctor_id      = doctor_id
        self._date           = date
        self._time           = time
        self._reason         = reason
        self._status         = status

    @property
    def appointment_id(self): return self._appointment_id
    @property
    def patient_id(self):     return self._patient_id
    @property
    def doctor_id(self):      return self._doctor_id
    @property
    def date(self):           return self._date
    @property
    def time(self):           return self._time
    @property
    def reason(self):         return self._reason
    @property
    def status(self):         return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    def to_dict(self) -> dict:
        return {
            "appointment_id": self._appointment_id,
            "patient_id":     self._patient_id,
            "doctor_id":      self._doctor_id,
            "date":           self._date,
            "time":           self._time,
            "reason":         self._reason,
            "status":         self._status,
        }


# ══════════════════════════════════════════════════════════════
#  BILLING — POLYMORPHISM DEMO
# ══════════════════════════════════════════════════════════════

class BillItem:
    """
    Abstract base class for all billable services.
    Subclasses override calculate() — this IS the polymorphism requirement.
    """
    def __init__(self, description: str, quantity: int = 1):
        self._description = description
        self._quantity    = quantity

    @property
    def description(self): return self._description
    @property
    def quantity(self):    return self._quantity

    def calculate(self) -> float:
        """Override in subclasses — polymorphic behaviour."""
        raise NotImplementedError("Subclasses must implement calculate()")

    def to_dict(self) -> dict:
        return {
            "description": self._description,
            "quantity":    self._quantity,
            "amount":      self.calculate(),
            "type":        self.__class__.__name__,
        }


class ConsultationFee(BillItem):
    """Flat fee per consultation."""
    RATE = 5000.00  # ₦5,000 per consultation

    def __init__(self, quantity: int = 1):
        super().__init__("Consultation Fee", quantity)

    def calculate(self) -> float:
        return self.RATE * self._quantity


class MedicationFee(BillItem):
    """Per-item medication charge."""
    def __init__(self, medication_name: str, unit_price: float, quantity: int):
        super().__init__(f"Medication: {medication_name}", quantity)
        self._unit_price = unit_price

    def calculate(self) -> float:
        return self._unit_price * self._quantity


class LaboratoryFee(BillItem):
    """Fixed rate per lab test."""
    RATE = 3500.00  # ₦3,500 per test

    def __init__(self, test_name: str, quantity: int = 1):
        super().__init__(f"Lab Test: {test_name}", quantity)

    def calculate(self) -> float:
        return self.RATE * self._quantity


class WardFee(BillItem):
    """Daily ward/bed charge."""
    RATE = 8000.00  # ₦8,000 per day

    def __init__(self, days: int):
        super().__init__(f"Ward/Bed ({days} day{'s' if days != 1 else ''})", days)

    def calculate(self) -> float:
        return self.RATE * self._quantity


class SurgeryFee(BillItem):
    """Fixed surgery fee."""
    def __init__(self, surgery_name: str, base_cost: float):
        super().__init__(f"Surgery: {surgery_name}", 1)
        self._base_cost = base_cost

    def calculate(self) -> float:
        return self._base_cost


class Bill:
    """
    Aggregates BillItems for a patient.
    Calls calculate() on each item — runtime polymorphism in action.
    """
    def __init__(self, bill_id: str, patient_id: str):
        self._bill_id    = bill_id
        self._patient_id = patient_id
        self._items: list[BillItem] = []
        self._paid       = False
        self._created_at = datetime.utcnow().isoformat()

    def add_item(self, item: BillItem):
        self._items.append(item)

    def total(self) -> float:
        # Polymorphic call — each item type handles its own logic
        return sum(item.calculate() for item in self._items)

    @property
    def bill_id(self):    return self._bill_id
    @property
    def patient_id(self): return self._patient_id
    @property
    def paid(self):       return self._paid
    @paid.setter
    def paid(self, v):    self._paid = v

    def to_dict(self) -> dict:
        return {
            "bill_id":    self._bill_id,
            "patient_id": self._patient_id,
            "items":      [i.to_dict() for i in self._items],
            "total":      self.total(),
            "paid":       self._paid,
            "created_at": self._created_at,
        }


# ══════════════════════════════════════════════════════════════
#  PRIORITY QUEUE — EMERGENCY TRIAGE
# ══════════════════════════════════════════════════════════════

class EmergencyQueueEntry:
    """
    Wraps a patient for the priority queue.
    Lower priority number = seen first (EMERGENCY=1 beats NORMAL=3).
    """
    def __init__(self, patient_id: str, name: str,
                 priority: Priority, reason: str):
        self.patient_id = patient_id
        self.name       = name
        self.priority   = priority
        self.reason     = reason
        self.arrived_at = datetime.utcnow().isoformat()

    # heapq compares tuples; (priority.value, arrived_at) breaks ties by arrival time
    def __lt__(self, other):
        if self.priority.value == other.priority.value:
            return self.arrived_at < other.arrived_at
        return self.priority.value < other.priority.value

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "name":       self.name,
            "priority":   self.priority.name,
            "reason":     self.reason,
            "arrived_at": self.arrived_at,
        }


class EmergencyQueue:
    """
    Min-heap priority queue — patients with Priority.EMERGENCY (1)
    are always processed before URGENT (2) or NORMAL (3).
    """
    def __init__(self):
        self._heap: list = []

    def enqueue(self, entry: EmergencyQueueEntry):
        heapq.heappush(self._heap, entry)

    def dequeue(self) -> EmergencyQueueEntry | None:
        return heapq.heappop(self._heap) if self._heap else None

    def peek(self) -> EmergencyQueueEntry | None:
        return self._heap[0] if self._heap else None

    def all_entries(self) -> list[dict]:
        # Return sorted view without consuming the queue
        return [e.to_dict() for e in sorted(self._heap)]

    def size(self) -> int:
        return len(self._heap)

    def remove_by_patient_id(self, patient_id: str):
        self._heap = [e for e in self._heap if e.patient_id != patient_id]
        heapq.heapify(self._heap)


# ── Module-level singleton queue (shared across requests in dev) ──
emergency_queue = EmergencyQueue()