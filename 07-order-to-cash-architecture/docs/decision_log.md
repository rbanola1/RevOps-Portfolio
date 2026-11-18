# Decision log

| # | Decision | Reason | Revisit when |
|---|---|---|---|
| 1 | Orders flow store to ERP to accounting, one way | Removes re-keying and keeps one order record | A second sales channel is added |
| 2 | Invoice status flows from accounting back to the CRM | Sales needs paid and unpaid status without asking finance | Volume makes manual checks unnecessary |
| 3 | Product sync between CRM and accounting is off | Two product lists caused mismatches and duplicates | Product database becomes the single catalogue for both |
| 4 | Contact sync between CRM and accounting is off | Accounting should not create or change CRM contacts | A customer-account sync is designed with clear ownership |
| 5 | Product database is the only place products are created | Matching on product ID needs one source | A new product line needs a different structure |
| 6 | The BI connection is read only | Dashboards must never write back | Never |
| 7 | Field mapping is reviewed with each system owner before go-live | Prevents silent data loss such as tax status | Each time a mapped field changes |
| 8 | Build the connection switched off, test on a few orders, then switch on | Safe rollout without a sandbox | Always |
