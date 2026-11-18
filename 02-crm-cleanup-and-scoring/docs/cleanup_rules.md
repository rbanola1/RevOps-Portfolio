# Cleanup rules

## Demote (marketing to non-marketing)
A contact is demoted only if **all** of these are true:
1. Currently a marketing contact
2. No email open in the last 12 months (or never opened)
3. Never clicked a marketing email
4. No reply to a sales email in the last 90 days
5. Engagement score below 15
6. Not protected (see below)

## Protected: never demote
- Opportunity or Customer lifecycle stage
- Target personas (scientists, directors, procurement and similar decision roles)
- Added on purpose by a person (form fill or sales-added)
- Created in the last 180 days

## Promote (non-marketing to marketing)
A non-marketing contact is promoted if **any** is true: replied to or clicked a sales email in the last 90 days, or engagement score is 30 or more.
- **EU, UK and Swiss contacts are held** for a consent check before promotion.

## Entry rules (stop the tier refilling)
A contact may become a marketing contact only if:
- They opted in through a form, or
- A rep qualified them, or
- They engaged with sales email and passed the consent check.

Bulk list imports enter as **non-marketing** by default. Marketing contacts are reviewed quarterly against the demote rules.

## Safety steps
1. Run the rules on an export; write the change log; no changes yet.
2. Review the log with the team, including marketing.
3. Apply in batches, starting with the clearest group.
4. Keep the log so any move can be reversed.
5. Report tier usage before and after.
