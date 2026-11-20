# KPI and funnel definitions

## Funnel stages
| Stage | Level | Rule |
|---|---|---|
| Lead | Contact | Contact exists in the CRM |
| MQL | Contact | Combined fit, intent and engagement score at or above the MQL cut-off (45 in the synthetic back-test), and not excluded by hard rules |
| SQL | Contact | Combined score at or above the SQL cut-off (65), or a hand-raise from a contact scoring 50 or more |
| Opportunity | Deal | A deal is created in any pipeline |
| Customer | Deal | Deal closed won, including free-sample pipeline if reported separately |

**Lead score:** maximum 100, engagement only, decays 20% every 3 months so stale activity stops counting.
**MQL and SQL** are engagement-based and rep-qualified. Track them from the date scoring went live; do not back-fill earlier quarters.

## Conversion rates
| KPI | Formula |
|---|---|
| MQL to SQL | SQL / MQL |
| SQL to Opportunity | Opportunities / SQL |
| Opportunity to Customer | Customers / Opportunities |
| Lead to Customer | Customers / Leads |

Use **stage-entry dates** within the period, not each contact's current stage.

## Forecast categories
| Category | Probability |
|---|---|
| Pipeline | 15% |
| Best case | 30% |
| Commit | 60% |
| Closed won | 100% |

Weighted forecast = sum of deal amount x category probability, open deals only.

## Revenue
| KPI | Definition |
|---|---|
| Closed-won revenue | Sum of deal product amounts for closed-won deals; excludes shipping and tax; includes discounts |
| Invoiced revenue | Accounting invoices after shipment; includes product, shipping and tax |
| Average order value | Closed-won revenue / closed-won orders |
| Sales cycle days | Close date minus create date, averaged per pipeline |
| Win rate | Closed won / (closed won + closed lost) |

## Data-quality flags (reported by owner)
| Flag | Rule |
|---|---|
| Expired deal | Close date is before today and the deal is not won, lost or completed |
| Expired task | Due date is before today and status is Not Started |
| Incomplete deal | Missing company, close date, product, or quantity |

## Support KPIs
Tickets by category and inquiry type, average days to close by owner, and spam share, so real demand is visible beneath inbox noise.
