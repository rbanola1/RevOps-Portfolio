# Capture standards

## One record per comment
| Field | Rule |
|---|---|
| VOC ID | Prefix plus the date of the conversation, with a number suffix for the same day (for example `VOC-20260212-3`) |
| Event | Fill only for a real event or webinar; otherwise leave blank |
| Source | Booth conversation, support ticket, survey, email or webinar question |
| Segment | One of the ten customer segments |
| Role | PI or lab head, scientist, director, procurement, founder or executive |
| Theme | One of the nine themes |
| Product | Product area the comment concerns |
| Sentiment | -2 to +2 |
| Competitor | Name or "in-house protocol", if mentioned |
| Contacts count | Number of associated contacts, minimum one |
| Summary | One or two lines in plain language |
| Feedback (input) | The customer's own words, lightly cleaned, in a single field |
| Action | Next step and owner |

## Rules
- Record within 48 hours of the conversation, while details are fresh.
- Do not change the column structure; add values to dropdowns only when a clear new category appears.
- Fields that do not fit go in a short header line inside the feedback text, not in new columns.
- Keep personal data to what is needed: a link to the contact record, not a copy of their details.
- One comment, one record. If a customer raises three points, create three records with a shared reference.
- No product complaint stays only in VOC: if it needs action, a support ticket is created and the VOC record references it.

## Quality checks
Monthly: entries without a theme, sentiment or segment; entries without an action; duplicate records; entries older than 48 hours at capture.
