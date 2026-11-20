"""Synthetic budgeting, forecasting and P&L model for RB Tech (fictional).

Pieces: monthly P&L by channel, budget vs actual variance, driver-based forecast from the pipeline,
CRM-won vs invoiced revenue bridge, cash-flow projection from days sales outstanding, scenarios.
All numbers invented. Run: python scripts/budget_forecast_pnl.py      Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(12)

MONTHS = pd.period_range("2026-01", "2026-12", freq="M")
ACTUAL_THROUGH = 9                                     # actuals for Jan-Sep, forecast for Oct-Dec
ROUTES = ["Direct", "Distributor", "Marketplace"]

# ---------------- 1. budget ----------------
season = np.array([.7, .8, .9, 1.0, 1.0, .9, 1.0, 1.1, 1.1, 1.2, 1.1, 1.2])
season = season / season.mean()
BUDGET_REV = 820_000
share = {"Direct": .78, "Distributor": .12, "Marketplace": .10}
ramp = {"Direct": np.ones(12), "Distributor": np.array([0, 0, 0, 0, 0, .4, .8, 1.2, 1.4, 1.6, 1.8, 1.8]),
        "Marketplace": np.array([.2, .4, .6, .8, 1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.5])}
budget = pd.DataFrame(index=MONTHS)
for r in ROUTES:
    base = BUDGET_REV * share[r] / 12
    budget[f"rev_{r}"] = base * season * (ramp[r] / ramp[r].mean())
budget["revenue"] = budget[[f"rev_{r}" for r in ROUTES]].sum(axis=1)
GM = {"Direct": .62, "Distributor": .42, "Marketplace": .55}
budget["cogs"] = sum(budget[f"rev_{r}"] * (1 - GM[r]) for r in ROUTES)
OPEX = {"Salaries and benefits": 21_000, "Marketing and events": 6_500, "Software and systems": 2_200,
        "Shipping and fulfilment": 3_100, "Travel": 1_300, "Professional services": 1_500, "Other": 900}
for k, v in OPEX.items():
    budget[k] = v * (season if k in ("Marketing and events", "Travel", "Shipping and fulfilment") else 1.0)

# ---------------- 2. actual and forecast ----------------
perf = rng.normal(.92, .07, 12)
actual = budget.copy()
for r in ROUTES:
    actual[f"rev_{r}"] = budget[f"rev_{r}"] * perf * (0.5 if r == "Distributor" else 1.0) * rng.normal(1, .05, 12)
actual["revenue"] = actual[[f"rev_{r}" for r in ROUTES]].sum(axis=1)
actual["cogs"] = sum(actual[f"rev_{r}"] * (1 - GM[r]) * rng.normal(1.02, .02, 12) for r in ROUTES)
for k in OPEX:
    actual[k] = budget[k] * rng.normal(1.0, .06, 12) * (1.18 if k == "Shipping and fulfilment" else 1.0)
# forecast: driver-based from open pipeline for Oct-Dec; actuals cannot exist yet
fc = actual.copy()
pipeline_weighted = {"Direct": 125_000, "Distributor": 19_000, "Marketplace": 28_000}   # weighted pipeline, next 3 months
for r in ROUTES:
    run_rate = actual[f"rev_{r}"].iloc[:ACTUAL_THROUGH].tail(3).mean()
    conv = pipeline_weighted[r] / 3
    fc.loc[fc.index[ACTUAL_THROUGH:], f"rev_{r}"] = (0.5 * run_rate + 0.5 * conv) * season[ACTUAL_THROUGH:] / season[ACTUAL_THROUGH - 3:ACTUAL_THROUGH].mean()
fc["revenue"] = fc[[f"rev_{r}" for r in ROUTES]].sum(axis=1)
fc.loc[fc.index[ACTUAL_THROUGH:], "cogs"] = sum(fc.loc[fc.index[ACTUAL_THROUGH:], f"rev_{r}"] * (1 - GM[r]) for r in ROUTES)
for k in OPEX:
    fc.loc[fc.index[ACTUAL_THROUGH:], k] = budget[k].iloc[ACTUAL_THROUGH:]

def pnl(df):
    out = pd.DataFrame(index=df.index)
    out["revenue"] = df.revenue
    out["cogs"] = df.cogs
    out["gross_profit"] = out.revenue - out.cogs
    out["opex"] = df[list(OPEX)].sum(axis=1)
    out["operating_profit"] = out.gross_profit - out.opex
    out["gross_margin"] = out.gross_profit / out.revenue
    return out
pb, pa, pf = pnl(budget), pnl(actual), pnl(fc)
pb.round(0).to_csv(DATA / "budget_pnl.csv")
pf.round(0).to_csv(DATA / "forecast_pnl.csv")
pa.round(0).to_csv(DATA / "actual_pnl.csv")

# variance YTD (actuals only)
ytd = slice(0, ACTUAL_THROUGH)
var = pd.DataFrame({"budget_ytd": pb.iloc[ytd].sum(), "actual_ytd": pa.iloc[ytd].sum()}).drop(index=["gross_margin"])
var["variance"] = var.actual_ytd - var.budget_ytd
var["variance_pct"] = (var.variance / var.budget_ytd).round(3)
var.assign(budget_ytd=var.budget_ytd.round(0), actual_ytd=var.actual_ytd.round(0), variance=var.variance.round(0), variance_pct=var.variance_pct.round(3)).to_csv(DATA / "variance_ytd.csv")
opex_var = pd.DataFrame({"budget": budget[list(OPEX)].iloc[ytd].sum(), "actual": actual[list(OPEX)].iloc[ytd].sum()})
opex_var["variance"] = opex_var.actual - opex_var.budget
opex_var.round(0).to_csv(DATA / "opex_variance_ytd.csv")

# ---------------- 3. CRM won vs invoiced bridge ----------------
bridge_rows = []
won = actual.revenue.iloc[:ACTUAL_THROUGH].sum()
shipping_tax = won * 0.062          # shipping and tax billed but not in CRM amounts
timing = -won * 0.021               # won in month but invoiced later (not yet shipped)
discount_adj = -won * 0.004         # credit notes and rounding
bridge = pd.Series({"CRM closed-won": won, "+ shipping and tax billed": shipping_tax,
                    "- orders won, not yet shipped": timing, "- credits and adjustments": discount_adj})
bridge["= Invoiced (accounting)"] = bridge.sum()
bridge.round(0).to_csv(DATA / "won_to_invoiced_bridge.csv", header=["usd"])

# ---------------- 4. cash flow from DSO ----------------
DSO = {"Direct": 6, "Distributor": 45, "Marketplace": 38}
cash = pd.DataFrame(index=MONTHS)
cash["cash_in"] = 0.0
for r in ROUTES:
    lag = int(round(DSO[r] / 30))
    cash["cash_in"] += fc[f"rev_{r}"].shift(lag).fillna(fc[f"rev_{r}"].iloc[0])
cash["cash_out"] = fc.cogs + fc[list(OPEX)].sum(axis=1)
cash["net_cash"] = cash.cash_in - cash.cash_out
cash["closing_cash"] = 180_000 + cash.net_cash.cumsum()
cash.round(0).to_csv(DATA / "cash_flow.csv")

# ---------------- 5. scenarios ----------------
def scen(name, rev_mult=1.0, cogs_mult=1.0, opex_mult=1.0):
    f = pf.iloc[ACTUAL_THROUGH:]
    rev_f = f.revenue.sum() * rev_mult
    cogs_f = f.cogs.sum() * rev_mult * cogs_mult
    opex_f = f.opex.sum() * opex_mult
    rev = pa.revenue.iloc[:ACTUAL_THROUGH].sum() + rev_f
    op = pa.operating_profit.iloc[:ACTUAL_THROUGH].sum() + (rev_f - cogs_f - opex_f)
    return dict(scenario=name, full_year_revenue=round(rev), full_year_operating_profit=round(op))
scenarios = pd.DataFrame([scen("Base forecast"), scen("Pipeline converts 15% lower", .85),
                          scen("Pipeline converts 10% higher", 1.10), scen("Shipping and COGS +8%", 1.0, 1.08),
                          scen("Hiring: opex +10%", 1.0, 1.0, 1.10)])
scenarios["vs_budget_revenue"] = scenarios.full_year_revenue - pb.revenue.sum()
scenarios["vs_budget_revenue"] = scenarios.vs_budget_revenue.round(0)
scenarios.to_csv(DATA / "scenarios.csv", index=False)
print(var.round(0).to_string())
print(scenarios.to_string(index=False))
print("full-year: budget", round(pb.revenue.sum()), "forecast", round(pf.revenue.sum()),
      "op profit budget", round(pb.operating_profit.sum()), "forecast", round(pf.operating_profit.sum()))

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("RB Tech | Budget, forecast and P&L (synthetic data)", fontsize=13, weight="bold")
m = [str(p)[-2:] for p in MONTHS]
ax[0].plot(m, pb.revenue / 1000, color=GREY, marker="o", ms=3, label="Budget")
ax[0].plot(m[:ACTUAL_THROUGH], pa.revenue.iloc[:ACTUAL_THROUGH] / 1000, color=BLUE, marker="o", ms=3, label="Actual")
ax[0].plot(m[ACTUAL_THROUGH - 1:], pf.revenue.iloc[ACTUAL_THROUGH - 1:] / 1000, color=TEAL, ls="--", marker="o", ms=3, label="Forecast")
ax[0].legend(fontsize=8)
ax[0].set(title="Monthly revenue", ylabel="$K")
v = var.loc[["revenue", "cogs", "opex", "operating_profit"], "variance"] / 1000
ax[1].barh(["Revenue", "COGS", "Opex", "Operating profit"][::-1], v.values[::-1], color=[(TEAL if x > 0 else RED) if lab in ("Revenue", "Operating profit") else (TEAL if x < 0 else RED) for lab, x in zip(["Revenue", "COGS", "Opex", "Operating profit"][::-1], v.values[::-1])])
ax[1].axvline(0, color="k", lw=.6)
ax[1].set(title="YTD variance vs budget ($K, green = favorable)", xlabel="actual minus budget")
labels = list(bridge.index)
vals = bridge.values
steps = [vals[0], vals[1], vals[2], vals[3]]
bottoms = [0, vals[0], vals[0] + vals[1] + min(vals[2], 0), vals[0] + vals[1] + vals[2] + min(vals[3], 0)]
ax[2].bar(range(4), [abs(s) for s in steps], bottom=bottoms, color=[BLUE, TEAL, RED, RED])
ax[2].bar(4, vals[4], color=GOLD)
ax[2].set_xticks(range(5), ["CRM\nwon", "+ship/tax", "- not yet\nshipped", "- credits", "Invoiced"], fontsize=8)
ax[2].set(title="Won to invoiced bridge ($)", ylim=(vals[4] * .85, vals[1] + vals[0] * 1.03))
ax[3].bar(m, cash.net_cash / 1000, color=[TEAL if x > 0 else RED for x in cash.net_cash])
ax3 = ax[3].twinx()
ax3.plot(m, cash.closing_cash / 1000, color=BLUE, marker="o", ms=3)
ax3.spines["top"].set_visible(False)
ax[3].set(title="Cash flow: net monthly (bars), closing cash (line)", ylabel="$K net")
ax3.set_ylabel("$K closing")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "budget_forecast_overview.png", dpi=130)
print("done")
