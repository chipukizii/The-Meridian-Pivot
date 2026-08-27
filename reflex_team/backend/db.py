# backend/db.py
# OWNER: Member 1
# RESPONSIBILITY: Data models, order state machine, in-memory database, OTP logic
#
# TODO — Member 1, implement the following:
#
#   [ ] _ORDERS dict — store all delivery orders keyed by order ID
#   [ ] _RIDERS dict — seed 3 default riders with id, name, phone, status
#   [ ] _AUDIT_LOGS list — immutable log of every state transition
#
#   [ ] reset_db()         — reset all state to seed data (used for demo resets)
#   [ ] get_all_orders()   — return list of all orders
#   [ ] get_order_by_id()  — return single order by ID
#   [ ] get_all_riders()   — return list of all riders
#   [ ] get_rider_by_id()  — return single rider by ID
#   [ ] get_audit_logs()   — return audit log, optionally filtered by order_id
#   [ ] create_order()     — create a new PENDING_DISPATCH order with auto-generated OTP
#   [ ] assign_order_to_rider() — PENDING_DISPATCH → ASSIGNED with concurrency guard
#   [ ] rider_pickup_order()    — ASSIGNED → PICKED_UP
#   [ ] verify_and_deliver_order() — PICKED_UP → DELIVERED after OTP check
#
# State machine:
#   PENDING_DISPATCH → ASSIGNED → PICKED_UP → DELIVERED


def reset_db():
    pass


def get_all_orders():
    pass


def get_order_by_id(order_id):
    pass


def get_all_riders():
    pass


def get_rider_by_id(rider_id):
    pass


def get_audit_logs(order_id=None):
    pass


def create_order(retailer_name, customer_name, customer_phone, dropoff_address, item_desc, order_value_kes):
    pass


def assign_order_to_rider(order_id, rider_id):
    pass


def rider_pickup_order(order_id, rider_id):
    pass


def verify_and_deliver_order(order_id, rider_id, input_otp):
    pass
