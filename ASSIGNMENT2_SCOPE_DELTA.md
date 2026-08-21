# Assignment 2: Mid-Sprint Scope Delta Analysis & Deliverable Report

**Project**: Solstice Events Co. & Northstar Support Kiosk MVP  
**Sprint Phase**: Day 5 — Refactor & Final Review  
**Team / Individual Submission**: Solo Engineer (GraphQL & Async Queue Specialist)  

---

## 1. Executive Summary & Pivot Adaptation

During Sprint 2 (Day 4), the client delivered a non-negotiable pivot: **The synchronous badge-printer REST API was permanently deprecated (`HTTP 410 Gone`)**. 

Our team successfully refactored the architecture within the 48-hour deadline into an **Asynchronous Message Queue & Webhook Callback Model** without breaking pre-existing query APIs.

---

## 2. Scope Delta Matrix (Dropped, Modified, Added Features)

| Feature / Module | Original Spec (Day 3) | New Spec (Day 4–5 Pivot) | Status | Architectural Impact & Rationale |
| :--- | :--- | :--- | :---: | :--- |
| **Sync Printer API (`POST /api/printer/print-job-sync`)** | Synchronous REST call waiting for printer ACK | Endpoint returns `410 Gone (Killed)` | **DROPPED** | Removed synchronous blocking thread to meet non-negotiable client pivot rule. |
| **5-Min Warehouse Polling Engine (`polling_service.py`)** | Polled warehouse every 300 seconds | Retired / Deprecated | **DROPPED** | Replaced pull-based polling with push-based webhook events. |
| **Kiosk QR Scan Check-In (`POST /api/kiosk/checkin`)** | Immediatly set status to `CHECKED_IN` | Returns `PENDING_PRINT` status & enqueues job | **ADDED** | Decouples check-in UI from printer hardware latency via `message_queue.py`. |
| **Duplicate-Scan Protection Guard** | Checked if `CHECKED_IN` | Rejects if status is `PENDING_PRINT` OR `CHECKED_IN` | **MODIFIED** | Prevents duplicate badge printing even when callbacks arrive out of order. |
| **Webhook Callback (`POST /api/webhooks/badge-printed`)** | Non-existent | HMAC-SHA256 authenticated callback handler | **ADDED** | Receives vendor print confirmation and transitions attendee to `CHECKED_IN`. |
| **GraphQL Check-In Schema** | Inventory lookups only | Added `scanAttendeeQr` & `attendeeStatus` | **ADDED** | Enables single-query kiosk state resolution for frontend clients. |

---

## 3. Architectural Integrity & Regression Protection

To guarantee that the mid-sprint refactor did not break existing features, we conducted regression checks across all system layers:

1. **API Contract Compatibility**:
   - `GET /api/inventory` continues serving cached stock lookups seamlessly.
   - `query { checkStock(sku: "SKU-SHOE-01") }` resolves without schema breaking changes.
2. **State Machine Integrity**:
   - Validated state transitions: `REGISTERED` ──> `PENDING_PRINT` ──> `CHECKED_IN`.
   - Verified that invalid ticket IDs return `404 Not Found` and missing signatures return `401 Unauthorized`.
3. **Idempotency Guard**:
   - Verified that duplicate webhook callbacks for the same `jobId` do not generate duplicate badges or corrupt timestamps.

---

## 4. Technical Trade-Off Documentation & Backlog Refactoring

### Trade-Off #1: In-Memory Message Queue vs. Distributed Broker (RabbitMQ/Kafka)
- **Context**: 48-hour time constraint on Day 4 pivot.
- **Decision**: Implemented an in-memory queue module (`message_queue.py`) with thread locking and HMAC payload signing instead of deploying an external RabbitMQ container.
- **Impact**: Zero external dependency overhead, meeting the tight deadline while fulfilling async decoupling requirements.

### Trade-Off #2: HMAC-SHA256 Signature Guard vs. OAuth2 Tokens
- **Context**: Need to authenticate vendor webhook callbacks securely.
- **Decision**: Implemented HMAC-SHA256 signature validation via header `X-Printer-Signature`.
- **Impact**: Lightweight, cryptographic verification without requiring token refresh handshakes.

---

## 5. Definition of Done & Verification Evidence

All 14 unit and integration tests across Days 1, 3, 4, and 5 passed cleanly:

```text
...............
----------------------------------------------------------------------
Ran 14 tests in 0.420s

OK
```
