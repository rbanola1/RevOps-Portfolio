# Data governance rules

## Ownership
| Object | Business owner | System owner |
|---|---|---|
| Companies and contacts | Commercial operations | CRM administrator |
| Deals and pipeline | Sales manager | CRM administrator |
| Products and price lists | Finance and product management | Commercial operations |
| Marketing properties and lists | Marketing | CRM administrator |

## Rules
- Every record has an owner; unowned records are assigned at creation by the routing rules.
- One match key per object: company domain, contact email, deal ID. Duplicates are merged, not deleted.
- New properties and picklist values need a request, a reason and an owner; the administrator reviews monthly and retires unused properties each quarter.
- Required fields are enforced at the stage where they matter (for example amount and close date from quote stage).
- Imports go through a staging sheet and a checklist: duplicates checked, picklist values valid, owner set, source recorded.
- Nobody deletes records in bulk without a backup and a second approver.

## Monthly quality check
| Check | Target |
|---|---|
| Completeness of the twelve key fields | 90% or more |
| Duplicate rate | Under 2% |
| Records without an owner | 0 |
| Valid emails | 95% or more |
| Records touched in the last 12 months | 70% or more, with the rest reviewed for reactivation or archiving |

System-level data ownership between tools (which system owns which field) is in [project 07](../../07-commercial-systems-architecture/docs/data_ownership.md); this page covers record ownership, quality checks and change control.
