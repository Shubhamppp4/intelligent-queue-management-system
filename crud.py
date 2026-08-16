from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas


# =========================================================
# QUEUE INTELLIGENCE SETTINGS
# =========================================================

AVERAGE_SERVICE_TIME = 5  # minutes per customer


# =========================================================
# CUSTOMER CRUD
# =========================================================

def create_customer(
    db: Session,
    customer: schemas.CustomerCreate
):
    db_customer = models.Customer(
        name=customer.name,
        unique_id=customer.unique_id,
        service=customer.service,
        token=customer.token,
        status="WAITING"
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer


def get_customer(
    db: Session,
    customer_id: int
):
    return (
        db.query(models.Customer)
        .filter(models.Customer.id == customer_id)
        .first()
    )


def get_customer_by_token(
    db: Session,
    token: str
):
    return (
        db.query(models.Customer)
        .filter(models.Customer.token == token)
        .first()
    )


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(models.Customer)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_customer_status(
    db: Session,
    customer_id: int,
    status: str
):
    customer = get_customer(db, customer_id)

    if customer:
        customer.status = status
        db.commit()
        db.refresh(customer)

    return customer


# =========================================================
# STAFF CRUD
# =========================================================

def create_staff(
    db: Session,
    staff: schemas.StaffCreate
):
    db_staff = models.Staff(
        name=staff.name,
        staff_id=staff.staff_id,
        assigned_counter=staff.assigned_counter,
        active=False,
        served_today=0
    )

    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)

    return db_staff


def get_staff(
    db: Session,
    staff_id: int
):
    return (
        db.query(models.Staff)
        .filter(models.Staff.id == staff_id)
        .first()
    )


def get_staff_by_staff_id(
    db: Session,
    staff_id: str
):
    return (
        db.query(models.Staff)
        .filter(models.Staff.staff_id == staff_id)
        .first()
    )


def get_all_staff(
    db: Session
):
    return db.query(models.Staff).all()


def update_staff_status(
    db: Session,
    staff_id: int,
    active: bool
):
    staff = get_staff(db, staff_id)

    if staff:
        staff.active = active

        if active:
            staff.active_time = datetime.now().strftime("%H:%M:%S")
        else:
            staff.not_active_time = datetime.now().strftime("%H:%M:%S")

        db.commit()
        db.refresh(staff)

    return staff


def update_staff_counter(
    db: Session,
    staff_id: int,
    counter_number: int
):
    staff = get_staff(db, staff_id)

    if staff:
        staff.assigned_counter = counter_number
        db.commit()
        db.refresh(staff)

    return staff


def increment_served_count(
    db: Session,
    staff_id: int
):
    staff = get_staff(db, staff_id)

    if staff:
        staff.served_today += 1
        db.commit()
        db.refresh(staff)

    return staff


# =========================================================
# ADMIN CRUD
# =========================================================

def create_admin(
    db: Session,
    admin: schemas.AdminCreate
):
    db_admin = models.Admin(
        name=admin.name,
        admin_id=admin.admin_id,
        username=admin.username,
        password=admin.password,
        active=True
    )

    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    return db_admin


def get_admin(
    db: Session,
    admin_id: int
):
    return (
        db.query(models.Admin)
        .filter(models.Admin.id == admin_id)
        .first()
    )


def get_admin_by_username(
    db: Session,
    username: str
):
    return (
        db.query(models.Admin)
        .filter(models.Admin.username == username)
        .first()
    )


def get_all_admins(
    db: Session
):
    return db.query(models.Admin).all()


# =========================================================
# QUEUE INTELLIGENCE
# =========================================================

def recalculate_queue(db: Session):
    """
    Waiting queue ki position aur estimated
    waiting time automatically calculate karta hai.
    """

    waiting_customers = (
        db.query(models.QueueRecord)
        .filter(
            models.QueueRecord.status == "WAITING"
        )
        .order_by(
            models.QueueRecord.created_at.asc()
        )
        .all()
    )

    for position, queue in enumerate(
        waiting_customers,
        start=1
    ):
        queue.queue_position = position

        # Example:
        # Position 1 = 5 minutes
        # Position 2 = 10 minutes
        # Position 3 = 15 minutes

        queue.waiting_time = (
            position * AVERAGE_SERVICE_TIME
        )

    db.commit()

    return waiting_customers


# =========================================================
# QUEUE CRUD
# =========================================================

def create_queue_record(
    db: Session,
    queue: schemas.QueueRecordCreate
):
    db_queue = models.QueueRecord(
        customer_id=queue.customer_id,
        staff_id=queue.staff_id,
        counter_number=queue.counter_number,
        token=queue.token,
        service=queue.service,
        status="WAITING",
        queue_position=None,
        waiting_time=0
    )

    db.add(db_queue)
    db.commit()
    db.refresh(db_queue)

    # Automatically calculate queue position
    recalculate_queue(db)

    db.refresh(db_queue)

    return db_queue


def get_queue_record(
    db: Session,
    queue_id: int
):
    return (
        db.query(models.QueueRecord)
        .filter(
            models.QueueRecord.id == queue_id
        )
        .first()
    )


