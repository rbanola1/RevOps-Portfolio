"""Forecast suite for RB Tech (fictional): five forecasts that answer five different questions.

1 Inbound lead forecast  2 Deal and revenue plan (reverse funnel)  3 Revenue recognition forecast
4 Product forecast       5 Demand (units and stock cover) forecast
All numbers are invented. Run: python scripts/forecast_suite.py    Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(808)
M = pd.period_range("2026-01", "2026-12", freq="M")
MN = [m.strftime("%b") for m in M]
SEAS = np.array([.85, .95, 1.1, 1.05, .95, .9, .8, .85, 1.1, 1.25, 1.0, .8])   # seasonality index (conference season in spring and autumn)

# ---------- 1. inbound lead forecast ----------
# leads = visitors x visit-to-lead rate + webinar attendees x lead rate + event scans x qualify rate
visitors = (4200 * SEAS * (1 + .015 * np.arange(12))).round()
webinar_att = np.array([0, 60, 0, 80, 0, 70, 0, 0, 90, 0, 75, 0])
event_scans = np.array([0, 0, 420, 0, 0, 380, 0, 0, 0, 520, 0, 0])
leads = pd.DataFrame({"month": MN, "website": (visitors * .012).round(), "webinars": (webinar_att * .45).round(), "events": (event_scans * .30).round()})
leads["total_leads"] = leads[["website", "webinars", "events"]].sum(axis=1)
leads.to_csv(DATA / "forecast_inbound_leads.csv", index=False)

# ---------- 2. deal and revenue plan (reverse funnel) ----------
TARGET, DEAL = 240_000, 5_000
deals_needed = TARGET / DEAL
CH = {"Large conferences": (.26, 18), "Regional events": (.26, 16), "Field prospecting": (.19, 12), "Webinars": (.13, 10), "Inside sales": (.04, 5),
      "Inbound organic": (.02, 4), "Launches": (.02, 4), "Beta programmes": (.02, 3), "Partners and distributors": (.02, 6), "Other": (.04, 4)}
ch = pd.DataFrame([(k, v[0], TARGET * v[0], TARGET * v[0] / DEAL, v[1]) for k, v in CH.items()],
                  columns=["channel", "share", "revenue_target", "deals_needed", "close_rate_pct_of_qualified"])
ch["qualified_leads_needed"] = (ch.deals_needed / (ch.close_rate_pct_of_qualified / 100)).round()
ch["deals_needed"] = ch.deals_needed.round(1)
ch.to_csv(DATA / "forecast_deal_plan.csv", index=False)

# ---------- 3. revenue recognition: orders won -> invoiced -> recognised ----------
bookings = np.array([14, 18, 22, 25, 21, 24, 20, 19, 26, 31, 24, 18]) * 1000.0
LAG = [.40, .35, .15, .10]          # share recognised in the month of the order and the next three months
rec = np.zeros(12 + 3)
for i, b in enumerate(bookings):
    for k, s in enumerate(LAG):
        rec[i + k] += b * s
rec = rec[:12]
rr = pd.DataFrame({"month": MN, "bookings": bookings, "recognised_revenue": rec.round(0), "gap": (bookings - rec).round(0)})
rr["cumulative_deferred"] = rr.gap.cumsum()
rr.to_csv(DATA / "forecast_revenue_recognition.csv", index=False)

# ---------- 4. product forecast (revenue by product, with a launch ramp) ----------
PROD = {"Cell Line A": (6200, .010), "Cell Line B": (5400, .008), "Media Kit C": (3000, .015), "Compound Sets": (2200, .006)}
pf = pd.DataFrame({"month": MN})
for p, (base, g) in PROD.items():
    pf[p] = (base * SEAS * (1 + g * np.arange(12))).round()
launch = np.array([0, 0, 0, 0, 0, 0, 800, 2000, 3600, 4800, 5600, 6200.0])        # new product from July: ramps up over six months
pf["New growth medium (launch July)"] = launch
pf["total"] = pf.drop(columns="month").sum(axis=1)
pf.to_csv(DATA / "forecast_product_revenue.csv", index=False)

# ---------- 5. demand forecast (units) and stock cover ----------
UNITS = {"Cell Line A": 9, "Cell Line B": 8, "Media Kit C": 3, "Compound Sets": 55}
dm = pd.DataFrame({"month": MN})
for p, u in UNITS.items():
    dm[p] = (u * SEAS * (1 + .012 * np.arange(12)) * rng.uniform(.95, 1.05, 12)).round()
stock = {"Cell Line A": 70, "Cell Line B": 40, "Media Kit C": 36, "Compound Sets": 420}
cover = {}
for p in UNITS:
    cum = dm[p].cumsum()
    cover[p] = int((cum <= stock[p]).sum())          # months of cover from current stock at forecast demand
cover = pd.Series(cover, name="months_of_cover")
reorder = pd.DataFrame({"product": list(UNITS), "stock_on_hand": list(stock.values()), "avg_monthly_demand_next_6": [round(dm[p][6:].mean(), 1) for p in UNITS],
                        "months_of_cover": cover.values})
reorder["action"] = np.where(reorder.months_of_cover < 4, "Reorder now", np.where(reorder.months_of_cover < 6, "Reorder soon", "OK"))
dm.to_csv(DATA / "forecast_demand_units.csv", index=False)
reorder.to_csv(DATA / "forecast_stock_cover.csv", index=False)

# ---------- 6. accuracy back-test: how wrong were last year's forecasts? ----------
acc = pd.DataFrame({"forecast": ["Inbound leads", "Revenue plan by channel", "Revenue recognition", "Product revenue", "Unit demand"],
                    "typical_error_pct": [12, 22, 6, 15, 18], "how_measured": ["Forecast vs actual leads, 3-month average", "Planned vs actual revenue by channel",
                                                                                 "Recognised vs forecast recognised", "Forecast vs actual by product", "Forecast vs actual units shipped"]})
acc.to_csv(DATA / "forecast_accuracy.csv", index=False)
print(ch[["channel", "revenue_target", "deals_needed", "qualified_leads_needed"]].to_string(index=False)); print(rr.tail(3)); print(reorder)

# ---------- dashboard: one plain chart per question ----------
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(2, 3, figsize=(20, 10.5))
fig.suptitle("RB Tech | Forecast suite: five forecasts, five questions (synthetic data)", fontsize=14, weight="bold")

ax[0, 0].bar(MN, leads.website, color=BLUE, label="Website")
ax[0, 0].bar(MN, leads.webinars, bottom=leads.website, color=TEAL, label="Webinars")
ax[0, 0].bar(MN, leads.events, bottom=leads.website + leads.webinars, color=GOLD, label="Events")
ax[0, 0].legend(fontsize=8, ncol=3, loc="upper left")
ax[0, 0].set(title="1  How many leads will arrive each month?", ylabel="leads")
ax[0, 0].text(.01, -.2, "Leads = visitors x 1.2% + webinar attendees x 45% + event scans x 30%, times seasonality", transform=ax[0, 0].transAxes, fontsize=8, color="#444")

c = ch.sort_values("revenue_target")
ax[0, 1].barh(c.channel, c.revenue_target / 1000, color=BLUE)
for y, (r, dl) in enumerate(zip(c.revenue_target / 1000, c.deals_needed)):
    ax[0, 1].text(r + 1, y, f"${r:,.0f}K  ({dl:.0f} deal{'' if round(dl) == 1 else 's'})", va="center", fontsize=8)
ax[0, 1].set_xlim(0, 85)
ax[0, 1].set(title=f"2  Which channels must deliver the ${TARGET/1000:,.0f}K target?", xlabel="$K")
ax[0, 1].text(.01, -.2, f"Deals needed = target / average deal (${DEAL:,}) = {deals_needed:.0f}; leads needed = deals / close rate", transform=ax[0, 1].transAxes, fontsize=8, color="#444")

x = np.arange(12)
ax[0, 2].bar(x - .2, bookings / 1000, .4, color=GREY, label="Orders won (bookings)")
ax[0, 2].bar(x + .2, rec / 1000, .4, color=TEAL, label="Revenue recognised")
ax[0, 2].set_xticks(x, MN)
ax[0, 2].legend(fontsize=8, loc="upper left")
ax[0, 2].set(title="3  When will won orders turn into recognised revenue?", ylabel="$K")
ax[0, 2].text(.01, -.2, "Recognised = 40% in order month, then 35%, 15%, 10% over the next 3 months", transform=ax[0, 2].transAxes, fontsize=8, color="#444")

cols = [c_ for c_ in pf.columns if c_ not in ("month", "total")]
ax[1, 0].stackplot(MN, [pf[c_] / 1000 for c_ in cols], labels=cols, colors=[BLUE, TEAL, GOLD, GREY, RED])
ax[1, 0].legend(fontsize=7, loc="upper left")
ax[1, 0].set(title="4  Which products will drive revenue?", ylabel="$K per month")
ax[1, 0].text(.01, -.2, "Product revenue = base x seasonality x growth; a new product follows a six-month ramp", transform=ax[1, 0].transAxes, fontsize=8, color="#444")

for p, c_ in zip(UNITS, [BLUE, TEAL, GOLD, GREY]):
    if p != "Compound Sets":
        ax[1, 1].plot(MN, dm[p], marker="o", ms=3, color=c_, label=p)
ax[1, 1].legend(fontsize=8)
ax[1, 1].set(title="5  How many units will customers order?", ylabel="units per month (compound sets not shown)")
ax[1, 1].text(.01, -.2, "Demand = recent average x seasonality x growth; compared with stock on hand to set reorders", transform=ax[1, 1].transAxes, fontsize=8, color="#444")

ax[1, 2].axis("off")
tbl = ax[1, 2].table(cellText=reorder[["product", "stock_on_hand", "months_of_cover", "action"]].values, colLabels=["Product", "Stock", "Months of cover", "Action"], loc="upper center", cellLoc="center", colWidths=[.36, .14, .24, .26])
tbl.auto_set_font_size(False)
tbl.set_fontsize(9)
tbl.scale(1, 1.8)
for (r, c_), cell in tbl.get_celld().items():
    if r > 0 and c_ == 3:
        a_ = reorder.action.iloc[r - 1]
        cell.set_facecolor({"Reorder now": "#F4C7CE", "Reorder soon": "#FBE5B6", "OK": "#CFE9E3"}[a_])
ax[1, 2].set_title("5b  What should operations order?", pad=14)
ax[1, 2].text(.5, .22, "Typical forecast error, last year\n" + "\n".join(f"{r.forecast}: about {r.typical_error_pct}%" for r in acc.itertuples()), ha="center", fontsize=9, transform=ax[1, 2].transAxes)
for a_ in (ax[0, 0], ax[0, 2], ax[1, 0], ax[1, 1]):
    a_.tick_params(axis="x", labelsize=8)
fig.tight_layout(rect=[0, .02, 1, .95], h_pad=4)
fig.savefig(CHARTS / "forecast_suite.png", dpi=125)
print("done")
