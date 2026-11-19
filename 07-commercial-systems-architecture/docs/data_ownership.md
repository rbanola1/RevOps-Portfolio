# Data ownership

| Object | System of record | Owner (role) | Others may |
|---|---|---|---|
| Product (ID, name, size, price, classification codes) | Product data hub | Product management | Read |
| Tax-exempt status | Product data hub | Finance | Read; copies held in the ERP, store and CRM |
| Lead and verified email | Lead tools and verifier, then the CRM after import | Commercial operations | Read |
| Contact, company, deal, ticket | CRM | Commercial operations | Read |
| Web order | Online store, then ERP | Operations | Read |
| Marketplace and distributor order | ERP (entered by the order desk) | Operations | Read |
| Inventory and shipment | ERP | Operations | Read |
| Invoice and payment | Accounting | Finance | Read; status mirrored to the CRM |
| Revenue reporting | BI | Commercial operations | Read |

## Rules
- Fix data at the system of record, never in a downstream copy.
- A field has one owner. Disagreements are raised to the owner, not overwritten.
- Document who may write to the CRM (people, workflows, integrations, import files) before adding a new writer.
- Changes to a product ID, order number format, PO format or customer key need sign-off from every system owner.
- Customs and classification codes are never edited outside the product data hub.
