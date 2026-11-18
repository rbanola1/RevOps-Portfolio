# Data ownership

| Object | System of record | Owner (role) | Others may |
|---|---|---|---|
| Product (ID, name, size, list price) | Product database | Product management | Read |
| Order and shipment | ERP | Operations | Read |
| Invoice and payment | Accounting | Finance | Read |
| Contact, company, deal, ticket | CRM | Commercial operations | Read |
| Customs and classification codes | Product database | Operations | Read only, never edited elsewhere |
| Tax-exempt status | Accounting, mirrored to the store | Finance | Read |
| Revenue reporting | BI | Commercial operations | Read |

## Rules
- Fix data at the system of record, never in a downstream copy.
- A field has one owner. Disagreements are raised to the owner, not overwritten.
- Document who may write to the CRM (people, workflows, integrations, enrichment tools) before adding any new writer.
- Changes to a product ID, order number format or customer key need sign-off from every system owner.
