# "Research first" rule and ownership

## The rule
Before anyone contacts a lead, they must search the CRM for the **company, the deal and the contact**.

1. **Company found:** check the account owner. If a different rep owns it, get permission before contacting anyone at that company. The same applies if the contact or deal was managed by another rep before.
2. **New contact in a different department of an existing account:** announce it in the team chat, for example "I am reaching out to the R&D group at this account about a new product. The account owner is X, so I wanted to let everyone know."
3. **Golden rule:** never contact a lead or account already owned by another rep without checking with the team first.

## Logging
Every email, call, note, task and meeting is logged in the CRM by the rep who did it. In a conflict, the log decides.

## Ownership data model (mandatory)
| Field | Rule |
|---|---|
| Contact owner | Always set |
| Deal owner | Always set |
| Company owner | Always set |
| Deal associations | Link each deal to both the company and the primary or relevant contact |
| Parent and child accounts | Create hierarchy for companies with divisions or subsidiaries, so ownership is explicit |

## Conflict handling
| Conflict | Resolution |
|---|---|
| Two reps contact the same person | Account owner leads; the other rep stops and hands over notes |
| Two reps quote the same project | One quote only; owner of the deal sends it |
| New division of an existing customer | Parent account owner is told first and decides |
| Marketing-generated vs self-sourced lead | Existing owner wins; otherwise lane criteria decide |
| Trade-show lead with several attendees | Default to the outside sales manager, then reassign |
| Duplicate records | Merge on a match key, keep the oldest record's history |

## Workflows
- Alert the account owner when a deal is created in their company by someone else.
- Flag deals missing a company or contact association.
- Report unowned contacts, companies and deals weekly.
