# routes.py — Flask Route Layer (Member 2 owns this file)
# Responsible for: HTTP endpoints, request parsing, response formatting
# Calls db.py for all data — no direct file I/O here.

from flask import Blueprint, jsonify, request
import db

api = Blueprint('api', __name__)

# ---- API Root Directory ----

@api.route('/', methods=['GET'])
def api_index():
    return jsonify({
        'status': 'online',
        'endpoints': {
            'deflection-stats': '/api/deflection-stats [GET, POST]',
            'order-status': '/api/orders/<order_id> [GET]',
            'returns-eligibility': '/api/returns/<order_id> [GET]',
            'returns-generate-slip': '/api/returns/generate-slip [POST]',
            'inventory-search': '/api/inventory?q=<query> [GET]',
            'inventory-notify': '/api/inventory/notify [POST]',
            'support-ticket': '/api/support-ticket [POST]'
        }
    })


# Shared in-memory deflection counter
_deflection = {'count': 124, 'total': 159}


# ---- Deflection Stats ----

@api.route('/deflection-stats', methods=['GET', 'POST'])
def deflection_stats():
    if request.method == 'POST':
        _deflection['count'] += 1
        _deflection['total'] += 1
    rate = round((_deflection['count'] / max(1, _deflection['total'])) * 100)
    return jsonify({
        'count': _deflection['count'],
        'rate': rate,
        'message': f"{_deflection['count']} queries resolved self-serve today ({rate}% deflection rate)"
    })


# ---- Category 1: Order Status ----

@api.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = db.get_order_by_id(order_id)
    if not order:
        return jsonify({
            'success': False,
            'error': f"Order '{order_id}' not found. Try ORD-1001, ORD-1002, or ORD-1003."
        }), 404

    _deflection['count'] += 1
    _deflection['total'] += 1
    return jsonify({'success': True, 'order': order})


# ---- Category 2: Returns & Refunds ----

@api.route('/returns/<order_id>', methods=['GET'])
def get_return_eligibility(order_id):
    order, items = db.get_return_items_for_order(order_id)
    if order is None:
        return jsonify({
            'success': False,
            'error': f"Order '{order_id}' not found."
        }), 404

    _deflection['count'] += 1
    _deflection['total'] += 1
    policy = db.get_return_policy()
    return jsonify({
        'success': True,
        'orderId': order['orderId'],
        'customer': order['customer'],
        'items': items,
        'policyDays': policy.get('policyDays', 30),
        'prepaidLabel': True
    })


@api.route('/returns/generate-slip', methods=['POST'])
def generate_slip():
    data = request.get_json() or {}
    order_id = data.get('orderId', '')
    item_name = data.get('itemName', '')

    rma_code = f"RMA-{abs(hash(order_id + item_name)) % 100000:05d}-RET"
    _deflection['count'] += 1
    _deflection['total'] += 1
    return jsonify({
        'success': True,
        'rmaCode': rma_code,
        'orderId': order_id,
        'itemName': item_name,
        'barcode': '||| | |||| | |||||| || | ||| ||||',
        'carrier': 'FedEx Parcel Return',
        'instructions': 'Drop off at any FedEx location or show QR code at a partner store.'
    })


# ---- Category 3: Stock & Availability ----

@api.route('/inventory', methods=['GET'])
def get_inventory():
    query = request.args.get('q', '').strip()
    results = db.search_inventory(query)
    if not results:
        return jsonify({
            'success': False,
            'error': f"No products found matching '{query}'."
        }), 404

    _deflection['count'] += 1
    _deflection['total'] += 1
    return jsonify({'success': True, 'results': results})


@api.route('/inventory/notify', methods=['POST'])
def notify_restock():
    data = request.get_json() or {}
    email = data.get('email', '')
    sku = data.get('sku', '')
    return jsonify({
        'success': True,
        'message': f"Subscribed {email} for restock alerts on {sku}."
    })


# ---- Escalation Ticket ----

@api.route('/support-ticket', methods=['POST'])
def submit_ticket():
    data = request.get_json() or {}
    ticket_id = f"TKT-{abs(hash(str(data))) % 10000:04d}"
    _deflection['total'] += 1
    return jsonify({
        'success': True,
        'ticketId': ticket_id,
        'message': 'Our support team will respond within 4 business hours.'
    })
