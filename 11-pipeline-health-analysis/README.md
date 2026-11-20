# 11 | Pipeline Health Analysis: Conversion, Ageing, Coverage and Stalled Deals

**Fictional company:** RB Tech · **All data is synthetic**

![Pipeline health dashboard](charts/pipeline_health_dashboard.png)

## The problem
The pipeline report showed one number: total open value. It said nothing about whether deals were moving, which sources produced wins, or whether next quarter's quota was actually covered. Leadership saw a healthy total while several deals had not been touched for weeks.

## What I built
A weekly pipeline-health view from CRM deal data with six measures:
1. **Stage conversion**: how many deals reach each stage, and the rate from one stage to the next.
2. **Open value versus weighted value** by stage, using stage probabilities agreed with sales.
3. **Coverage of next-quarter quota**, as reported and after removing stalled deals, against a 3x target.
4. **Time in stage versus benchmark** for each stage.
5. **Win rate by lead source**, to show where effort pays back.
6. **A stalled-deal list**: no activity for 21 days, or more than twice the benchmark time in stage, sorted by value for the weekly review.

## What the synthetic data shows (700 deals, one year)
| Finding | Evidence |
|---|---|
| Coverage looks fine but falls short | Open pipeline is 2.4x next-quarter quota against a 3x target; removing stalled deals drops it to 2.1x |
| The funnel leaks evenly | About 70% of deals move up at each stage; overall win rate is 29% of closed deals |
| Source decides the outcome | Existing customers win 71% of the time; distributor referrals 35%; trade shows 30%; inbound web 18%; outbound sequences 6% |
| Trade show and referral deals are larger | Average won deal is about $20K versus about $11K from outbound |
| Stalled deals are a visible list, not a feeling | Each Monday the owner sees the deals past benchmark, with value and days idle |

## The CRM as a factory
The core finding was that the CRM held plenty of good material that nobody used. I treated the CRM like a production line: records are raw material, stages are stations, wins are finished goods. In the synthetic data, of 4,000 records entering the CRM in a year, 74% were touched once, 40% were worked with follow-up, 7% became deals and 2% were won. Trade-show records were the most idle: 71% were never worked. Nothing was wasted in the sense of bad data; it was simply not used.

![CRM factory utilisation](charts/crm_factory_utilization.png)

The fix was operational: every station gets an owner, a time limit and a report, and idle inventory raises an alert. See [diagrams/crm_factory.md](diagrams/crm_factory.md) for the before and after line.

## How the data is used
- **Weekly pipeline review:** start with the stalled list, then coverage, then new deals needed to reach 3x.
- **Lead-source planning:** the win-rate table feeds the reverse-funnel model in [project 03](../03-lead-gen-plan).
- **Forecast:** weighted pipeline by stage feeds the driver-based forecast in [project 08](../08-budget-forecast-pnl).

## Design decisions
1. **Coverage is shown twice**, with and without stalled deals, so the real gap is visible.
2. **Benchmarks come from won deals**: the median time won deals spent in each stage, not an opinion.
3. **One definition of stalled**, written down ([docs/stage_definitions.md](docs/stage_definitions.md)), so the rep, the manager and the report agree.
4. **Weighted value is a planning number**, never a promise; the forecast uses it with a range.

## Documents and diagrams
- [docs/stage_definitions.md](docs/stage_definitions.md) · [docs/weekly_review_routine.md](docs/weekly_review_routine.md)
- [diagrams/pipeline_review_flow.md](diagrams/pipeline_review_flow.md) · [diagrams/crm_factory.md](diagrams/crm_factory.md)

## Reproduce
```bash
pip install pandas numpy matplotlib
python scripts/pipeline_health.py    # writes data/*.csv and charts/pipeline_health_dashboard.png
```

## Skills shown
Pipeline analysis · stage-conversion funnels · coverage ratios · deal-ageing benchmarks · win-rate analysis by source · forecasting inputs · weekly review design · Python
