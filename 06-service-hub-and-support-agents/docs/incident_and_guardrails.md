# Incident: auto-reply loop, and the guardrails

## What happened (illustrative)
An institutional helpdesk robot answered our automatic "ticket received" email with its own automatic "ticket created" email. Each of those emails created a new ticket in our system, which sent a new acknowledgement, which the robot answered again. Overnight the loop created roughly a thousand junk tickets and buried genuine requests.

## Cause
1. An automatic acknowledgement was sent to every new ticket, including auto-generated ones.
2. No check for automatic-reply subjects ("ticket created", "has been received", "out of office", "automatic reply", "undeliverable").
3. No limit on how many acknowledgements one sender could receive.

## Response
1. Stop the damage: identify the pattern, pause the acknowledgement workflow.
2. Remove junk tickets in bulk through delete, not close, because closing fires the satisfaction survey. Deleted tickets remain restorable for a period; genuine tickets were kept.
3. Reopen and correct the original genuine ticket.
4. Do not block the sender, since the institution was an approved supplier relationship.

## Guardrails now in place
| Guard | How it works |
|---|---|
| Subject filter | The acknowledgement workflow skips tickets whose subject or name contains automatic-reply phrases |
| One reply per sender per hour | A contact flag records that an acknowledgement was sent; a second workflow resets it after an hour |
| Survey rule | Never bulk-close tickets; closing triggers the satisfaction survey |
| Weekly check | A scheduled review of ticketing activity looks for loops and suspicious volume |
| Old workflow kept as backup | The previous version stays unpublished for rollback |

## Testing
Test an empty flag passes, a "yes" flag blocks, auto-reply subjects are skipped, and genuine tickets still get one acknowledgement.

## Lessons
- Any workflow that sends email needs loop protection from day one.
- Delete is safer than close for junk, and tickets should be restorable.
- Alert on abnormal ticket volume rather than relying on someone noticing.
- Document the incident, the cause and the guardrail map so it can be repeated or audited.
