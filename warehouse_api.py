# warehouse_api.py — Mock Warehouse API Feed
# Represents Northstar Retail Co.'s upstream warehouse system (Sprint 2 - Day 3 Spec)
# Exposes polling endpoint: GET /warehouse/stock

from flask import Blueprint, jsonify
import random

warehouse_bp = Blueprint('warehouse_api', __name__)

# Simulated warehouse database
_MOCK_WAREHOUSE_STOCK = [
    {"sku": "SKU-SHOE-01", "name": "Ultra-Fit Running Shoes", "stockCount": 45, "inStock": True},
    {"sku": "SKU-AUDIO-02", "name": "Wireless Noise-Canceling Headphones", "stockCount": 18, "inStock": True},
    {"sku": "SKU-HOOD-03", "name": "Organic Cotton Hoodie", "stockCount": 12, "inStock": True},
    {"sku": "SKU-BOTT-04", "name": "Insulated Thermal Water Bottle (1L)", "stockCount": 92, "inStock": True}
]

@warehouse_bp.route('/warehouse/stock', methods=['GET'])
def get_warehouse_stock():
    """
    Simulated Warehouse API endpoint polled every 5 minutes.
    Simulates real-time inventory updates from the central distribution center.
    """
    # Slightly fluctuate stock levels to simulate real warehouse activity
    for item in _MOCK_WAREHOUSE_STOCK:
        delta = random.choice([-1, 0, 1, 2])
        item['stockCount'] = max(0, item['stockCount'] + delta)
        item['inStock'] = item['stockCount'] > 0

    return jsonify({
        'status': 'success',
        'source': 'Northstar Central Warehouse #4',
        'pollIntervalSeconds': 300,
        'itemCount': len(_MOCK_WAREHOUSE_STOCK),
        'inventory': _MOCK_WAREHOUSE_STOCK
    })
