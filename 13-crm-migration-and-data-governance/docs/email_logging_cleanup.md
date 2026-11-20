# Email logging cleanup and the ticket email loop

## Problem
Email logging between the mailbox and the CRM created noise and risk:
- Automated and internal emails were logged to customer records, burying real conversations.
- One customer's reply could create a new ticket, and the ticket's auto-reply could trigger another reply, producing a loop that sent many emails.
- Duplicate logging inflated activity counts, which distorted engagement scores and reports.

## Cleanup approach
| Step | Action |
|---|---|
| 1. Measure | Count logged emails per day by sender type: customer, internal, automated, unknown; find the top senders by volume |
| 2. Exclude | Add internal domains, system notifications and no-reply senders to the exclusion list so they are never logged |
| 3. Fix the loop | Stop auto-replies from creating or re-opening tickets; one auto-reply per sender per 24 hours; ignore messages with auto-reply headers |
| 4. Clean | Remove or archive logged emails from excluded senders, with a backup export first and a change log |
| 5. Re-check scores | Recalculate engagement scores so duplicated or automated activity no longer counts |
| 6. Monitor | A monthly check on the 28th: top senders, volume spikes, loop alerts, duplicate rate |

## Guardrails
- A rate limit alert if one contact generates more than a set number of emails or tickets in an hour.
- Ticket creation ignores automated senders and out-of-office replies.
- The customer-facing auto-reply states that replying will update the same ticket, not open a new one.
- Every bulk deletion needs a backup export, a second approver and a written log.

## Measures
| Measure | Target |
|---|---|
| Share of logged emails from automated or internal senders | Under 2% |
| Tickets opened by automated senders | 0 |
| Loop alerts per month | 0, with any alert reviewed within a day |
| Duplicate activity records | Under 1% |

## Rules
- A named owner and deputy run the monthly check.
- Findings are recorded as a short note: what changed, why and the effect on the measures.
