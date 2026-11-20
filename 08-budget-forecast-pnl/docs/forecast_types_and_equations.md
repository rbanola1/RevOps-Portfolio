# Forecast types and equations

Five forecasts answer five different questions. Each has one owner, one equation and one accuracy measure.

| # | Forecast | Question it answers | Equation | Inputs | Owner | Reviewed |
|---|---|---|---|---|---|---|
| 1 | Inbound lead forecast | How many leads will arrive each month? | Leads = website visitors x visit-to-lead rate + webinar attendees x lead rate + event badge scans x qualify rate, each times a seasonality index | Web analytics, event and webinar calendar, past rates | Marketing | Monthly |
| 2 | Deal and revenue plan (reverse funnel) | Which channels must deliver the target, and how many leads does each need? | Deals needed = target revenue / average deal size. Channel revenue = target x channel share. Qualified leads needed = channel deals / channel close rate | Target, average deal, channel shares, close rates, capacity ceiling | Commercial operations | Quarterly |
| 3 | Revenue recognition forecast | When will won orders turn into recognised revenue? | Recognised(month) = sum over k of Orders won(month - k) x share recognised in month k, for example 40% / 35% / 15% / 10%; milestone projects follow their schedule | Bookings, invoicing lag, shipment dates, project milestones | Finance with commercial operations | Monthly |
| 4 | Product forecast | Which products will drive revenue, including launches? | Product revenue = base units x price x seasonality x growth; a launch follows a ramp curve (for example six months to steady state) | Product history, launch plan, price list | Product and commercial operations | Monthly |
| 5 | Demand forecast (units and stock cover) | How many units will customers order, and what should operations order? | Demand = recent average x seasonality x growth. Months of cover = stock on hand / forecast monthly demand. Reorder when cover is below lead time plus safety buffer | Orders, forecasts 2 and 4, stock, supplier lead times | Operations | Monthly |

## How they connect
Forecast 2 sets the plan. Forecast 1 shows whether lead flow supports it. Forecast 4 splits the plan by product. Forecast 5 turns product forecasts into units and orders for operations. Forecast 3 turns won orders into recognised revenue for the P&L.

## Accuracy tracking
| Forecast | Typical error (synthetic) | Measured as |
|---|---|---|
| Inbound leads | about 12% | Forecast vs actual leads, 3-month average |
| Revenue plan by channel | about 22% | Planned vs actual revenue by channel |
| Revenue recognition | about 6% | Recognised vs forecast |
| Product revenue | about 15% | Forecast vs actual by product |
| Unit demand | about 18% | Forecast vs actual units shipped |

## Rules
- Every forecast states its equation and inputs on the page.
- Seasonality indexes are rebuilt each year from actual months.
- Plans are never changed to match actuals; a re-forecast is a new version with the date.
- Accuracy is reviewed monthly, and any forecast with error above its tolerance gets a change to its inputs.
