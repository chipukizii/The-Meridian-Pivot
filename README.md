# 🧭 The Meridian Pivot: Event Check-in & Async Badge Printing Architecture

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Framework-Flask-black?logo=flask)](https://flask.palletsprojects.com/)
[![GraphQL](https://img.shields.io/badge/API-GraphQL%20%26%20REST-e10098?logo=graphql)](https://graphql.org/)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(6%2F6)-brightgreen?logo=pytest)](test_day4_pivot_build.py)
[![Security](https://img.shields.io/badge/Auth-HMAC--SHA256-orange?logo=security)](message_queue.py)

An event kiosk microservice built to handle high-concurrency attendee check-ins and resilient badge printing under realistic, mid-sprint industry constraints.

---

## 📌 1. The Challenge (What We Were Solving)

During live deployment of an event check-in service for **Solstice Events Co.** / **Northstar Retail Co.**, the badge-printer hardware vendor announced an immediate, non-negotiable deprecation of their synchronous REST print API (`POST /api/printer/print-job-sync`) with zero deadline extensions.

### Core Problems:
1. **Hardware Latency & Kiosk Lockups**: The legacy synchronous model forced the check-in terminal to hang until physical printer hardware confirmed printing, creating massive attendee queue bottlenecks.
2. **Hard Deprecation (`410 Gone`)**: Any attempt to make synchronous printer calls had to permanently return `HTTP 410 Gone`.
3. **Double-Scan Vulnerability**: In an asynchronous environment where print jobs execute out-of-order, multiple kiosk scans by impatient attendees risked duplicate badges and wasted hardware stock.
4. **Untrusted Callbacks**: Asynchronous vendor printer events needed cryptographic verification to prevent spoofed or replay check-in confirmations.

---

## ⚙️ 2. The Solution (How We Solved It)

Within a 48-hour mid-sprint pivot window, the system was re-architected from a synchronous blocking model into an **Asynchronous Message Queue & HMAC Webhook Callback Architecture**.

### Architecture Workflow:

```
[Attendee Scans QR at Kiosk]
             │
             ▼
   POST /api/kiosk/checkin
             │
             ├──► [State Check] ── (Already PENDING or CHECKED_IN?) ──► REJECT (HTTP 400 Duplicate)
             │
             ▼
  [message_queue.py]
  Enqueues print job & returns PENDING_PRINT immediately to kiosk (< 50ms)
             │
             ▼ (Async Job Processing)
   [Badge Printer Daemon]
             │
             ▼ (HMAC-SHA256 Signed Webhook)
  POST /api/webhooks/badge-printed
             │
             ├──► [Verify X-Printer-Signature HMAC] ── (Invalid?) ──► REJECT (HTTP 401)
             │
             ▼
   [State Machine: db.py]
   Transition: PENDING_PRINT ──► CHECKED_IN (Idempotent update)
```

---

## 🚀 3. Key Technical Implementations

### 1. Synchronous API Deprecation (`routes.py`)
Permanently retired the blocking endpoint to satisfy vendor deprecation constraints:
```python
@app.route("/api/printer/print-job-sync", methods=["POST"])
def deprecated_sync_print():
    return jsonify({
        "error": "DEPRECATED_ENDPOINT",
        "status": "KILLED",
        "message": "The synchronous badge-printer API has been deprecated per Day 4 pivot."
    }), 410
```

### 2. Decoupled Message Queue (`message_queue.py`)
Introduced `BadgePrinterMessageQueue` to accept print jobs asynchronously, allowing the front-end kiosk to complete check-ins instantly and poll status non-blockingly.

### 3. Strict 3-Stage State Machine & Duplicate Protection (`db.py`)
State transitions:
$$\text{REGISTERED} \longrightarrow \text{PENDING\_PRINT} \longrightarrow \text{CHECKED\_IN}$$
- Prevents duplicate prints by rejecting scans if the attendee is already in `PENDING_PRINT` or `CHECKED_IN` (`DUPLICATE_SCAN_REJECTED`, `400 Bad Request`).
- Implements **idempotency guards** on webhook ingestion: duplicate or out-of-order vendor callbacks do not trigger duplicated badge issuance.

### 4. Cryptographic Callback Security (`routes.py`)
Vendor webhooks are authenticated via **HMAC-SHA256 signatures** (`X-Printer-Signature`) using a shared secret, rejecting untrusted or tampered payloads.

### 5. Unified GraphQL Layer (`graphql_schema.py`)
Provided frontend kiosks with unified mutations and queries:
- `mutation scanAttendeeQr(ticketId: "...")`: Triggers async check-in and queues print jobs.
- `query attendeeStatus(ticketId: "...")`: Allows kiosks to poll print progress in real-time.

---

## 🧪 4. Automated Verification & Test Coverage

Full test suite with 100% pass rate across edge cases:

```bash
python -m unittest test_day4_pivot_build.py
```

| Test Case | Scenario Verified | Status |
| :--- | :--- | :---: |
| `test_sync_endpoint_deprecated` | Confirms `POST /api/printer/print-job-sync` returns `410 Gone` | ✅ PASS |
| `test_kiosk_checkin_pending_state` | Verifies kiosk check-in enqueues job and returns `PENDING_PRINT` | ✅ PASS |
| `test_duplicate_scan_protection` | Verifies subsequent scans during print return `DUPLICATE_SCAN_REJECTED` | ✅ PASS |
| `test_webhook_hmac_security` | Blocks invalid HMAC signatures (`401`) and confirms valid payloads | ✅ PASS |
| `test_graphql_mutations` | Verifies `scanAttendeeQr` and status resolution | ✅ PASS |
| `test_full_lifecycle` | End-to-end multi-attendee test (`ATT-1001` to `ATT-1003`) | ✅ PASS |

---

## 📁 5. Repository Structure

```
├── app.py                     # Main application entry point
├── routes.py                  # Kiosk, webhook, and deprecated REST routes
├── db.py                      # Thread-safe database state machine & duplicate guards
├── message_queue.py           # In-memory async print queue with HMAC signing
├── graphql_schema.py          # GraphQL query and mutation schemas
├── test_day4_pivot_build.py   # Comprehensive automated test suite
├── DAY4_PIVOT_LOG.md          # Architectural pivot rationale & delta log
└── ASSIGNMENT2_SCOPE_DELTA.md # Scope delta and trade-off analysis report
```
