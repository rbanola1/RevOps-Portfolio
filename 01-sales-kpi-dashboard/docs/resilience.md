# Dashboard resilience

## Why
A single reporting tool is a single point of failure. A failed refresh or a tool outage should not leave leadership without numbers on the day they need them.

## Layers
| Layer | Tool | Used when | Owner |
|---|---|---|---|
| Main report: 15 visuals, 5 pages | BI tool | Normal weekly and monthly reporting | Commercial operations |
| Executive failover dashboard | CRM native dashboard | BI tool down, or board and leadership need a quick view | Commercial operations |
| Internal KPI failover dashboard | CRM native dashboard | BI tool down; weekly team review | Commercial operations |
| Weekly PDF export | BI tool export | Archive and offline reading | Commercial operations |

## Failover content
| Dashboard | Contents |
|---|---|
| Executive | Revenue (as last loaded from the accounting feed), pipeline value and coverage, deals won, open tickets and SLA |
| Internal KPI | Opportunities by stage, new contacts, orders, tasks overdue, tickets by status |

## Performance clean-up checklist
1. Remove columns and tables the report does not use.
2. Filter and aggregate at the source, not in the report.
3. Use one date table and one customer table shared by all pages.
4. Replace calculated columns with measures where possible.
5. Schedule refreshes outside working hours; alert the owner on failure.
6. Test refresh time after every change and record it.

## Rules
- Failover dashboards are checked monthly against the main report; differences above 2% are investigated.
- Every number on a failover dashboard uses the same definition as the main report.
- The owner and a named deputy know how to switch to the failover view.

The data flow into the BI model, its owners and failure points are in the [CRM to BI runbook](../../07-commercial-systems-architecture/docs/crm_to_bi_runbook.md); this page covers only the failover layers and the clean-up checklist.
