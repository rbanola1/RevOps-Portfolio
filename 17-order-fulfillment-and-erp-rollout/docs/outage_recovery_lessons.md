# Outage recovery and lessons

## What happened
After a system outage, the ERP came back working but without some of its configuration (for example order numbering, default values and a few workflow settings). Orders could be created, but some fields were wrong until the settings were rebuilt.

## Recovery steps used
1. Stop new order entry; use the manual order sheet.
2. Compare the system with the settings list and with a recent test order.
3. Restore each missing setting and test with a sample order.
4. Re-enter any orders taken during the outage from the manual sheet.
5. Tell users the system is back and what changed.
6. Write a short incident note: cause, impact, fix, prevention.

## Lessons
| Lesson | Action |
|---|---|
| Vendor instability is a project risk | Add schedule buffer; ask the vendor for outage and restore commitments in writing |
| Settings are data | Export and store a copy of the configuration after every change |
| Document first | A written process and settings list make recovery a checklist, not a rebuild from memory |
| Keep a manual fallback | A simple order sheet keeps shipping going during an outage |
| Test restores | Practise recovery on a test copy once a quarter |
| Do not depend on one person | A trained backup and a recorded walkthrough |

## Settings export list (illustrative)
Order and invoice numbering · default warehouse and shipping methods · tax settings · customer and item defaults · user roles · email templates · integration credentials (stored in the password manager, not in the export).
