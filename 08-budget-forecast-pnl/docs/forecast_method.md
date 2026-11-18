# Forecast method

## Closed months
Use actuals from accounting.

## Open months (driver-based)
For each route: forecast = 50% x recent run-rate (average of the last three months) + 50% x weighted pipeline spread over the next three months, then adjusted for seasonality.

### Weighted pipeline
Deal amount x stage probability: pipeline 15%, best case 30%, commit 60%, closed won 100%. Require each open deal to have a company, close date and product, so the forecast is not distorted by incomplete records.

## Costs
- Cost of goods follows forecast revenue by route margin.
- Operating expenses stay at budget unless a known change is approved.

## Cash
Collections lag revenue by route: direct about 6 days, distributors about 45, marketplaces about 38. Cash in equals revenue shifted by the route's lag; cash out equals cost of goods plus operating expenses. Closing cash starts from the actual balance.

## Scenarios
| Scenario | Change |
|---|---|
| Pipeline converts 15% lower | Forecast revenue x 0.85 |
| Pipeline converts 10% higher | Forecast revenue x 1.10 |
| Shipping and COGS up 8% | Cost of goods x 1.08 |
| Hiring | Operating expenses x 1.10 |

## Accuracy tracking
Record the forecast made each month and compare to the outcome: mean absolute percentage error by route. Improve the pipeline-weighting and seasonality where error is highest.
