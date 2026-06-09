import heapq
from datetime import datetime
from enum import Enum

class Priority(Enum):
    EMERGENCY = 1
    URGENT    = 2
    NORMAL    = 3

class Patient:
    def __init__(self, patient_id, name, age, gender, blood_type, contact, medical_history="", status="Admitted"):
        self._patient_id      = patient_id
        self._name            = name
        self._age             = age
        self._gender          = gender
        self._blood_type      = blood_type
        self._contact         = contact
        self._medical_history = medical_history
        self._status          = status
        self._registered_at   = datetime.utcnow().isoformat()

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
    def status(self, value):   self._status = value

    def to_dict(self):
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

class Doctor:
    def __init__(self, doctor_id, name, specialisation, contact):
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

    def to_dict(self):
        return {
            "doctor_id":      self._doctor_id,
            "name":           self._name,
            "specialisation": self._specialisation,
            "contact":        self._contact,
        }

class Appointment:
    def __init__(self, appointment_id, patient_id, doctor_id, date, time, reason, status="Scheduled"):
        self._appointment_id = appointment_id
        self._patient_id     = patient_id
        self._doctor_id      = doctor_id
        self._date           = date
        self._time           = time
        self._reason         = reason
        self._status         = status

    def to_dict(self):
        return {
            "appointment_id": self._appointment_id,
            "patient_id":     self._patient_id,
            "doctor_id":      self._doctor_id,
            "date":           self._date,
            "time":           self._time,
            "reason":         self._reason,
            "status":         self._status,
        }

class BillItem:
    def __init__(self, description, quantity=1):
        self._description = description
        self._quantity    = quantity
    @property
    def description(self): return self._description
    @property
    def quantity(self):    return self._quantity
    def calculate(self):
        raise NotImplementedError
    def to_dict(self):
        return {
            "description": self._description,
            "quantity":    self._quantity,
            "amount":      self.calculate(),
            "type":        self.__class__.__name__,
        }

class ConsultationFee(BillItem):
    RATE = 5000.00
    def __init__(self, quantity=1):
        super().__init__("Consultation Fee", quantity)
    def calculate(self):
        return self.RATE * self._quantity

class MedicationFee(BillItem):
    def __init__(self, medication_name, unit_price, quantity):
        super().__init__(f"Medication: {medication_name}", quantity)
        self._unit_price = unit_price
    def calculate(self):
        return self._unit_price * self._quantity

class LaboratoryFee(BillItem):
    RATE = 3500.00
    def __init__(self, test_name, quantity=1):
        super().__init__(f"Lab Test: {test_name}", quantity)
    def calculate(self):
        return self.RATE * self._quantity

class WardFee(BillItem):
    RATE = 8000.00
    def __init__(self, days):
        super().__init__(f"Ward/Bed ({days} days)", days)
    def calculate(self):
        return self.RATE * self._quantity

class SurgeryFee(BillItem):
    def __init__(self, surgery_name, base_cost):
        super().__init__(f"Surgery: {surgery_name}", 1)
        self._base_cost = base_cost
    def calculate(self):
        return self._base_cost

class Bill:
    def __init__(self, bill_id, patient_id):
        self._bill_id    = bill_id
        self._patient_id = patient_id
        self._items      = []
        self._paid       = False
        self._created_at = datetime.utcnow().isoformat()

    def add_item(self, item):
        self._items.append(item)

    def total(self):
        return sum(item.calculate() for item in self._items)

    @property
    def bill_id(self):    return self._bill_id
    @property
    def patient_id(self): return self._patient_id
    @property
    def paid(self):       return self._paid
    @paid.setter
    def paid(self, v):    self._paid = v

    def to_dict(self):
        return {
            "bill_id":    self._bill_id,
            "patient_id": self._patient_id,
            "items":      [i.to_dict() for i in self._items],
            "total":      self.total(),
            "paid":       self._paid,
            "created_at": self._created_at,
        }

class EmergencyQueueEntry:
    def __init__(self, patient_id, name, priority, reason):
        self.patient_id = patient_id
        self.name       = name
        self.priority   = priority
        self.reason     = reason
        self.arrived_at = datetime.utcnow().isoformat()

    def __lt__(self, other):
        if self.priority.value == other.priority.value:
            return self.arrived_at < other.arrived_at
        return self.priority.value < other.priority.value

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "name":       self.name,
            "priority":   self.priority.name,
            "reason":     self.reason,
            "arrived_at": self.arrived_at,
        }

class EmergencyQueue:
    def __init__(self):
        self._heap = []

    def enqueue(self, entry):
        heapq.heappush(self._heap, entry)

    def dequeue(self):
        return heapq.heappop(self._heap) if self._heap else None

    def all_entries(self):
        return [e.to_dict() for e in sorted(self._heap)]

    def size(self):
        return len(self._heap)

    def remove_by_patient_id(self, patient_id):
        self._heap = [e for e in self._heap if e.patient_id != patient_id]
        heapq.heapify(self._heap)

emergency_queue = EmergencyQueue()