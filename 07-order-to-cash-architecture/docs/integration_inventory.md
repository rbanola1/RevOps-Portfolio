# Integration inventory

| # | From | To | Data | Direction | Match key | Status |
|---|---|---|---|---|---|---|
| 1 | Online store | ERP | Web orders | One way | Order ID, with field mapping | Live |
| 2 | ERP | Accounting | Orders for invoice generation | One way | Order number | Live |
| 3 | Accounting | CRM | Invoice status and paid date | One way | Order number | Live |
| 4 | CRM | BI | All objects, read only | One way | Object IDs | Live |
| 5 | Product database | Online store | Product data | One way | Product ID | Live |
| 6 | Product database | CRM | Product catalogue | One way | Product ID | Live |
| 7 | CRM | Accounting | Product sync | Off | SKU | Switched off by design |
| 8 | CRM | Accounting | Contact sync | Off | Email | Switched off by design |
| 9 | Online store | CRM | Customer and order backup | One way | Email and order ID | Live |

## How to read it
- Every connection has exactly one direction and one match key.
- "Off" lines are recorded so nobody switches them on without reading the reason ([decision log](decision_log.md)).
- Statuses: Live, Switched off by design.
- Review the table whenever a system, field or process changes.
