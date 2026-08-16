from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# =========================
# CUSTOMER TABLE
# =========================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    unique_id = Column(String(100), unique=True, nullable=False, index=True)

    service = Column(String(100), nullable=False)

    token = Column(String(20), unique=True, nullable=False, index=True)

    status = Column(
        String(30),
        default="WAITING"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    queue_records = relationship(
        "QueueRecord",
        back_populates="customer"
    )


# =========================
# STAFF TABLE
# =========================

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    staff_id = Column(String(50), unique=True, nullable=False, index=True)

    assigned_counter = Column(Integer, nullable=True)

    active = Column(Boolean, default=False)

    active_time = Column(String(20), nullable=True)

    not_active_time = Column(String(20), nullable=True)

    served_today = Column(Integer, default=0)

    queue_records = relationship(
        "QueueRecord",
        back_populates="staff"
    )


# =========================
# ADMIN TABLE
# =========================

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    admin_id = Column(String(50), unique=True, nullable=False, index=True)

    username = Column(String(100), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    active = Column(Boolean, default=True)


# =========================
# MAIN QUEUE TABLE
# =========================

class QueueRecord(Base):
    __tablename__ = "queue_records"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    staff_id = Column(
        Integer,
        ForeignKey("staff.id"),
        nullable=True
    )

    counter_number = Column(
        Integer,
        nullable=True
    )

    token = Column(
        String(20),
        nullable=False,
        index=True
    )

    service = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(30),
        default="WAITING"
    )

    queue_position = Column(
        Integer,
        nullable=True
    )

    waiting_time = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    called_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    # Relationships

    customer = relationship(
        "Customer",
        back_populates="queue_records"
    )

    staff = relationship(
        "Staff",
        back_populates="queue_records"
    )


# =========================
# COUNTER TABLE
# =========================

class Counter(Base):
    __tablename__ = "counters"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    counter_id = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    counter_name = Column(
        String(100),
        nullable=False
    )

    service = Column(
        String(100),
        nullable=False
    )

    staff_count = Column(
        Integer,
        default=0
    )

    status = Column(
        String(30),
        default="ACTIVE"
    )

    avg_service_time = Column(
        Float,
        default=0.0
    )