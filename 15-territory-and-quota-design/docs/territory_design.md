# Territory design

## Principles
| Principle | How it is applied |
|---|---|
| Balance potential, not account count | Each target account carries a potential value (segment multiplier times local density); reps get equal totals |
| Keep metro areas whole | Research hubs such as Boston or the Bay Area stay with one rep unless one hub is too large for one rep |
| Contiguous and travelable | Territories run west to east so a rep can cover them in one trip |
| Protect current customers | Customers move with the territory; any change comes with a handover plan and a split of in-flight deals |
| Review once a year | Re-run the model each January; change mid-year only for a new hire, product or partner |

## Domestic territories (synthetic result)
Four territories with potential between $3.317M and $3.322M each; account counts range from 626 to 977 because dense hubs hold higher-value accounts.

## International routing rules
| Country group | Default route | Exception |
|---|---|---|
| Canada | Nearest rep by province group | None |
| United Kingdom and Ireland | Distributor | Large account: direct rep, distributor informed |
| Germany, France, Benelux | Distributor | Same |
| Nordics and Switzerland | Distributor | Same |
| Japan and Korea | Distributor | Same |
| China, Singapore, Australia | Distributor | Same |
| Rest of world | Inside-sales queue, quotes only | Move to a distributor when one is signed |

### How an AI assistant was used
1. Export international leads with company, country, segment and source.
2. Ask the assistant to map each country to a group, flag segments and sizes, and rank by estimated potential, with the reason for each call.
3. A person reviews a sample, corrects the rules, and runs the batch again.
4. The final mapping is stored as a lookup table in the CRM so routing is automatic and does not depend on the assistant.
5. Large-account exceptions and any lead the assistant was unsure about go to a human review list.

## Rules
- Each account has one owner: a rep, a distributor or the inside-sales queue.
- A distributor lead is shared with the distributor within two business days.
- A direct-rep exception always informs the distributor, and sales credit follows the partner agreement.
