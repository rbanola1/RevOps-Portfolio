# 03 | Lead Generation Plan: Reverse-Funnel Revenue Model

**Fictional company:** RB Tech · **All data is synthetic**

![Lead generation plan](charts/lead_gen_plan.png)

## At a glance
```mermaid
flowchart LR
    A["Revenue target but no lead plan"] --> B["Reverse funnel by channel with a capacity check"] --> C["Target split into wins, SQLs and leads per channel"]
    classDef p fill:#EEF0F3,stroke:#9AA5B1,color:#222
    classDef b fill:#DCE8F7,stroke:#2B5C9E,color:#222
    classDef r fill:#CFE9E3,stroke:#2A9D8F,color:#222
    class A p
    class B b
    class C r
```

## The story in STAR
- **Starting point:** No historical conversion data by channel existed. The plan rests on two stated assumptions, that the planned product launches happen (the portfolio multiplier P) and a fixed brand trust factor (T), checked against the CRM's own close rates ([assumptions and validation](docs/assumptions_and_validation.md)).
- **Situation:** The business had a revenue number for the year but no plan for the leads needed to reach it.
- **Task:** Work backwards from a $1.7M catalogue revenue target (the $3.8M plan also includes about $2.1M of custom projects, planned deal by deal) to the leads each channel must produce, and test whether the team could deliver.
- **Action:** Divided the target by order size, split it by channel, worked back through deals, SQLs and MQLs, added a capacity ceiling, repeat purchasers, monthly plan-versus-actual and stress tests.
- **Result:** 850 wins and about 700 new customers needed; 9 of 11 channels within capacity; a 15% lower close rate would leave a gap of about $255K.

## The problem
The business wanted a revenue number for the year and needed to know what lead generation it would take to hit it. Typical plans start from marketing activity ("we will run N events and send M emails") and hope it adds up. I planned the other way round: start from the revenue target and work backwards to the leads, meetings and activities each channel must produce, then test whether the plan is believable.

## Method
1. **Target and order size.** Revenue target divided by average order value gives the number of wins needed ($1.7M of catalogue revenue at a $2,000 order is 850 wins).
2. **Allocate by channel.** Each channel gets a share of revenue based on how it has performed: conferences, tabletop and regional shows, field prospecting, webinars, launch campaigns, inbound, distributors, inside sales, paid media, beta programs, and small-product OEM.
3. **Work backwards per channel.** Wins, divided by the channel's win rate, gives deals; divided by its SQL-to-deal rate gives SQLs; divided by its MQL-to-SQL rate gives MQLs ([docs/method.md](docs/method.md)).
4. **Validate.** A team can only close so many qualified deals. A capacity ceiling (portfolio multiplier x trust factor, here 0.8 x 0.4 = 32%) caps the close rate any channel is allowed to assume. Any channel above it is flagged.
5. **Add repeat purchasers.** Assume a few constant repeat accounts (distributors) and that a share of other customers reorder, so the plan needs fewer unique new customers than wins.
6. **Track plan against actual** each month and re-forecast.
7. **Stress-test.** Re-run with lower close rates to see the revenue gap.

## Results on the synthetic run
| Item | Value |
|---|---|
| Catalogue revenue target (part of a $3.8M plan) | $1,700,000 |
| Wins needed | 850 at the standard order size (about 875 including low-value OEM orders) |
| Unique new customers needed | about 700 (after repeat purchasers) |
| Channels within capacity | 9 of 11 (paid media and small-product OEM flagged: their close rates rest on a different, narrow buyer set) |
| Month 9 actual vs plan to date | $712K vs $1.27M, a run-rate of about $950K for the year |
| If close rates run 15% below plan | revenue gap of about $255K |
| If close rates run 30% below plan | revenue gap of about $510K |

Lowest cost per win: small-product OEM, distributors, inbound and field prospecting. Highest: paid media, large conferences and inside sales, each with a clear role (awareness, relationships, warm-up) beyond direct cost.

## What the plan teaches
- **MQL volume is a poor planning currency for low-intent channels.** Launch campaigns and inside-sales warm-up needed tens of thousands of MQLs to yield a handful of wins, a sign that engagement-based MQL counts say little about buying. Plan on SQLs and deals, and define MQL from fit and intent ([see the lead scoring redesign](https://github.com/rbanola1/GTM-Strategy)).
- **Capacity checks keep targets honest.** If a channel needs a close rate above what the team can do, the plan is fiction until the inputs change.
- **Plan versus actual shows which channels drive the gap.** In the synthetic run, the largest gaps are in conferences, tabletop shows and field prospecting, the biggest bets.
- **Channels with a slow ramp (distributors) need a different timing assumption**, not the same monthly phasing as events.

## Documents and diagrams
- [docs/method.md](docs/method.md): formulas, assumptions, capacity logic
- [docs/assumptions_and_validation.md](docs/assumptions_and_validation.md): the P, T and CS% variables, the two validation checks and what is assumed against measured
- [docs/review_cadence.md](docs/review_cadence.md): monthly plan-versus-actual routine
- [diagrams/reverse_funnel.md](diagrams/reverse_funnel.md)

## Reproduce
```bash
pip install pandas numpy matplotlib
python scripts/lead_gen_plan.py    # writes data/*.csv and charts/lead_gen_plan.png
```

## Skills shown
Revenue planning · reverse-funnel modelling · channel ROI and cost per win · capacity-based validation · plan-versus-actual reporting · sensitivity analysis · Python
