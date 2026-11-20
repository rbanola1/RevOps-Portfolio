"""Two simple forecasts for RB Tech (fictional): sales scenarios by forecast category, and product demand.

1 Sales scenarios: closed won, commit, best case and pipeline, each with a probability, for the next three months.
2 Product demand: units per product for the next six months, compared with stock to flag reorders.
All numbers are invented. Run: python scripts/forecast_scenarios_and_demand.py    Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(809)

# ---------- 1. sales scenarios by forecast category ----------
PROB = {"Closed won": 1.0, "Commit": .60, "Best case": .30, "Pipeline": .15}
MONTHS = ["Nov", "Dec", "Jan"]
open_value = pd.DataFrame({"Closed won": [9_000, 2_000, 0], "Commit": [17_000, 8_000, 3_000],
                           "Best case": [21_000, 15_000, 9_000], "Pipeline": [28_000, 30_000, 24_000]}, index=MONTHS)
weighted = open_value * pd.Series(PROB)
scen = pd.DataFrame({"scenario": ["Commit only", "Commit + best case", "All pipeline"],
                     "next_3_months": [weighted[["Closed won", "Commit"]].sum().sum(), weighted[["Closed won", "Commit", "Best case"]].sum().sum(),
                                       weighted.sum().sum()]}).round(0)
open_value.to_csv(DATA / "forecast_open_value_by_category.csv")
weighted.round(0).to_csv(DATA / "forecast_weighted_by_category.csv")
scen.to_csv(DATA / "forecast_scenarios.csv", index=False)

# ---------- 2. product demand and stock cover ----------
M6 = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
SEAS = np.array([1.0, .8, .85, 1.0, 1.1, 1.2])
BASE = {"Cell Line A": 9, "Cell Line B": 8, "Media Kit C": 3, "Compound Set": 55}
STOCK = {"Cell Line A": 70, "Cell Line B": 30, "Media Kit C": 36, "Compound Set": 420}
dm = pd.DataFrame({"month": M6})
for p, u in BASE.items():
    dm[p] = (u * SEAS * (1 + .012 * np.arange(6)) * rng.uniform(.95, 1.05, 6)).round()
rows = []
for p in BASE:
    cum = dm[p].cumsum()
    cover = int((cum <= STOCK[p]).sum())
    rows.append(dict(product=p, stock_on_hand=STOCK[p], avg_monthly_demand=round(dm[p].mean(), 1), months_of_cover=cover,
                     action="Reorder now" if cover < 3 else "Reorder soon" if cover < 5 else "OK"))
cover = pd.DataFrame(rows)
dm.to_csv(DATA / "product_demand_forecast.csv", index=False)
cover.to_csv(DATA / "stock_cover.csv", index=False)
print(scen.to_string(index=False)); print(cover.to_string(index=False))

# ---------- chart ----------
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 3, figsize=(19, 5.6))
fig.suptitle("RB Tech | Simple forecasts: sales scenarios and product demand (synthetic data)", fontsize=13, weight="bold")
bottom = np.zeros(3)
for cat, col in [("Closed won", BLUE), ("Commit", TEAL), ("Best case", GOLD), ("Pipeline", GREY)]:
    ax[0].bar(MONTHS, weighted[cat] / 1000, bottom=bottom, color=col, label=f"{cat} ({int(PROB[cat] * 100)}%)")
    bottom += weighted[cat].values / 1000
ax[0].legend(fontsize=8)
ax[0].set(title="Expected sales by forecast category (value x probability)", ylabel="$K")
cols = [TEAL, GOLD, GREY]
ax[1].bar(scen.scenario, scen.next_3_months / 1000, color=cols)
for i, v in enumerate(scen.next_3_months / 1000):
    ax[1].text(i, v + 1, f"${v:,.0f}K", ha="center", weight="bold")
ax[1].set(title="Three scenarios for the next three months", ylabel="$K")
ax[1].text(.5, -.14, "Commit only = closed won + commit. Best case adds best-case deals. All pipeline adds early-stage deals.", transform=ax[1].transAxes, ha="center", fontsize=8, color="#444")
for p, c in zip(["Cell Line A", "Cell Line B", "Media Kit C"], [BLUE, TEAL, GOLD]):
    ax[2].plot(M6, dm[p], marker="o", color=c, label=p)
ax[2].legend(fontsize=8)
ax[2].set(title="Product demand forecast (units per month)", ylabel="units")
tx = "   ".join(f"{r.product}: {r.months_of_cover} months of cover, {r.action}" for r in cover.itertuples())
ax[2].text(.5, -.14, "Stock cover: " + "; ".join(f"{r.product} {r.months_of_cover} mo ({r.action})" for r in cover.itertuples()), transform=ax[2].transAxes, ha="center", fontsize=7.5, color="#444", wrap=True)
fig.tight_layout(rect=[0, .03, 1, .93])
fig.savefig(CHARTS / "forecast_scenarios_and_demand.png", dpi=125)
print("done")
