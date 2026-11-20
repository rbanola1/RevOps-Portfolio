# Stage definitions

| Stage | Entry rule | Exit evidence | Probability | Benchmark days |
|---|---|---|---|---|
| Qualified | Contact fits the target profile and has a stated need or a score of 50 or more | Need, budget range and timeline confirmed on a call | 10% | 14 |
| Needs confirmed | Application, product and quantity are known | A quote request is logged | 25% | 21 |
| Quote sent | Quote delivered to the buyer | Buyer replies with questions, a PO route or a decline | 50% | 18 |
| Negotiation | Buyer is discussing price, terms or paperwork | PO or signed order received | 75% | 14 |
| Won | PO received | Order entered in the order system | 100% | n/a |

## Rules
- Every open deal has an amount, a close date, a next step and a next-step date; a deal without them is flagged, not counted in coverage.
- A deal is **stalled** when there is no logged activity for 21 days, or time in stage is more than twice the benchmark.
- A deal never moves backward without a note.
- Lost deals carry one of six loss reasons: price, timing, competitor, no budget, no response, product fit.
- Benchmarks are reset each quarter from the median time of deals won in the previous four quarters.
