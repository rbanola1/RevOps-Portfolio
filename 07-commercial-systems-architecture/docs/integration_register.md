# Integration register

| # | From | To | Data | Direction | Match key | Status |
|---|---|---|---|---|---|---|
| 1 | Lead sources and verifier | CRM | Verified contacts with lead source tag | Reviewed import | Email and name, after suppression check | Live |
| 2 | CRM | BI dashboards | All objects, read only | One way | Object IDs | Live |
| 3 | Product data hub | CRM | Products | Hub to CRM, about 1 minute | Product ID | Live |
| 4 | Product data hub | CRM | Tax-exempt documents (backup) | Hub to CRM | Company ID | Live |
| 5 | Product data hub | Online store | Product data | Hub to store, about 5 minutes | Product ID | Live |
| 6 | Online store | ERP | Web orders | Store to ERP | Order ID with field mapping | Live |
| 7 | Order desk (templates) | ERP | Marketplace purchase orders and distributor orders | Entry from approved template | PO number | Live |
| 8 | ERP | Accounting | Orders for invoice generation | ERP to accounting | Order number | Live |
| 9 | Accounting | CRM | Invoice status and paid date | Accounting to CRM | Order number | Live |
| 10 | CRM | Accounting | Product sync | Off | SKU | Off by design |
| 11 | Accounting | CRM | Contact sync | Off | Email | Off by design |
| 12 | Online store | CRM | Product sync | Off | Product ID | Off by design |

The same register is available as data in `data/integration_inventory.csv`.

## How to read it
- Every connection has exactly one direction and one match key.
- "Off by design" rows are recorded so nobody turns them on without reading the reason in the [decision log](decision_log.md):
  - Row 10: products now come only from the product data hub, so a second product sync would create conflicts.
  - Row 11: accounting must not create or change CRM contacts; invoices flow one way instead.
  - Row 12: the store's product sync into the CRM became redundant when the hub began feeding both.
- Review the register whenever a system, field or process changes, and at least quarterly.
- Statuses: Live, Off by design.
