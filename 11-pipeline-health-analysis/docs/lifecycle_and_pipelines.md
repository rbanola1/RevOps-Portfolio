# Lifecycle stages, pipelines and funnel history

## Lifecycle stages
| Stage | How a contact enters | Notes |
|---|---|---|
| Lead | A new contact is created (automatic) | Every contact starts here |
| MQL | Combined fit, intent and engagement score reaches the MQL cut-off | Fit, intent and engagement together; fit rules can block it (competitors, very small companies, students) |
| SQL | Score reaches the SQL cut-off, or a fit-checked hand-raise | Goes to a rep |
| Opportunity | A deal is created for the contact (automatic) | Counted per deal |
| Customer | A deal is closed-won in any pipeline (automatic) | Counted per deal |

**Qualified SQL** = an SQL that a rep has contacted and verified (lead status set to connected). It measures real sales acceptance, not just a score.

### Why the cut-offs changed
The first rules used an engagement-only score: MQL at 15 points and SQL at 30. Once fit and intent were added to the score, those numbers no longer mean the same thing. The new score combines company fit, contact fit, engagement and intent, and its cut-offs are chosen from a back-test of precision, recall and sales capacity (in the synthetic back-test: MQL at 45, SQL at 65, or a fit-checked hand-raise from a contact scoring 50 or more). See GTM-Strategy 02 for the method. Free samples are tracked as validation, with their own pipeline, so they do not inflate revenue funnels.

## Pipelines
| Pipeline | Used for | Closed-won stage |
|---|---|---|
| Sales | Quoted orders and direct deals | Closed won |
| Samples (non-revenue) | Free samples sent for evaluation and validation data | Sample delivered and feedback logged |
| E-commerce | Web-store orders | Order paid |
| Custom project | Services and contract projects with milestones | Contract signed |

All four feed one funnel; each deal carries a deal source and a free-sample flag.

## Deal sources (twelve channels, aligned to the lead generation plan)
Large conferences · tabletop and regional shows · field prospecting · launch campaigns · distributor and channel sales · inside sales · OEM products · webinars · inbound organic · paid media and third party · beta testing · referral and other.
Existing open deals are tagged with a source retroactively so channel results are comparable.

## Funnel history table
| Stage | Counted from | Level |
|---|---|---|
| Lead | Contact created date | Contact |
| MQL | Date the contact entered MQL | Contact |
| SQL | Date the contact entered SQL | Contact |
| Opportunity | Deal created date | Deal |
| Customer | Deal close date, closed-won in any pipeline | Deal |

Opportunity and Customer are counted per deal so a deal with several contacts is not counted several times. One combined table of entry dates feeds the funnel views.

## Funnel views and measures
| View | What it shows |
|---|---|
| Live funnel (all time and this year) | How many contacts and deals are at each stage today |
| Entry-based funnel by quarter | How many entered each stage in each quarter, from the history table |
| Conversion cards | MQL to SQL, SQL to opportunity, opportunity to customer, lead to customer |
| Inside sales tracker | Contacts in sequences by stage, active enrolments, deals and revenue from inside sales, and rep activity (qualified SQLs, meetings, emails) |

## Dashboard pages
Weekly revenue KPIs · year-to-date performance · deals performance · projections · leads and weekly activity · service tickets · expired deals · expired tasks · open deals · sales funnel · inside sales tracker.

## Rules
- Distributor and channel partner is not a lifecycle stage; it conflicted with the automatic customer rule.
- Every deal has an amount, close date, source and owner before it can leave the first stage.
- Funnel definitions are printed on the funnel page so readers see how each number is counted.
