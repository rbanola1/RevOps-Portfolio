"""Trade show budget and return model for RB Tech (fictional).

Eight synthetic events with full cost lines, leads, deals and revenue; computes cost per lead, cost per deal,
return on spend, payback time, and a repeat / change / drop score. Also runs a simple budget reallocation.
All data is invented. Run: python scripts/tradeshow_roi.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(1201)

# name, audience fit (0-1), booth size, travelers, days
EVENTS = [("Neuroscience Annual Meeting", .85, "20x20", 4, 5), ("Stem Cell Research Summit", .95, "10x20", 3, 4),
          ("Toxicology Congress", .70, "10x20", 3, 4), ("Lab Automation Expo", .45, "10x10", 2, 3),
          ("Regional Biotech Showcase", .65, "10x10", 2, 2), ("Drug Discovery Conference", .60, "10x20", 3, 4),
          ("Cell Therapy Forum", .90, "10x10", 2, 3), ("Core Facilities Meeting", .55, "tabletop", 2, 3)]
BOOTH_COST = {"20x20": 10500, "10x20": 5300, "10x10": 2800, "tabletop": 900}
rows = []
for name, fit, booth, trav, days in EVENTS:
    reg = BOOTH_COST[booth] * rng.uniform(.95, 1.1)
    build = {"20x20": 2300, "10x20": 1400, "10x10": 650, "tabletop": 150}[booth] * rng.uniform(.9, 1.2)
    ship = {"20x20": 1000, "10x20": 650, "10x10": 330, "tabletop": 100}[booth] * rng.uniform(.9, 1.3)
    travel = trav * (days * 250 + 500) * rng.uniform(.9, 1.2)       # hotel + meals + flights
    marketing = 500 + 700 * fit * rng.uniform(.6, 1.2)
    staff_time = trav * (days + 2) * 220                            # loaded daily cost of staff time
    SC = .5                                                         # small-company scale
    reg, build, ship, travel, marketing, staff_time = (x * SC for x in (reg, build, ship, travel, marketing, staff_time))
    cost = reg + build + ship + travel + marketing + staff_time
    # first-year revenue scales with audience fit (the main driver of event value), then leads and scans are derived from it
    revenue = cost * (.55 + 5.3 * (fit - .45)) * rng.uniform(.88, 1.12)
    avg_deal = rng.uniform(9000, 13000)
    deals = max(1, int(revenue / avg_deal))
    qual = int(deals / rng.uniform(.10, .14))
    scans = int(qual / (.25 + .2 * fit))
    rows.append(dict(event=name, booth=booth, audience_fit=fit, registration=round(reg), booth_build=round(build), shipping=round(ship),
                     travel=round(travel), pre_event_marketing=round(marketing), staff_time=round(staff_time), total_cost=round(cost),
                     badge_scans=scans, qualified_leads=qual, deals=deals, first_year_revenue=round(revenue)))
ev = pd.DataFrame(rows)
ev["cost_per_qualified_lead"] = (ev.total_cost / ev.qualified_leads).round(0)
ev["cost_per_deal"] = (ev.total_cost / ev.deals.replace(0, np.nan)).round(0)
ev["return_on_spend"] = (ev.first_year_revenue / ev.total_cost).round(2)
ev["payback_months"] = (12 * ev.total_cost / ev.first_year_revenue).round(1)

# gross margin applied to revenue before judging return
GM = .62
ev["gross_profit_return"] = (ev.first_year_revenue * GM / ev.total_cost).round(2)
# score: 50% gross-profit return, 30% cost per lead (lower better), 20% audience fit
z = lambda s: (s - s.min()) / (s.max() - s.min())
ev["score"] = (50 * z(ev.gross_profit_return) + 30 * (1 - z(ev.cost_per_qualified_lead)) + 20 * z(ev.audience_fit)).round(0)
ev["decision"] = np.where(ev.gross_profit_return >= 1.2, "Repeat", np.where(ev.gross_profit_return >= .8, "Change", "Drop"))
ev = ev.sort_values("score", ascending=False)
ev.to_csv(DATA / "event_roi.csv", index=False)

budget = ev.total_cost.sum()
keep = ev[ev.decision != "Drop"]
realloc = pd.DataFrame({"scenario": ["Current plan", "Drop low-return shows, move budget to best three"],
                        "spend": [budget, budget],
                        "expected_gross_profit": [(ev.first_year_revenue * GM).sum(),
                                                  (keep.first_year_revenue * GM).sum() +
                                                  (budget - keep.total_cost.sum()) * ev.head(3).gross_profit_return.mean() * .7]}).round(0)
realloc.to_csv(DATA / "budget_reallocation.csv", index=False)
cost_lines = ev[["registration", "booth_build", "shipping", "travel", "pre_event_marketing", "staff_time"]].sum().round(0)
cost_lines.to_csv(DATA / "cost_breakdown.csv", header=["total"])
print(ev[["event", "total_cost", "qualified_leads", "deals", "first_year_revenue", "cost_per_qualified_lead", "gross_profit_return", "decision"]].to_string(index=False))
print(realloc.to_string(index=False)); print(cost_lines)

plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
col = {"Repeat": TEAL, "Change": GOLD, "Drop": RED}
fig, ax = plt.subplots(2, 3, figsize=(18, 9))
fig.suptitle("RB Tech | Trade show budget and return (synthetic data)", fontsize=13, weight="bold")
e2 = ev.sort_values("total_cost")
ax[0, 0].barh([n[:22] for n in e2.event], e2.total_cost / 1e3, color=BLUE)
ax[0, 0].set(title="Total cost per event ($K)", xlabel="$K")
ax[0, 1].pie(cost_lines.values, labels=[c.replace("_", " ") for c in cost_lines.index], autopct="%1.0f%%", colors=plt.cm.Blues(np.linspace(.9, .3, 6)),
             textprops={"fontsize": 8})
ax[0, 1].set(title="Where the money goes (all events)")
e3 = ev.sort_values("cost_per_qualified_lead")
ax[0, 2].barh([n[:22] for n in e3.event][::-1], e3.cost_per_qualified_lead[::-1], color=[col[d] for d in e3.decision[::-1]])
ax[0, 2].set(title="Cost per qualified lead ($)", xlabel="$")
ax[1, 0].scatter(ev.total_cost / 1e3, ev.first_year_revenue / 1e3, s=ev.deals * 25, c=[col[d] for d in ev.decision], alpha=.8)
for _, r in ev.iterrows():
    ax[1, 0].annotate(r.event[:14], (r.total_cost / 1e3, r.first_year_revenue / 1e3), fontsize=7, xytext=(4, 4), textcoords="offset points")
lim = max(ev.total_cost.max(), ev.first_year_revenue.max()) / 1e3
ax[1, 0].plot([0, lim], [0, lim], color="k", lw=.6, ls="--")
ax[1, 0].set(title="Cost vs first-year revenue (bubble = deals; dashed = break-even)", xlabel="cost $K", ylabel="revenue $K")
e4 = ev.sort_values("gross_profit_return")
ax[1, 1].barh([n[:22] for n in e4.event], e4.gross_profit_return, color=[col[d] for d in e4.decision])
ax[1, 1].axvline(1, color="k", lw=.7)
ax[1, 1].set(title="Gross-profit return per $1 spent (1.0 = break-even)", xlabel="x")
ax[1, 2].bar(["Current plan", "Reallocated"], realloc.expected_gross_profit / 1e3, color=[GREY, TEAL], width=.5)
for i, v in enumerate(realloc.expected_gross_profit / 1e3):
    ax[1, 2].text(i, v + 8, f"${v:,.0f}K", ha="center", weight="bold")
ax[1, 2].set(title="Expected gross profit on the same budget ($K)", ylabel="$K")
fig.tight_layout(rect=[0, 0, 1, .95])
fig.savefig(CHARTS / "tradeshow_roi_dashboard.png", dpi=125)
print("done")
