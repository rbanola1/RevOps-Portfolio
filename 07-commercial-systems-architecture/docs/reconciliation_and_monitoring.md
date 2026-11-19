# Reconciliation and monitoring

## Monthly three-way check
Compare, by month: CRM closed-won amount, ERP order amount, accounting invoice amount.
Report the gap in dollars and percent, plus the share of orders with at least one exception.

## Exception types
| Exception | Typical cause | Owner | Fix |
|---|---|---|---|
| Product ID missing or mismatched | Product created in one system only | Product management | Correct at the product database and re-sync |
| Tax-exempt flag not carried over | Status set in accounting but not mirrored | Finance | Add the field to the mapping, backfill |
| Duplicate customer record | Same person created through two entry points | Commercial operations | Merge, then add a match rule on email |
| Amount differs between systems | Manual edit or discount applied in one place | Finance and sales | Trace to the edit, fix the source |
| Order stuck in sync queue | Failed API call or required field blank | Operations | Re-run, add a required-field check |

## Alerts and cadence
- Daily: list of orders without an invoice after N days and orders without a product ID.
- Weekly: new duplicates and sync failures.
- Monthly: three-way reconciliation and exception-rate trend, shared with finance and sales.

## Success measures
Exception rate, days from deal won to invoice, size of the monthly gap, and time to resolve an exception.
