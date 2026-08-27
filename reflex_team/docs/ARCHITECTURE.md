# Reflex: System Architecture Document
# OWNER: Member 5 (QA Testing & Technical Documentation)
# RESPONSIBILITY: Document the full system architecture chosen for Reflex

---

## Architecture Pattern

TODO — State which primary architecture pattern was used (e.g. Layered / N-Tier, REST, etc.)

---

## Layer Breakdown

```
TODO — Draw the layer diagram, e.g.:

┌─────────────────────────────────────────┐
│         Presentation Layer              │
├─────────────────────────────────────────┤
│         Application Layer (API)         │
├─────────────────────────────────────────┤
│         Business Logic / State Machine  │
├─────────────────────────────────────────┤
│         Data Layer                      │
└─────────────────────────────────────────┘
```

---

## API Endpoints

TODO — List all 10 REST endpoints with method, path, and persona

| Method | Endpoint | Persona |
|:---|:---|:---|
| TODO | TODO | TODO |

---

## State Machine

TODO — Diagram the Order state transitions

```
PENDING_DISPATCH → ASSIGNED → PICKED_UP → DELIVERED
```

Explain each transition guard and what blocks an invalid transition.

---

## Sync Strategy

TODO — Explain HTTP polling and why WebSockets were not used

---

## Proof of Delivery

TODO — Explain the SMS OTP challenge-response pattern

---

## Development Methodology

TODO — State which methodology was used (Agile Scrum) and map sprint events to project days
