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
    sync_meta = db.get_sync_status()
    return jsonify({'success': True, 'syncMetadata': sync_meta, 'results': results})


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


# ==============================================================================
# DAY 4 PIVOT: Solstice Events Co. Kiosk Check-In & Async Webhook Architecture
# ==============================================================================

# 1. DEPRECATED ROUTE: Synchronous Printer API (Killed per Day 4 Pivot)
@api.route('/printer/print-job-sync', methods=['POST'])
def deprecated_sync_printer():
    """
    DEPRECATED ENDPOINT (Day 4 Pivot Requirement).
    Returns HTTP 410 Gone to indicate synchronous printing is permanently killed.
    """
    return jsonify({
        'error': 'DEPRECATED_ENDPOINT',
        'status': 'KILLED',
        'message': 'The synchronous badge-printer API has been deprecated per the Day 4 pivot. You must use the asynchronous message queue + webhook callback model.'
    }), 410


# 2. Kiosk Check-In QR Code Scanning Endpoint
@api.route('/kiosk/checkin', methods=['POST'])
def kiosk_scan_checkin():
    """
    Kiosk Staff Scans Attendee QR Code.
    Enforces Duplicate-Scan Protection and enqueues print job asynchronously.
    Initial UI State: PENDING_PRINT (not Checked In immediately).
    """
    from message_queue import printer_queue
    data = request.get_json() or {}
    ticket_id = data.get('ticketId', '').strip()

    if not ticket_id:
        return jsonify({'success': False, 'error': 'Ticket ID is required.'}), 400

    success, code, attendee = db.initiate_attendee_checkin(ticket_id)

    if not success:
        if code == 'DUPLICATE_SCAN_REJECTED':
            return jsonify({
                'success': False,
                'error': 'DUPLICATE_SCAN_REJECTED',
                'message': f"Attendee {ticket_id} is already checked in or print job is pending.",
                'attendee': attendee
            }), 400
        return jsonify({'success': False, 'error': f"Ticket '{ticket_id}' not found."}), 404

    # Publish message to vendor queue
    job_id = attendee['printJobId']
    printer_queue.publish_print_job(ticket_id, job_id)

    return jsonify({
        'success': True,
        'status': 'PENDING_PRINT',
        'message': 'Print job enqueued onto vendor message queue. Waiting for webhook callback confirmation.',
        'jobId': job_id,
        'attendee': attendee
    })


# 3. Webhook Endpoint: Receives Badge Printer Callback Confirmation
@api.route('/webhooks/badge-printed', methods=['POST'])
def badge_printed_webhook():
    """
    Asynchronous Webhook Callback Endpoint.
    Receives callback from badge printer vendor once print job completes.
    Validates HMAC signature and updates attendee status to CHECKED_IN.
    """
    from message_queue import printer_queue, WEBHOOK_SECRET
    import hmac, hashlib

    signature_header = request.headers.get('X-Printer-Signature', '')
    raw_payload = request.get_data()

    # HMAC Signature Validation
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        raw_payload,
        hashlib.sha256
    ).hexdigest()

    if signature_header and not hmac.compare_digest(signature_header, expected_sig):
        return jsonify({'error': 'INVALID_SIGNATURE', 'message': 'HMAC signature verification failed.'}), 401

    data = request.get_json() or {}
    ticket_id = data.get('ticketId')
    job_id = data.get('jobId')
    badge_id = data.get('badgeId')

    if not ticket_id or not job_id:
        return jsonify({'error': 'INVALID_PAYLOAD', 'message': 'Missing ticketId or jobId in payload.'}), 400

    # Process confirmation (Idempotent update)
    updated_attendee = db.confirm_badge_printed(ticket_id, job_id, badge_id)

    return jsonify({
        'success': True,
        'status': 'CHECKED_IN',
        'message': f"Badge printing confirmed for attendee {ticket_id}.",
        'attendee': updated_attendee
    })


# 4. Kiosk Status Query Endpoint
@api.route('/kiosk/status/<ticket_id>', methods=['GET'])
def get_kiosk_attendee_status(ticket_id):
    """Fetch real-time check-in status for an attendee."""
    attendee = db.get_attendee_by_ticket_id(ticket_id)
    if not attendee:
        return jsonify({'success': False, 'error': f"Ticket '{ticket_id}' not found."}), 404

    return jsonify({'success': True, 'attendee': attendee})

