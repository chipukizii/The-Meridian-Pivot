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

