# The sales funnel, its factors and the Six Sigma method behind it

## The funnel
```
Lead  ->  MQL  ->  SQL  ->  Opportunity  ->  Customer
```
Lead, MQL and SQL are counted per contact. Opportunity and Customer are counted per deal, so a deal with several contacts is not counted twice.

## The factors that move a record forward (the "Xs")
| Stage change | Factors that decide it | How it is measured |
|---|---|---|
| Lead to MQL | **Fit** (segment, role, organisation size), **engagement** (replies, clicks, form fills), **source** (event, referral, outbound, web), product awareness | Share of leads reaching the MQL cut-off |
| MQL to SQL | **Intent** (pricing visit, quote or sample request, meeting booked), **touches** (number and speed), a fit check, a clear owner | Share of MQLs accepted by sales |
| SQL to opportunity | **Speed to first contact**, quality of the conversation, data completeness (company and contact linked), owner clarity | Share of SQLs with a deal created; days to first touch |
| Opportunity to customer | **Quote speed**, price and terms, sample and technical support, **time in stage**, product fit, competitor position | Win rate; days in each stage against benchmark |
| Across all stages | **Touches per record**, record data quality, owner assigned, hand-off between inside sales and reps | Average touches; share of records idle; stalled deals |

## Why touches matter (the proof)
In the synthetic run, an idle record averages about 2 touches, a record that became a deal about 16, and a closed-won record about 31. 85% of records have three or fewer touches. The signal was there, but effort was not routed toward records showing it.

## Funnel results in the synthetic run
| Step | Records | Share of input |
|---|---|---|
| Records in the CRM | 1,600 | 100% |
| Touched at least once | 1,193 | 75% |
| Worked with follow-up | 635 | 40% |
| Qualified | 180 | 11% |
| Deal created | 99 | 6% |
| Won | 25 | 2% |

## The Six Sigma method (DMAIC) applied to the funnel
| Phase | What was done |
|---|---|
| **Define** | Problem: very few records become customers. Critical-to-quality measures: conversion at each stage, days in stage, touches per record, cost per win. Scope: all four pipelines, lead to customer |
| **Measure** | Counted records at every stage, conversion between stages, touches per record, days in stage and win rate by source, to set the baseline |
| **Analyse** | Looked for the vital few causes: records idle on the floor, low touches, weak fit rules, unclear ownership, low awareness of some products, and stale deals. Win rate by source and touches by outcome showed where effort pays back |
| **Improve** | Redesigned scoring (fit, intent, engagement), routed records by lane, capped sends and added a stop rule, set a touch target and a stalled-deal alert, and clarified ownership |
| **Control** | Weekly pipeline review, the stalled list, KPI definitions with one source per KPI, a monthly data-quality check and owner alerts for idle records |

The same method is used in the Green Belt project in [SixSigma_Green_Belt](https://github.com/rbanola1/SixSigma_Green_Belt).

## Assumptions and data
The funnel was set up from scratch. At the start there was no usable history of conversion rates, so the first stage probabilities, cut-offs and benchmarks were stated assumptions. Each is labelled, and each is replaced by actual data as it builds up. The synthetic figures here follow that same pattern: assumptions first, then measured values.