def get_queue_by_token(
    db: Session,
    token: str
):
    return (
        db.query(models.QueueRecord)
        .filter(
            models.QueueRecord.token == token
        )
        .first()
    )


def get_waiting_queue(
    db: Session
):
    # Always keep queue intelligence updated
    recalculate_queue(db)

    return (
        db.query(models.QueueRecord)
        .filter(
            models.QueueRecord.status == "WAITING"
        )
        .order_by(
            models.QueueRecord.queue_position.asc()
        )
        .all()
    )


def get_all_queue_records(
    db: Session
):
    return (
        db.query(models.QueueRecord)
        .order_by(
            models.QueueRecord.created_at.desc()
        )
        .all()
    )


# =========================================================
# CALL NEXT CUSTOMER
# =========================================================

def call_next_customer(
    db: Session,
    staff_id: int,
    counter_number: int
):
    # First calculate latest queue
    recalculate_queue(db)

    next_customer = (
        db.query(models.QueueRecord)
        .filter(
            models.QueueRecord.status == "WAITING"
        )
        .order_by(
            models.QueueRecord.queue_position.asc()
        )
        .first()
    )

    if not next_customer:
        return None

    next_customer.staff_id = staff_id
    next_customer.counter_number = counter_number
    next_customer.status = "CALLED"
    next_customer.called_at = datetime.now()

    # Update customer status
    customer = get_customer(
        db,
        next_customer.customer_id
    )

    if customer:
        customer.status = "CALLED"

    db.commit()
    db.refresh(next_customer)

    # Recalculate remaining customers
    recalculate_queue(db)

    return next_customer


# =========================================================
# START SERVICE
# =========================================================

def start_service(
    db: Session,
    queue_id: int
):
    queue = get_queue_record(
        db,
        queue_id
    )

    if not queue:
        return None

    queue.status = "SERVING"

    # Update customer status
    customer = get_customer(
        db,
        queue.customer_id
    )

    if customer:
        customer.status = "SERVING"

    db.commit()
    db.refresh(queue)

    return queue


# =========================================================
# COMPLETE SERVICE
# =========================================================

def complete_service(
    db: Session,
    queue_id: int
):
    queue = get_queue_record(
        db,
        queue_id
    )

    if not queue:
        return None

    queue.status = "COMPLETED"
    queue.completed_at = datetime.now()

    # Update customer status
    customer = get_customer(
        db,
        queue.customer_id
    )

    if customer:
        customer.status = "COMPLETED"

    # Update staff served count
    if queue.staff_id:

        staff = get_staff(
            db,
            queue.staff_id
        )

        if staff:
            staff.served_today += 1

    db.commit()
    db.refresh(queue)

    # Recalculate remaining queue
    recalculate_queue(db)

    return queue


# =========================================================
# HOLD CUSTOMER
# =========================================================

def hold_customer(
    db: Session,
    queue_id: int
):
    queue = get_queue_record(
        db,
        queue_id
    )

    if not queue:
        return None

    queue.status = "HOLD"

    # Update customer status
    customer = get_customer(
        db,
        queue.customer_id
    )

    if customer:
        customer.status = "HOLD"

    db.commit()
    db.refresh(queue)

    # Recalculate remaining queue
    recalculate_queue(db)

    return queue


# =========================================================
# SKIP CUSTOMER
# =========================================================

def skip_customer(
    db: Session,
    queue_id: int
):
    queue = get_queue_record(
        db,
        queue_id
    )

    if not queue:
        return None

    queue.status = "SKIPPED"

    # Update customer status
    customer = get_customer(
        db,
        queue.customer_id
    )

    if customer:
        customer.status = "SKIPPED"

    db.commit()
    db.refresh(queue)

    # Recalculate remaining queue
    recalculate_queue(db)

    return queue


# =========================================================
# UPDATE WAITING TIME
# =========================================================

def update_waiting_time(
    db: Session,
    queue_id: int,
    waiting_time: int
):
    queue = get_queue_record(
        db,
        queue_id
    )

    if not queue:
        return None

    queue.waiting_time = waiting_time

    db.commit()
    db.refresh(queue)

    return queue

# =========================================================
# COUNTER INTELLIGENCE
# =========================================================

