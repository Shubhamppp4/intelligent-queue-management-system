from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# =========================
# CUSTOMER SCHEMAS
# =========================

class CustomerBase(BaseModel):
    name: str
    unique_id: str
    service: str
    token: str


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================
# STAFF SCHEMAS
# =========================

class StaffBase(BaseModel):
    name: str
    staff_id: str
    assigned_counter: Optional[int] = None


class StaffCreate(StaffBase):
    pass


class StaffResponse(StaffBase):
    id: int
    active: bool
    active_time: Optional[str] = None
    not_active_time: Optional[str] = None
    served_today: int

    model_config = ConfigDict(from_attributes=True)


# =========================
# ADMIN SCHEMAS
# =========================

class AdminBase(BaseModel):
    name: str
    admin_id: str
    username: str


class AdminCreate(AdminBase):
    password: str


class AdminResponse(AdminBase):
    id: int
    active: bool

    model_config = ConfigDict(from_attributes=True)


# =========================
# QUEUE RECORD SCHEMAS
# =========================

class QueueRecordBase(BaseModel):
    customer_id: int
    staff_id: Optional[int] = None
    counter_number: Optional[int] = None
    token: str
    service: str


class QueueRecordCreate(QueueRecordBase):
    pass


class QueueRecordResponse(QueueRecordBase):
    id: int
    status: str
    queue_position: Optional[int] = None
    waiting_time: int
    created_at: datetime
    called_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

#=====================================
# Counter Base
#=====================================
class CounterBase(BaseModel):
    counter_id: str
    counter_name: str
    service: str
    staff_count: int = 0
    status: str = "ACTIVE"
    avg_service_time: float = 0.0


class CounterCreate(CounterBase):
    pass


class CounterResponse(CounterBase):
    id: int

    class Config:
        from_attributes = True



class CounterUpdate(BaseModel):
    counter_id: str
    counter_name: str
    service: str
    staff_count: int
    status: str
    avg_service_time: float