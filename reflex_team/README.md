# Reflex — Delivery Synchronization Platform
> Real-time delivery tracking for small urban retailers in Kenya.
> Built during Reflex: The Readiness Sprint.

---

## System Overview

Reflex connects three personas into one synchronized delivery ledger:

| Persona | Role | Device |
|:---|:---|:---|
| **Retailer Staff** | Logs delivery requests | Shop tablet / desktop |
| **Dispatcher** | Assigns orders to riders | Control cockpit monitor |
| **Field Rider** | Updates status & verifies delivery via OTP | Budget Android smartphone |

---

## Team Members & File Ownership (5 Members)

> Each member owns their assigned file(s). **Do NOT edit another member's file.**
> Commit only your own assigned work.

| Member | Role | Assigned File(s) | Responsibility |
|:---|:---|:---|:---|
| **Member 1** | Backend Core & Data Engine | `backend/db.py` | In-memory data store, Order FSM state machine, Customer OTP generation, concurrency guards |
| **Member 2** | Backend API & Integration | `backend/app.py` | Flask REST API routes, request parsing, JSON responses, error handling |
| **Member 3** | Frontend UI & Interaction | `frontend/static/index.html` | 3-column dashboard, persona view switcher, order forms, real-time polling logic |
| **Member 4** | Frontend Styling & Theming | `frontend/static/styles.css` | Modern CSS grid, dark/light mode variables, mobile phone frame, status badges |
| **Member 5** | QA Testing & Technical Docs | `tests/test_reflex.py`<br>`docs/TRADE_OFF_LOG.md`<br>`docs/ARCHITECTURE.md` | Automated test suite (8 tests), Trade-off justification log, Architecture specification |

---

## Folder Structure

```
reflex_team/
├── backend/
│   ├── app.py          → Member 2: Flask REST API server
│   └── db.py           → Member 1: State machine & data store
├── frontend/
│   └── static/
│       ├── index.html  → Member 3: Dashboard UI & persona switcher
│       └── styles.css  → Member 4: Styling, dark/light theme, mobile frame
├── tests/
│   └── test_reflex.py  → Member 5: Automated test suite (8 tests)
├── docs/
│   ├── TRADE_OFF_LOG.md    → Member 5: Architectural trade-off log
│   └── ARCHITECTURE.md     → Member 5: System architecture document
├── requirements.txt    → Shared (do not modify without team agreement)
└── README.md           → Team guide & role assignments
```

---

## How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python backend/app.py

# 3. Open the dashboard
# Visit: http://127.0.0.1:5050

# 4. Run tests
python tests/test_reflex.py
```

---

## Git Workflow (Per Member)

```bash
# Step 1: Pull latest before starting
git pull origin main

# Step 2: Work ONLY on your assigned file(s)
# Step 3: Stage only your file(s)
git add backend/db.py          # (replace with your file)

# Step 4: Commit with a clear message
git commit -m "feat(db): implement state machine and OTP generation - Member 1"

# Step 5: Push
git push origin main
```

---

## Order Status Flow

```
PENDING_DISPATCH  →  ASSIGNED  →  PICKED_UP  →  DELIVERED
```

---

## Tech Stack

- **Backend**: Python 3.12 / Flask
- **Frontend**: Vanilla HTML, CSS, JavaScript
- **Database**: In-memory relational store
- **Auth/Verification**: 4-digit SMS OTP per order
- **Sync**: HTTP polling every 4 seconds