def get_counter_intelligence(
    db: Session
):
    counters = (
        db.query(models.Counter)
        .order_by(models.Counter.id.asc())
        .all()
    )

    result = []

    for counter in counters:

        # Waiting customers for this service
        waiting_customers = (
            db.query(models.QueueRecord)
            .filter(
                models.QueueRecord.status == "WAITING",
                models.QueueRecord.service == counter.service
            )
            .count()
        )

        # Staff assigned to this counter
        active_staff = (
            db.query(models.Staff)
            .filter(
                models.Staff.assigned_counter == counter.id,
                models.Staff.active == True
            )
            .count()
        )

        # If staff_count is stored in counter table,
        # use it when actual active staff is not available.
        staff_count = active_staff

        if staff_count == 0:
            staff_count = counter.staff_count

        # Calculate load
        if staff_count == 0:
            load_score = waiting_customers * 10
        else:
            load_score = (
                waiting_customers
                * counter.avg_service_time
            ) / staff_count

        # Determine load level
        if load_score >= 30:
            load_level = "HIGH"

        elif load_score >= 15:
            load_level = "MEDIUM"

        else:
            load_level = "LOW"

        # Recommendation
        if load_level == "HIGH":
            recommendation = (
                "Counter overloaded. "
                "Consider assigning additional staff."
            )

        elif load_level == "MEDIUM":
            recommendation = (
                "Counter moderately loaded. "
                "Monitor queue."
            )

        else:
            recommendation = (
                "Counter operating normally."
            )

        result.append(
            {
                "counter_id": counter.counter_id,
                "counter_name": counter.counter_name,
                "service": counter.service,
                "waiting_customers": waiting_customers,
                "active_staff": active_staff,
                "staff_count": staff_count,
                "avg_service_time": counter.avg_service_time,
                "load_score": round(load_score, 2),
                "load_level": load_level,
                "status": counter.status,
                "recommendation": recommendation
            }
        )

    return result


#==========Delete Counter==========
def delete_counter(db: Session, counter_id: int):
    counter = (
        db.query(models.Counter)
        .filter(models.Counter.id == counter_id)
        .first()
    )

    if not counter:
        return None

    db.query(models.Staff).filter(
        models.Staff.assigned_counter == counter.id
    ).update(
        {models.Staff.assigned_counter: None},
        synchronize_session=False
    )

    db.delete(counter)
    db.commit()

    return True


# =========================================================
# STAFF ↔ COUNTER RECOMMENDATION
# =========================================================

def get_staff_counter_recommendation(
    db: Session
):
    counters = (
        db.query(models.Counter)
        .filter(
            models.Counter.status == "ACTIVE"
        )
        .all()
    )

    staff_members = (
        db.query(models.Staff)
        .filter(
            models.Staff.active == True
        )
        .all()
    )

    recommendations = []

    for staff in staff_members:

        # Current counter of staff
        current_counter = None

        if staff.assigned_counter is not None:
            current_counter = (
                db.query(models.Counter)
                .filter(
                    models.Counter.id ==
                    staff.assigned_counter
                )
                .first()
            )

        counter_analysis = []

        for counter in counters:

            # Waiting customers for this service
            waiting_customers = (
                db.query(models.QueueRecord)
                .filter(
                    models.QueueRecord.status == "WAITING",
                    models.QueueRecord.service ==
                    counter.service
                )
                .count()
            )

            # Active staff at this counter
            active_staff = (
                db.query(models.Staff)
                .filter(
                    models.Staff.assigned_counter ==
                    counter.id,
                    models.Staff.active == True
                )
                .count()
            )

            # Include this staff if evaluating
            # the counter he/she could move to.
            effective_staff = active_staff

            if (
                current_counter is not None
                and current_counter.id == counter.id
            ):
                effective_staff = max(
                    active_staff,
                    1
                )

            if effective_staff == 0:
                effective_staff = 1

            # Calculate workload
            load_score = (
                waiting_customers
                * counter.avg_service_time
            ) / effective_staff

            counter_analysis.append(
                {
                    "counter_id": counter.counter_id,
                    "counter_name": counter.counter_name,
                    "waiting_customers": waiting_customers,
                    "active_staff": active_staff,
                    "avg_service_time":
                        counter.avg_service_time,
                    "load_score":
                        round(load_score, 2)
                }
            )

        # Find counter with highest load
        if counter_analysis:

            highest_load_counter = max(
                counter_analysis,
                key=lambda x: x["load_score"]
            )

            lowest_load_counter = min(
                counter_analysis,
                key=lambda x: x["load_score"]
            )

            # Recommendation
            if (
                highest_load_counter["load_score"]
                > lowest_load_counter["load_score"] * 1.5
            ):
                recommendation = (
                    f"Assign {staff.name} to "
                    f"{highest_load_counter['counter_name']}"
                )

                recommended_counter = (
                    highest_load_counter["counter_id"]
                )

            else:
                recommendation = (
                    f"{staff.name} can remain at "
                    "the current counter"
                )

                recommended_counter = (
                    current_counter.counter_id
                    if current_counter
                    else None
                )

            recommendations.append(
                {
                    "staff_id": staff.staff_id,
                    "staff_name": staff.name,
                    "current_counter":
                        current_counter.counter_id
                        if current_counter
                        else None,
                    "recommended_counter":
                        recommended_counter,
                    "recommendation":
                        recommendation,
                    "counter_analysis":
                        counter_analysis
                }
            )

    return recommendations



def update_counter(db: Session, counter_id: int, data):
    counter = db.query(models.Counter).filter(
        models.Counter.id == counter_id
    ).first()

    if not counter:
        return None

    counter.counter_id = data.counter_id
    counter.counter_name = data.counter_name
    counter.service = data.service
    counter.staff_count = data.staff_count
    counter.status = data.status
    counter.avg_service_time = data.avg_service_time

    db.commit()
    db.refresh(counter)

    return counter