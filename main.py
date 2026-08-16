from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud

from database import engine, Base, get_db


# =========================================================
# DATABASE TABLE CREATION
# =========================================================

models.Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Intelligent Queue Management API",
    description="Backend API for Customer, Staff and Admin applications",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "Intelligent Queue Management API is running",
        "status": "success"
    }


# =========================================================
# CUSTOMER APIs
# =========================================================

@app.post(
    "/customers",
    response_model=schemas.CustomerResponse
)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    existing_token = crud.get_customer_by_token(
        db,
        customer.token
    )

    if existing_token:
        raise HTTPException(
            status_code=400,
            detail="Token already exists"
        )

    return crud.create_customer(
        db,
        customer
    )


@app.get(
    "/customers",
    response_model=List[schemas.CustomerResponse]
)
def get_customers(
    db: Session = Depends(get_db)
):
    return crud.get_customers(db)


@app.get(
    "/customers/{customer_id}",
    response_model=schemas.CustomerResponse
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = crud.get_customer(
        db,
        customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


@app.get(
    "/customers/token/{token}",
    response_model=schemas.CustomerResponse
)
def get_customer_by_token(
    token: str,
    db: Session = Depends(get_db)
):
    customer = crud.get_customer_by_token(
        db,
        token
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Token not found"
        )

    return customer


@app.patch(
    "/customers/{customer_id}/status",
    response_model=schemas.CustomerResponse
)
def update_customer_status(
    customer_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    customer = crud.update_customer_status(
        db,
        customer_id,
        status
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


# =========================================================
# STAFF APIs
# =========================================================

@app.post(
    "/staff",
    response_model=schemas.StaffResponse
)
def create_staff(
    staff: schemas.StaffCreate,
    db: Session = Depends(get_db)
):
    existing_staff = crud.get_staff_by_staff_id(
        db,
        staff.staff_id
    )

    if existing_staff:
        raise HTTPException(
            status_code=400,
            detail="Staff ID already exists"
        )

    return crud.create_staff(
        db,
        staff
    )


@app.get(
    "/staff",
    response_model=List[schemas.StaffResponse]
)
def get_staff(
    db: Session = Depends(get_db)
):
    return crud.get_all_staff(db)


@app.get(
    "/staff/{staff_id}",
    response_model=schemas.StaffResponse
)
def get_staff_member(
    staff_id: int,
    db: Session = Depends(get_db)
):
    staff = crud.get_staff(
        db,
        staff_id
    )

    if not staff:
        raise HTTPException(
            status_code=404,
            detail="Staff not found"
        )

    return staff


@app.patch(
    "/staff/{staff_id}/status",
    response_model=schemas.StaffResponse
)
def update_staff_status(
    staff_id: int,
    active: bool,
    db: Session = Depends(get_db)
):
    staff = crud.update_staff_status(
        db,
        staff_id,
        active
    )

    if not staff:
        raise HTTPException(
            status_code=404,
            detail="Staff not found"
        )

    return staff


@app.patch(
    "/staff/{staff_id}/counter",
    response_model=schemas.StaffResponse
)
def update_staff_counter(
    staff_id: int,
    counter_number: int,
    db: Session = Depends(get_db)
):
    staff = crud.update_staff_counter(
        db,
        staff_id,
        counter_number
    )

    if not staff:
        raise HTTPException(
            status_code=404,
            detail="Staff not found"
        )

    return staff


# =========================================================
# ADMIN APIs
# =========================================================

@app.post(
    "/admins",
    response_model=schemas.AdminResponse
)
def create_admin(
    admin: schemas.AdminCreate,
    db: Session = Depends(get_db)
):
    existing_admin = crud.get_admin_by_username(
        db,
        admin.username
    )

    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    return crud.create_admin(
        db,
        admin
    )


@app.get(
    "/admins",
    response_model=List[schemas.AdminResponse]
)
def get_admins(
    db: Session = Depends(get_db)
):
    return crud.get_all_admins(db)


# =========================================================
# QUEUE APIs
# =========================================================

@app.post(
    "/queue",
    response_model=schemas.QueueRecordResponse
)
def create_queue(
    queue: schemas.QueueRecordCreate,
    db: Session = Depends(get_db)
):
    customer = crud.get_customer(
        db,
        queue.customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return crud.create_queue_record(
        db,
        queue
    )


@app.get(
    "/queue",
    response_model=List[schemas.QueueRecordResponse]
)
def get_queue(
    db: Session = Depends(get_db)
):
    return crud.get_all_queue_records(db)


@app.get(
    "/queue/waiting",
    response_model=List[schemas.QueueRecordResponse]
)
def get_waiting_queue(
    db: Session = Depends(get_db)
):
    return crud.get_waiting_queue(db)


@app.get(
    "/queue/{queue_id}",
    response_model=schemas.QueueRecordResponse
)
def get_queue_record(
    queue_id: int,
    db: Session = Depends(get_db)
):
    queue = crud.get_queue_record(
        db,
        queue_id
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


# =========================================================
# CALL NEXT CUSTOMER
# =========================================================

@app.post(
    "/queue/call-next/{staff_id}/{counter_number}",
    response_model=schemas.QueueRecordResponse
)
def call_next_customer(
    staff_id: int,
    counter_number: int,
    db: Session = Depends(get_db)
):
    staff = crud.get_staff(
        db,
        staff_id
    )

    if not staff:
        raise HTTPException(
            status_code=404,
            detail="Staff not found"
        )

    queue = crud.call_next_customer(
        db,
        staff_id,
        counter_number
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="No waiting customer"
        )

    return queue


# =========================================================
# START SERVICE
# =========================================================

@app.post(
    "/queue/{queue_id}/start",
    response_model=schemas.QueueRecordResponse
)
def start_service(
    queue_id: int,
    db: Session = Depends(get_db)
):
    queue = crud.start_service(
        db,
        queue_id
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


# =========================================================
# COMPLETE SERVICE
# =========================================================

@app.post(
    "/queue/{queue_id}/complete",
    response_model=schemas.QueueRecordResponse
)
def complete_service(
    queue_id: int,
    db: Session = Depends(get_db)
):
    queue = crud.complete_service(
        db,
        queue_id
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


# =========================================================
# HOLD CUSTOMER
# =========================================================

@app.post(
    "/queue/{queue_id}/hold",
    response_model=schemas.QueueRecordResponse
)
def hold_customer(
    queue_id: int,
    db: Session = Depends(get_db)
):
    queue = crud.hold_customer(
        db,
        queue_id
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


# =========================================================
# SKIP CUSTOMER
# =========================================================

@app.post(
    "/queue/{queue_id}/skip",
    response_model=schemas.QueueRecordResponse
)
def skip_customer(
    queue_id: int,
    db: Session = Depends(get_db)
):
    queue = crud.skip_customer(
        db,
        queue_id
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


# =========================================================
# WAITING TIME
# =========================================================

@app.patch(
    "/queue/{queue_id}/waiting-time",
    response_model=schemas.QueueRecordResponse
)
def update_waiting_time(
    queue_id: int,
    waiting_time: int,
    db: Session = Depends(get_db)
):
    queue = crud.update_waiting_time(
        db,
        queue_id,
        waiting_time
    )

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue record not found"
        )

    return queue


# =========================
# COUNTER APIs
# =========================

@app.post("/counters", response_model=schemas.CounterResponse)
def create_counter(
    counter: schemas.CounterCreate,
    db: Session = Depends(get_db)
):
    db_counter = models.Counter(
        counter_id=counter.counter_id,
        counter_name=counter.counter_name,
        service=counter.service,
        staff_count=counter.staff_count,
        status=counter.status,
        avg_service_time=counter.avg_service_time
    )

    db.add(db_counter)
    db.commit()
    db.refresh(db_counter)

    return db_counter


@app.get("/counters", response_model=list[schemas.CounterResponse])
def get_counters(
    db: Session = Depends(get_db)
):
    return db.query(models.Counter).all()

@app.delete("/counters/{counter_id}")
def delete_counter(
    counter_id: int,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_counter(db, counter_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Counter not found"
        )

    return {
        "message": "Counter deleted successfully",
        "counter_id": counter_id
    }


# =========================================================
# COUNTER INTELLIGENCE API
# =========================================================

@app.get("/counters/intelligence")
def counter_intelligence(
    db: Session = Depends(get_db)
):
    return crud.get_counter_intelligence(db)


# =========================================================
# STAFF COUNTER RECOMMENDATION
# =========================================================

@app.get("/staff-counter-recommendation")
def staff_counter_recommendation(
    db: Session = Depends(get_db)
):
    return crud.get_staff_counter_recommendation(db)


# =========================================================
# GET ALL STAFF
# =========================================================

@app.get(
    "/staff",
    response_model=List[schemas.StaffResponse]
)
def get_staff(
    db: Session = Depends(get_db)
):
    return crud.get_all_staff(db)


# =========================================================
# GET STAFF BY ID
# =========================================================

@app.get(
    "/staff/{staff_id}",
    response_model=schemas.StaffResponse
)
def get_staff_member(
    staff_id: int,
    db: Session = Depends(get_db)
):
    staff = crud.get_staff(
        db,
        staff_id
    )

    if not staff:
        raise HTTPException(
            status_code=404,
            detail="Staff not found"
        )

    return staff


@app.put("/counters/{counter_id}")
def update_counter(
    counter_id: int,
    data: schemas.CounterUpdate,
    db: Session = Depends(get_db)
):
    counter = crud.update_counter(db, counter_id, data)

    if not counter:
        raise HTTPException(
            status_code=404,
            detail="Counter not found"
        )

    return counter