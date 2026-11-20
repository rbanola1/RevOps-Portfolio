# Lifecycle and scoring

## Lifecycle stages
| Stage | Level | Rule |
|---|---|---|
| Lead | Contact | In the CRM |
| MQL | Contact | Engagement-only score of 15 or more (starting point; replaced by the combined score in GTM-Strategy 02) |
| SQL | Contact | Engagement-only score of 30 or more, or rep-qualified (starting point; replaced by the combined score) |
| Opportunity | Deal | Deal created |
| Customer | Deal | Closed won |

## Engagement score (0-100)
| Signal | Base points |
|---|---|
| Marketing email open | 5 |
| Marketing click (ever) | +10 while recent |
| Click on a sales email | 12 |
| Reply to a sales email | 30 |

**Decay:** each signal is multiplied by 0.8 for every 90 days since it happened, so a reply from nine months ago counts about half.

## Known limits and next step
- Engagement alone cannot tell buyers from bystanders. Add a separate **fit score** (segment, role, research area, past buyer) and combine the two. See the GTM-Strategy repo for the fit x intent model.
- Opens are inflated by security scanners, so weight clicks and replies above opens.
- Reset lifecycle stages that were bulk-set during imports before trusting stage-based reports.
