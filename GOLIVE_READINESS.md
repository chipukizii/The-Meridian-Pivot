# Northstar Retail Co. - Support Deflection MVP: Go-Live Readiness Note

**Document Status**: Final Handoff  
**Target Client**: Northstar Retail Co. Support & Engineering Team  
**Scope**: 1-Week Pod Working Simulation Deliverable  

---

## 1. Executive Summary
This 1-page note outlines the operational state of the Support Deflection MVP delivered by our 4–5 person pod. The solution is designed to reduce incoming support ticket volume across Northstar's three highest-frequency inquiry types: **Order Status**, **Returns & Refunds**, and **Stock Availability**.

---

## 2. What Works (Fully Functional MVP Features)

| Ticket Category | Shipped Feature | Operational Behavior |
| :--- | :--- | :--- |
| **Category 1: Order Status** | Self-Serve Order Tracking | Customers input an Order ID (e.g. `ORD-1001`) to view a step-by-step visual shipment timeline, carrier details, and estimated delivery dates without contacting support. |
| **Category 2: Returns & Refunds** | Automated Return Label & QR Slip | Customers can view eligible items from delivered orders, initiate returns, generate a pre-paid printable return slip/QR code, and estimate refund timelines. |
| **Category 3: Stock Availability** | SKU & Size Inventory Checker | Customers can search by item name or SKU to check size availability across stores/warehouses and register for back-in-stock email notifications. |
| **Deflection Tracking** | Real-Time Deflection Counter | Live metric header badge calculates the percentage and volume of queries resolved self-serve versus human ticket escalations. |
| **Escalation Support** | Pre-Filled Escalation Modal | If a customer's query cannot be resolved self-serve, a pre-filled ticket form captures context for human agents. |

---

## 3. What is Known-Broken / Out of Scope for MVP

1. **Static JSON Mock Data**: The MVP currently fetches data from static JSON stores (`data/orders.json`, `data/inventory.json`, `data/returns.json`). It does not connect to a live database.
2. **Third-Party Carrier APIs**: Carrier tracking links and status events are simulated rather than hooked up to live FedEx/UPS webhooks.
3. **Email Notification Service**: Back-in-stock alerts and email return slips show user confirmations but require SMTP service integration to send real emails.

---

## 4. Handoff Guide for Northstar's Engineering Team

To pick up and deploy this solution without our team in the room:

1. **Replace Mock API Calls**:
   - In `app.js`, replace the `fetch('data/*.json')` calls with Northstar's internal REST or GraphQL endpoints (e.g. `/api/v1/orders/:id`).
2. **Configure Deflection Analytics**:
   - Update `registerDeflection()` in `app.js` to log events to Northstar's analytics platform (Google Analytics 4 / Segment / Mixpanel).
3. **Styling & Branding**:
   - Theme variables are centralized in `style.css` under `:root` for quick color and typography matching.
