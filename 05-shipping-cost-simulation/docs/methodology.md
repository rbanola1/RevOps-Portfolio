# Methodology

## Question
What flat shipping charge covers delivery cost on temperature-controlled orders while staying competitive?

## Inputs (invented for this portfolio)
| Input | Value |
|---|---|
| Package | 25 lb, 13 x 14 x 15 in, holds up to 3 kits |
| Box | $12 |
| Dry ice | $38 |
| Packing | 1 hour at $30 per hour |
| Fixed cost per shipment | $80 |
| Zones | 2 to 8, equal probability in the baseline |
| Service mix | 90% standard overnight, 10% priority overnight |
| Priority premium | 18% |
| Courier rate | Rises with zone, from $58 (zone 2) to $188 (zone 8) before premium |

## Four-method triangulation
1. **Expert estimate:** a qualitative anchor from the person who runs shipping.
2. **Historical average:** past actual costs. Strong evidence but limited by sample size and by whatever zone mix occurred.
3. **Monte Carlo:** 1,000 random draws of zone and service level to capture variability.
4. **Statistical model:** fit a normal distribution to the simulated costs and read mean, spread, minimum and maximum.

If independent methods agree, the decision is robust. If they disagree, find out why before deciding.

## Decision analysis
- Charge-versus-margin curve across flat charges from $100 to $360.
- Share of shipments sold below cost at each charge, since an average can hide losses on far zones.
- A zone-tiered alternative compared to a flat charge.

## Sensitivity
Test what moves the answer: destination mix, service mix, dry ice cost, packing time and courier rate changes. This shows which assumptions deserve monitoring.

## Limits
- Domestic only; international is quoted per order.
- Equal zone probability is a baseline. Replace it with the real customer destination mix as soon as there is enough data.
- Ignores returns, failed deliveries and negotiated courier discounts.
- Competitiveness is a judgement call: compare the proposed charge to what peers charge and to the order value.

## Next steps
Run quarterly, re-estimate zone mix from actual orders, add a volume-discount scenario, and track whether conversion falls after the new charge.
