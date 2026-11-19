# Layers

## 1 Lead generation
| Component | Role |
|---|---|
| Academic contact and grant database | Keyword-based lead lists by cell type and application; strongest for academic contacts |
| Enrichment platform | Email lookups across several data providers plus AI fit checks; used where free sources cannot find a contact |
| Free scientific sources | Grant databases, literature databases and researcher identifiers; the best source for academic leads |
| Email verifier | Every list is verified before import |

Rules: every candidate passes the CRM suppression check first; no tool syncs into the CRM automatically; every import carries a lead source tag; all email is sent from the CRM.

## 2 CRM and engagement
Contacts, companies, deals, tickets, sequences and marketing email. Reps own accounts by territory. Marketing-contact capacity is managed against a tier limit, with inactive imports moved to non-marketing rather than deleted.

## 3 Product and pricing data
| Component | Role |
|---|---|
| Product data hub | System of record for product IDs, names, sizes, prices, classification codes and tax-exempt status; feeds the CRM (about every minute) and the store (about every five minutes) |
| Pricing sheets | One sheet per marketplace, generated from the hub in the platform's own format, with a discrepancy check against the master |

Every product carries a store ID and a CRM ID inside the hub, so each system matches products on a key rather than on a name.

## 4 Sales channels
| Channel | How it works |
|---|---|
| Online store | Customers order and pay online; orders flow to the ERP |
| B2B marketplaces and procurement platforms | Listings built from the product hub; customers send purchase orders through the platform |
| Distributors | Territory partners with their own price list; orders arrive by purchase order |
| Direct sales | Reps work accounts in the CRM; quotes become orders through the same ERP path |

## 5 Orders, fulfilment and finance
| Component | Role |
|---|---|
| ERP | Inventory and order management; the single order record for every channel |
| Order desk | Enters marketplace and distributor orders into the ERP from an approved template keyed on PO number |
| Accounting | Invoices customers and returns invoice status and paid date to the CRM |

## 6 Reporting
BI dashboards read from the CRM through a read-only connection. Nothing is written back. A monthly reconciliation compares CRM, ERP and invoice totals.

## Target-state note
As volume grows, channel order entry can move from templates to automated purchase-order intake. The ERP already feeds accounting directly, so the CRM needs only invoice status, which keeps the CRM free of accounting detail.
