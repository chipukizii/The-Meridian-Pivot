# Day 4: Mid-Sprint Pivot Architecture Report (Solstice Events Co.)

**Client**: Solstice Events Co. (Multi-Day Tech Conference Kiosk Service)  
**Scenario**: Transition from Synchronous Badge Printing to Asynchronous Message Queue + Webhook Callback Model  
**Non-Negotiable Constraint**: Synchronous API permanently deprecated (`410 Gone`). Zero deadline extensions. Duplicate-scan protection must hold under async out-of-order execution.  

---

## 1. Executive Summary & Pivot Delta

The badge-printer vendor announced the immediate deprecation of the synchronous print API (`POST /api/printer/print-job-sync`). We rebuilt the kiosk service around an **Asynchronous Message Queue & Webhook Callback Architecture**.

```
[Staff Scans QR Code] ──> POST /api/kiosk/checkin
                                │
                                ▼
               ┌───────────────────────────────────┐
               │ Check Duplicate Scan Protection   │
               └────────────────┬──────────────────┘
                                │ Pass (Initial Status: PENDING_PRINT)
                                ▼
               ┌───────────────────────────────────┐
               │ [message_queue.py] Publish Job    │
               └────────────────┬──────────────────┘
                                │ Async Queue Event
                                ▼
               ┌───────────────────────────────────┐
               │ Vendor Badge Printer Daemon       │
               └────────────────┬──────────────────┘
                                │ HMAC Signed Webhook Callback
                                ▼
               ┌───────────────────────────────────┐
               │ POST /api/webhooks/badge-printed  │
               └────────────────┬──────────────────┘
                                │ Verify HMAC Signature & Confirm Print
                                ▼
               ┌───────────────────────────────────┐
               │ Final Status: CHECKED_IN          │
               └───────────────────────────────────┘
```

---

## 2. Core Architectural Changes & Modules Implemented

### 1. Deprecation of Synchronous Printing (`routes.py`)
- Route `POST /api/printer/print-job-sync` now returns `HTTP 410 Gone`:
  ```json
  {
    "error": "DEPRECATED_ENDPOINT",
    "status": "KILLED",
    "message": "The synchronous badge-printer API has been deprecated per the Day 4 pivot."
  }
  ```

### 2. Message Queue Buffer (`message_queue.py`)
- Asynchronous badge printer queue module (`BadgePrinterMessageQueue`) that accepts enqueued print jobs (`publish_print_job`) and generates cryptographic HMAC-SHA256 signatures (`X-Printer-Signature`) for callback delivery.

### 3. Duplicate-Scan Protection & State Machine (`db.py`)
- State machine: `REGISTERED` ──> `PENDING_PRINT` ──> `CHECKED_IN`.
- **Duplicate Protection**: When a QR code is scanned, `db.initiate_attendee_checkin()` verifies whether the attendee is already in `PENDING_PRINT` or `CHECKED_IN`. If so, it immediately rejects the scan (`DUPLICATE_SCAN_REJECTED`, `HTTP 400 Bad Request`), preventing duplicate badge printing.

### 4. Asynchronous Webhook Ingestion (`routes.py`)
- Endpoint: `POST /api/webhooks/badge-printed`
- Validates HMAC-SHA256 signatures (`X-Printer-Signature`) using shared secret `WEBHOOK_SECRET`.
- Updates attendee state to `CHECKED_IN`, sets `badgePrinted = True`, assigns `badgeId`, and updates sync metadata.
- **Idempotency Guard**: Out-of-order or duplicate webhook callbacks for the same attendee return current `CHECKED_IN` state safely without duplicate processing.

---

## 3. Scope Delta Analysis Matrix (Assignment 2 Requirement)

| Feature / Endpoint | Status | Architectural Rationale |
| :--- | :--- | :--- |
| **POST /api/printer/print-job-sync** | **DROPPED / KILLED** | Marked `410 Gone` to satisfy non-negotiable deprecation rule. |
| **POST /api/kiosk/checkin** | **ADDED** | Enqueues print jobs onto `message_queue.py` and returns `PENDING_PRINT`. |
| **POST /api/webhooks/badge-printed** | **ADDED** | Webhook callback endpoint with HMAC security validation. |
| **Duplicate-Scan Protection** | **MODIFIED** | Updated state checks to block duplicates while status is `PENDING_PRINT` or `CHECKED_IN`. |
| **GraphQL Schema & Mutation** | **ADDED** | Added `scanAttendeeQr` mutation and `attendeeStatus` query in `graphql_schema.py`. |

---

## 4. Automated Verification & Test Results (`test_day4_pivot_build.py`)

Executed 6 automated tests covering all Solstice Events Co requirements:

```text
......
----------------------------------------------------------------------
Ran 6 tests in 0.288s

OK (Deprecated Sync Endpoint, Kiosk Pending State, Duplicate Protection, HMAC Webhook Validation, GraphQL Integration, 3 Attendees Lifecycle)
```

- [x] **Test 1**: Synchronous printer returns `HTTP 410 Gone`.
- [x] **Test 2**: Staff scan QR returns `PENDING_PRINT`.
- [x] **Test 3**: Duplicate scan attempt rejected with `DUPLICATE_SCAN_REJECTED`.
- [x] **Test 4**: Invalid HMAC signature returns `HTTP 401 Unauthorized`; valid HMAC signature sets status to `CHECKED_IN`.
- [x] **Test 5**: GraphQL `scanAttendeeQr` mutation and `attendeeStatus` query resolve cleanly.
- [x] **Test 6**: Full lifecycle across all 3 test attendees (`ATT-1001`, `ATT-1002`, `ATT-1003`).
