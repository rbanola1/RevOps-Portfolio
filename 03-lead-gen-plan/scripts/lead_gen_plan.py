"""Reverse-funnel lead generation plan for RB Tech (fictional), with plan-vs-actual tracking.

Method (all inputs invented):
  1. Revenue target / average order value = wins needed.
  2. Allocate wins to channels by expected contribution.
  3. Work backwards per channel: wins -> deals -> SQL -> MQL using channel conversion rates.
  4. Validate: each channel's required close rate must be below the team's capacity (P x T).
  5. Add repeat purchasers, cost per channel, plan-vs-actual and a sensitivity test.
Run: python scripts/lead_gen_plan.py      Needs: pandas, numpy, matplotlib
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, CHARTS = ROOT / "data", ROOT / "charts"
DATA.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)
rng = np.random.default_rng(8)

TARGET, AOV = 1_700_000, 2_000
WINS_NEEDED = int(np.ceil(TARGET / AOV))

# channel: (share of revenue, deal->win rate, SQL->deal rate, MQL->SQL rate, annual cost $, avg order $)
CH = {
    "Large conferences":      (0.22, 0.29, 0.30, 0.30, 364_000, AOV),
    "Tabletop / regional":    (0.20, 0.29, 0.60, 0.50, 126_000, AOV),
    "Field prospecting":      (0.18, 0.29, 0.32, 0.48, 84_000, AOV),
    "Webinars":               (0.06, 0.14, 0.35, 0.50, 42_000, AOV),
    "Launch campaigns":       (0.08, 0.28, 0.18, 0.005, 63_000, AOV),
    "Inbound organic":        (0.07, 0.27, 0.075, np.nan, 28_000, AOV),
    "Distributor channel":    (0.07, 0.27, 1.0, np.nan, 21_000, AOV),
    "Inside sales (warm-up)": (0.07, 0.27, 0.06, 0.008, 105_000, AOV),
    "Paid media":             (0.02, 0.60, 1.0, np.nan, 35_000, AOV),
    "Beta programs":          (0.02, 0.20, 0.25, np.nan, 14_000, AOV),
    "Small-product OEM":      (0.01, 0.47, 0.70, np.nan, 7_000, 500),
}
rows = []
for name, (share, dw, sd, ms, cost, aov) in CH.items():
    revenue = TARGET * share
    wins = revenue / aov
    deals = wins / dw
    sql = deals / sd
    mql = sql / ms if ms == ms else np.nan
    rows.append(dict(channel=name, revenue_target=round(revenue), avg_order=aov, wins=round(wins, 1),
                     deals=round(deals, 1), sql=round(sql, 1), mql=round(mql) if mql == mql else None,
                     deal_to_win=dw, sql_to_deal=sd, mql_to_sql=ms if ms == ms else None, cost=cost,
                     cost_per_win=round(cost / wins), roi=round(revenue / cost, 1)))
plan = pd.DataFrame(rows)
plan.to_csv(DATA / "channel_plan.csv", index=False)

# ---------------- validation: required close rate vs capacity (P x T) ----------------
P, T = 0.8, 0.4                         # portfolio multiplier (4 of 5 kits) and trust factor
CAPACITY = P * T                        # ceiling on how often a qualified deal can close
val = plan[["channel", "deal_to_win"]].assign(capacity=CAPACITY,
                                              headroom=lambda d: (CAPACITY - d.deal_to_win).round(2))
val["within_capacity"] = val.deal_to_win <= CAPACITY
val.to_csv(DATA / "validation.csv", index=False)

# ---------------- repeat purchasers ----------------
DIST_REPEAT = 3                         # constant repeat orders from a distributor
REPEAT_SHARE = 0.20                     # share of other customers who reorder
wins_total = plan.wins.sum()
repeat_customers = REPEAT_SHARE * (wins_total - DIST_REPEAT) + DIST_REPEAT
unique_customers = wins_total - repeat_customers
pd.Series({"wins_needed": WINS_NEEDED, "wins_planned": round(wins_total, 1),
           "repeat_customers_min": round(repeat_customers, 1),
           "unique_new_customers_needed": round(unique_customers, 1), "capacity_PxT": CAPACITY,
           "target_revenue": TARGET}).to_csv(DATA / "plan_summary.csv", header=["value"])

# ---------------- plan vs actual at month 9 (synthetic actuals) ----------------
MONTH = 9
seasonal = MONTH / 12
act = plan[["channel", "revenue_target", "wins"]].copy()
perf = rng.normal(0.85, 0.25, len(act)).clip(0.2, 1.4)
perf[act.channel.isin(["Large conferences", "Webinars"])] *= [1.15, 0.7]
perf[act.channel == "Distributor channel"] = 0.25                           # slow ramp, as planned for H2
act["actual_revenue"] = (act.revenue_target * seasonal * perf).round(-2)
act["plan_to_date"] = (act.revenue_target * seasonal).round(-2)
act["variance"] = act.actual_revenue - act.plan_to_date
act["pct_of_plan"] = (act.actual_revenue / act.plan_to_date).round(2)
act.to_csv(DATA / "plan_vs_actual.csv", index=False)
ytd, ytd_plan = act.actual_revenue.sum(), act.plan_to_date.sum()
run_rate = ytd / seasonal

# ---------------- sensitivity: lower close rates ----------------
sens = []
for scale in (1.0, 0.85, 0.7, 0.55):
    wins = float((plan.revenue_target / plan.avg_order / 1).sum())
    expected = float((plan.deals * plan.deal_to_win * scale * plan.avg_order).sum())
    sens.append(dict(close_rate_vs_plan=f"{scale:.0%}", expected_revenue=round(expected),
                     gap_to_target=round(expected - TARGET)))
pd.DataFrame(sens).to_csv(DATA / "sensitivity.csv", index=False)
print(plan[["channel", "revenue_target", "wins", "deals", "sql", "mql", "cost_per_win", "roi"]].to_string(index=False))
print(pd.DataFrame(sens).to_string(index=False))
print(f"wins needed {WINS_NEEDED} planned {wins_total:.1f}; unique customers {unique_customers:.1f}; "
      f"YTD {ytd:,.0f} vs plan {ytd_plan:,.0f}; run-rate {run_rate:,.0f}")

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 5))
fig.suptitle("RB Tech | Lead generation plan (synthetic data)", fontsize=13, weight="bold")
p = plan.sort_values("revenue_target")
ax[0].barh(p.channel, p.revenue_target / 1000, color=BLUE)
ax[0].set(title=f"Revenue target by channel (\${TARGET/1000:,.0f}K, {WINS_NEEDED} wins)", xlabel="$K")
f = plan[plan.sql.notna()]
stages = ["wins", "deals", "sql"]
x = np.arange(len(f))
per_win = (f.sql / f.wins.replace(0, np.nan)).round(1)
ax[1].barh(f.channel, per_win, color=BLUE)
for y_, v_ in enumerate(per_win):
    ax[1].text(v_ + .3, y_, f"{v_:g}", va="center", fontsize=8)
ax[1].set(title="Qualified leads (SQL) needed per win, by channel", xlabel="SQL per win")
colors = np.where(val.within_capacity, TEAL, RED)
v = val.sort_values("deal_to_win")
ax[2].barh(v.channel, v.deal_to_win * 100, color=[TEAL if w else RED for w in v.within_capacity])
ax[2].axvline(CAPACITY * 100, color="k", ls="--", lw=.8)
ax[2].text(CAPACITY * 100 + .5, 0, f"capacity {CAPACITY:.0%}", fontsize=8)
ax[2].set(title="Close rate each channel needs vs what the team can deliver", xlabel="% of deals won")
a = act.sort_values("plan_to_date")
yy = np.arange(len(a))
ax[3].barh(yy + .2, a.plan_to_date / 1000, .4, color=GREY, label="Plan to date")
ax[3].barh(yy - .2, a.actual_revenue / 1000, .4, color=TEAL, label="Actual")
ax[3].set_yticks(yy, a.channel)
ax[3].legend(fontsize=8)
ax[3].set(title=f"Month {MONTH}: plan vs actual (\${ytd/1000:,.0f}K vs \${ytd_plan/1000:,.0f}K)", xlabel="$K")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "lead_gen_plan.png", dpi=130)
print("done")
