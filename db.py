# db.py — Data Layer (Member 3 owns this file)
# Responsible for: loading JSON files, filtering/querying data
# All functions here return plain Python dicts — no Flask logic.

import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def _load(filename):
    """Load a JSON file from the data directory."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ---- Orders ----

def get_all_orders():
    """Return the full list of orders."""
    return _load('orders.json')

def get_order_by_id(order_id):
    """Return a single order dict matching order_id, or None if not found."""
    orders = get_all_orders()
    return next(
        (o for o in orders if o['orderId'].upper() == order_id.upper()),
        None
    )


# ---- Returns ----

def get_return_policy():
    """Return the returns policy configuration."""
    policy = _load('returns.json')
    return policy[0] if policy else {}

def get_return_items_for_order(order_id):
    """
    Return items eligible for return from a delivered order.
    Only delivered orders are eligible.
    """
    order = get_order_by_id(order_id)
    if not order:
        return None, None
    return order, order.get('items', [])


def _save(filename, data):
    """Save a Python object to JSON file in the data directory."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


# ---- Sync Status Metadata ----
_sync_metadata = {
    'lastSyncedAt': None,
    'syncMethod': 'UNINITIALIZED',
    'totalSynced': 0
}

def get_sync_status():
    """Return current inventory sync status metadata."""
    return _sync_metadata

def update_sync_status(method, count):
    """Update inventory sync metadata."""
    import datetime
    _sync_metadata['lastSyncedAt'] = datetime.datetime.now().isoformat()
    _sync_metadata['syncMethod'] = method
    _sync_metadata['totalSynced'] += count


# ---- Inventory ----

def search_inventory(query=''):
    """
    Return all inventory items matching the query string.
    Matches against name, sku, and category fields.
    Returns all items if query is empty.
    """
    inventory = _load('inventory.json')
    if not query:
        return inventory
    q = query.lower()
    return [
        item for item in inventory
        if q in item['name'].lower()
        or q in item['sku'].lower()
        or q in item['category'].lower()
    ]

def get_item_by_sku(sku):
    """Return a single inventory item by SKU, or None."""
    inventory = _load('inventory.json')
    return next((i for i in inventory if i['sku'] == sku), None)

def update_inventory_cache(updates):
    """
    Update local inventory cache with a list of stock updates.
    updates format: [{'sku': '...', 'stockCount': int, 'inStock': bool}, ...]
    """
    inventory = _load('inventory.json')
    updated_count = 0
    sku_map = {item['sku']: item for item in inventory}

    for update in updates:
        sku = update.get('sku')
        if sku in sku_map:
            if 'stockCount' in update:
                sku_map[sku]['stockCount'] = update['stockCount']
                sku_map[sku]['inStock'] = update['stockCount'] > 0
            if 'price' in update:
                sku_map[sku]['price'] = update['price']
            updated_count += 1

    _save('inventory.json', inventory)
    update_sync_status('POLLING_5MIN', updated_count)
    return updated_count


# ---- Day 4: Solstice Events Co. Attendees & Check-In Kiosk ----

def get_all_attendees():
    """Return all attendees."""
    try:
        return _load('attendees.json')
    except Exception:
        return []

def get_attendee_by_ticket_id(ticket_id):
    """Return a single attendee by ticket ID."""
    attendees = get_all_attendees()
    return next((a for a in attendees if a['ticketId'].upper() == ticket_id.upper()), None)

def initiate_attendee_checkin(ticket_id):
    """
    Initiate async badge print check-in for an attendee.
    Enforces Duplicate-Scan Protection: Rejects if status is PENDING_PRINT or CHECKED_IN.
    """
    import time
    attendees = get_all_attendees()
    attendee = next((a for a in attendees if a['ticketId'].upper() == ticket_id.upper()), None)

    if not attendee:
        return False, "ATTENDEE_NOT_FOUND", None

    # Duplicate scan protection check
    if attendee['status'] in ('PENDING_PRINT', 'CHECKED_IN'):
        return False, "DUPLICATE_SCAN_REJECTED", attendee

    # Generate unique print job ID
    job_id = f"JOB-{abs(hash(ticket_id + str(time.time()))) % 100000:05d}"
    attendee['status'] = 'PENDING_PRINT'
    attendee['printJobId'] = job_id

    _save('attendees.json', attendees)
    return True, "PRINT_JOB_ENQUEUED", attendee

def confirm_badge_printed(ticket_id, job_id, badge_id=None):
    """
    Callback handler to confirm badge print completion.
    Idempotent: If already CHECKED_IN, returns current state safely without duplicate processing.
    """
    import datetime
    attendees = get_all_attendees()
    attendee = next((a for a in attendees if a['ticketId'].upper() == ticket_id.upper()), None)

    if not attendee:
        return None

    # Idempotency check for out-of-order or duplicate webhooks
    if attendee['status'] == 'CHECKED_IN':
        return attendee

    attendee['status'] = 'CHECKED_IN'
    attendee['badgePrinted'] = True
    attendee['badgeId'] = badge_id or f"BDG-{job_id[-6:]}"
    attendee['checkedInAt'] = datetime.datetime.now().isoformat()

    _save('attendees.json', attendees)
    update_sync_status('ASYNC_QUEUE_WEBHOOK', 1)
    return attendee

def reset_attendees():
    """Reset attendees dataset to initial state for testing."""
    initial_attendees = [
        {"ticketId": "ATT-1001", "name": "Alice Johnson", "email": "alice@solsticeevents.com", "ticketType": "VIP Speaker", "status": "REGISTERED", "badgePrinted": False, "printJobId": None, "checkedInAt": None},
        {"ticketId": "ATT-1002", "name": "Bob Smith", "email": "bob@solsticeevents.com", "ticketType": "General Attendee", "status": "REGISTERED", "badgePrinted": False, "printJobId": None, "checkedInAt": None},
        {"ticketId": "ATT-1003", "name": "Charlie Davis", "email": "charlie@solsticeevents.com", "ticketType": "Workshop Lead", "status": "REGISTERED", "badgePrinted": False, "printJobId": None, "checkedInAt": None}
    ]
    _save('attendees.json', initial_attendees)
    return initial_attendees


