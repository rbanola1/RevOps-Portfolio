# CRM and accounting integration

## Goal
Show finance and customer data together: revenue next to pipeline, invoices next to deals, open balances next to account owners.

## How it works
| Item | Rule |
|---|---|
| Direction | Accounting system to CRM for invoice and payment status; CRM to accounting system for new customer records |
| Match key | One customer ID created once and stored in both systems |
| Frequency | Invoices and payments nightly; new customers on creation |
| Source of truth | Money: accounting system. Relationships, deals and activity: CRM |
| Reporting layer | Both feed one BI model through the same customer and date tables |

## Field map (illustrative)
| CRM field | Accounting field | Rule |
|---|---|---|
| Company ID | Customer ID | Created in the CRM, copied to accounting |
| Company name | Customer name | One standard format; changed in the CRM first |
| Billing contact | Billing email | Verified before invoicing |
| Deal amount at close | Invoice total | Compared at reconciliation; differences explained |
| Close date | Invoice date | Compared; gap is the won-to-invoiced time |
| Payment status | Payment status | Read-only in the CRM |

## Checks
- Nightly count of customers in both systems; mismatches go to the owner.
- Weekly list of won deals with no invoice after five business days.
- Monthly total of invoiced revenue in the BI model equals the accounting report to the dollar.
- Duplicate customers are merged in the CRM first, then in accounting, using the customer ID.

## Owners
| Step | Owner |
|---|---|
| Customer creation rules | Commercial operations |
| Invoice and payment data | Finance |
| Integration settings | Commercial operations |
| BI model | Commercial operations |
