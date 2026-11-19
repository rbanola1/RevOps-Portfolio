# Decision log

| # | Decision | Reason | Revisit when |
|---|---|---|---|
| 1 | The product data hub is the only place products are created and edited | Matching on product ID needs one source; two catalogues caused mismatches | A product line needs a different structure |
| 2 | Hub feeds the store and the CRM one way; each product carries both a store ID and a CRM ID | Each system matches on a key; the store never edits product data | A second store is added |
| 3 | The store's own product sync into the CRM is off | Redundant once the hub feeds the CRM | Never |
| 4 | Product sync and contact sync between the CRM and accounting are off | Two product lists and two contact lists caused duplicates and conflicts | Accounting needs customer-account data in the CRM, designed with clear ownership |
| 5 | Invoices flow from accounting to the CRM only | Sales needs paid and unpaid status without asking finance; accounting should not write to the CRM otherwise | Volume makes manual checks unnecessary |
| 6 | Tax-exempt status is owned by the product data hub, mirrored to the store and the ERP, with a backup copy in the CRM | One owner for a compliance-critical field; downstream systems read it | A tax engine is added |
| 7 | Marketplace purchase orders and distributor orders enter the ERP through an order desk using approved templates keyed on PO number | Gives every channel the same order record and invoice path; automation is not justified at current volume | Channel orders exceed what manual entry handles reliably |
| 8 | The ERP feeds accounting directly; the CRM does not sit between them | Fewer hops and fewer places for amounts to drift | Never |
| 9 | Lead tools never sync into the CRM; imports are reviewed, tagged and suppression-checked | Protects data quality and ownership rules | Import volume justifies a tested, monitored connector |
| 10 | The BI connection is read only | Dashboards must never write back | Never |
| 11 | Field mapping is reviewed with each system owner before go-live | Prevents silent data loss such as tax status | Each time a mapped field changes |
| 12 | Build each connection switched off, test on a few orders, then switch on | Safe rollout without a sandbox | Always |
