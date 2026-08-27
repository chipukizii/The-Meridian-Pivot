# backend/app.py
# OWNER: Member 2
# RESPONSIBILITY: Flask REST API server — all routes, request parsing, JSON responses
#
# TODO — Member 2, implement the following endpoints:
#
#   [ ] GET  /                          — serve frontend/static/index.html
#   [ ] GET  /api/orders                — list all orders (optional ?status= filter)
#   [ ] POST /api/orders                — retailer creates a new delivery request
#   [ ] GET  /api/orders/<id>/tracking  — tracking view with audit trail
#   [ ] GET  /api/dispatch/unassigned   — dispatcher views unassigned queue + available riders
#   [ ] POST /api/dispatch/assign       — dispatcher assigns order to rider
#   [ ] GET  /api/riders/<id>/tasks     — rider views their assigned tasks
#   [ ] POST /api/riders/pickup         — rider confirms package pickup
#   [ ] POST /api/riders/deliver        — rider submits OTP to verify delivery
#   [ ] POST /api/system/reset          — reset system to seed state for demos
#
# Required fields for POST /api/orders:
#   customer_name, customer_phone, dropoff_address, item_desc
#
# Return format for all endpoints:
#   { "success": true/false, "message": "...", "data": {...} }


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import db

app = Flask(__name__, static_folder='../frontend/static')
CORS(app)


# --- Retailer Endpoints ---

@app.route('/')
def index():
    # TODO: serve index.html
    pass


@app.route('/api/orders', methods=['GET'])
def list_orders():
    # TODO: return all orders, filter by ?status= if provided
    pass


@app.route('/api/orders', methods=['POST'])
def create_delivery_request():
    # TODO: validate required fields, call db.create_order(), return 201
    pass


@app.route('/api/orders/<order_id>/tracking', methods=['GET'])
def get_order_tracking(order_id):
    # TODO: return order + assigned rider + audit trail
    pass


# --- Dispatcher Endpoints ---

@app.route('/api/dispatch/unassigned', methods=['GET'])
def get_unassigned_queue():
    # TODO: return unassigned orders + available riders
    pass


@app.route('/api/dispatch/assign', methods=['POST'])
def assign_order():
    # TODO: read order_id + rider_id, call db.assign_order_to_rider()
    pass


# --- Rider Endpoints ---

@app.route('/api/riders/<rider_id>/tasks', methods=['GET'])
def get_rider_tasks(rider_id):
    # TODO: return all orders assigned to this rider
    pass


@app.route('/api/riders/pickup', methods=['POST'])
def rider_pickup():
    # TODO: call db.rider_pickup_order()
    pass


@app.route('/api/riders/deliver', methods=['POST'])
def rider_deliver():
    # TODO: call db.verify_and_deliver_order() with OTP check
    pass


# --- System ---

@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    # TODO: call db.reset_db(), return success message
    pass


if __name__ == '__main__':
    print("\n=======================================================")
    print("  REFLEX: Delivery Synchronization Service Running")
    print("  Live Interactive Dashboard: http://127.0.0.1:5050")
    print("=======================================================\n")
    app.run(port=5050, debug=True)
