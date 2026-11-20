"""Generate synthetic CRM data for RB Tech (fictional) and render the KPI dashboard.

Everything here is invented. Names, customers, prices and volumes do not belong to any real company.
Run:  python scripts/generate_data.py          (writes data/*.csv and charts/*.png)
Needs: pandas, numpy, matplotlib
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SEED = 2026
ROOT = Path(__file__).resolve().parent.parent
DATA, CHARTS = ROOT / "data", ROOT / "charts"
DATA.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)
rng = np.random.default_rng(SEED)

REPS = ["Avery Stone", "Jordan Pike", "Casey Lund"]
SOURCES = {  # name: (share of deals, relative win rate)
    "Field Sales Prospecting": (0.30, 1.0), "Large Conferences": (0.25, 0.9),
    "Inside Sales": (0.15, 0.5), "Inbound Organic": (0.10, 1.2),
    "Webinars": (0.08, 0.8), "Referral/Other": (0.07, 1.6), "Launch Campaigns": (0.05, 1.3),
}
PRODUCTS = {  # name: unit price (USD, invented)
    "Progenitor Cells 1x10^6": 600, "Endothelial Cells 1x10^6": 750,
    "Neural Media Kit": 1200, "Vascular Media Kit": 270,
    "Small Molecule 10mg": 100, "Expansion Medium Kit": 199, "Custom Project": 50000,
}
CUSTOMERS = [f"{a} {b}" for a in ["Northbridge", "Lakeshore", "Summit", "Harbor", "Cedar", "Ridgeway",
                                  "Evergreen", "Bluestone", "Meridian", "Granite", "Willow", "Atlas"]
             for b in ["University", "Institute", "Biologics", "Therapeutics", "Research Labs"]]
SEGMENTS = ["Academia", "Biotech", "Pharma", "CRO", "Hospital", "Government", "Core Facility"]
REGIONS = {"United States": 0.78, "Canada": 0.08, "Europe": 0.10, "Asia": 0.04}
STAGES = [("Discovery and Scoping", 0.15), ("Proposal/Quote Sent", 0.30),
          ("Verbal Commit", 0.60), ("Closed Won", 1.00), ("Closed Lost", 0.0)]
FORECAST = {"Discovery and Scoping": "PIPELINE", "Proposal/Quote Sent": "BEST_CASE",
            "Verbal Commit": "COMMIT", "Closed Won": "CLOSED", "Closed Lost": "LOST"}

# ---------- leads (contact level) with decaying engagement score ----------
N_LEADS = 24000
created = pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 320, N_LEADS), unit="D")
score = np.clip(rng.gamma(1.1, 6.0, N_LEADS), 0, 100).round()
leads = pd.DataFrame({
    "lead_id": [f"L{100000 + i}" for i in range(N_LEADS)],
    "created_date": created.date,
    "source": rng.choice(list(SOURCES), N_LEADS, p=[v[0] for v in SOURCES.values()]),
    "segment": rng.choice(SEGMENTS, N_LEADS, p=[.42, .22, .08, .10, .06, .06, .06]),
    "region": rng.choice(list(REGIONS), N_LEADS, p=list(REGIONS.values())),
    "lead_score": score,
})
leads["lifecycle_stage"] = np.select(
    [leads.lead_score >= 30, leads.lead_score >= 15], ["SQL", "MQL"], "Lead")
leads["in_sequence"] = rng.random(N_LEADS) < 0.38

# ---------- deals ----------
N_DEALS = 130
d_created = pd.to_datetime("2026-01-05") + pd.to_timedelta(rng.integers(0, 300, N_DEALS), unit="D")
src = rng.choice(list(SOURCES), N_DEALS, p=[v[0] for v in SOURCES.values()])
rows = []
for i in range(N_DEALS):
    prod = rng.choice(list(PRODUCTS), p=[.20, .14, .10, .12, .16, .10, .18])
    qty = int(rng.integers(1, 9)) if prod != "Custom Project" else 1
    amount = qty * PRODUCTS[prod] * (1 - rng.choice([0, 0, .05, .10]))
    pipeline = ("Custom Project" if prod == "Custom Project"
                else "Non-Revenue (Free Sample)" if rng.random() < .12 else "Sales")
    win_p = 0.30 * SOURCES[src[i]][1] if prod != "Custom Project" else 0.0
    r = rng.random()
    stage = ("Closed Won" if r < win_p else "Closed Lost" if r < win_p + .45
             else str(rng.choice([s for s, _ in STAGES[:3]], p=[.4, .4, .2])))
    cycle = int(np.clip(rng.normal(35 if pipeline == "Sales" else 25, 12), 3, 120))
    close = d_created[i] + pd.Timedelta(days=cycle)
    if pipeline.startswith("Non-Revenue"):
        amount = 0
    if prod == "Custom Project":  # large, slow deals: stay in open pipeline or are lost
        amount = float(rng.choice([150000, 200000, 250000]))
    rows.append(dict(
        deal_id=f"D{5000 + i}", deal_name=f"{rng.choice(CUSTOMERS)} - {prod}",
        owner=rng.choice(REPS, p=[.42, .36, .22]), pipeline=pipeline, product=prod, quantity=qty,
        amount=round(float(amount), 2), deal_source=src[i], stage=stage,
        forecast_category=FORECAST[stage], create_date=d_created[i].date(),
        close_date=close.date(), sales_cycle_days=cycle,
        region=rng.choice(list(REGIONS), p=list(REGIONS.values()))))
deals = pd.DataFrame(rows)
deals["weighted_amount"] = deals.amount * deals.stage.map(dict(STAGES))
# a few deliberately incomplete records so the data-quality check has something to catch
deals.loc[rng.choice(N_DEALS, 4, replace=False), "product"] = ""
won = deals[(deals.stage == "Closed Won") & (deals.pipeline != "Non-Revenue (Free Sample)")].copy()
won["close_month"] = pd.to_datetime(won.close_date).dt.to_period("M").astype(str)
won["close_quarter"] = "Q" + pd.to_datetime(won.close_date).dt.quarter.astype(str)

# ---------- support tickets ----------
N_T = 180
tickets = pd.DataFrame({
    "ticket_id": [f"T{9000 + i}" for i in range(N_T)],
    "category": rng.choice(["Spam", "Pre-sale Support", "Order/Shipping", "Troubleshooting",
                            "Documentation Request", "Large-scale/Custom Order Request", "Accounting"],
                           N_T, p=[.5, .14, .10, .07, .06, .08, .05]),
    "owner": rng.choice(REPS + ["Ops Lead"], N_T, p=[.1, .1, .1, .7]),
})
tickets["days_to_close"] = np.where(tickets.category == "Spam", rng.exponential(1, N_T),
                                    rng.gamma(2, 6, N_T)).round(1)
tickets["stage"] = "Closed"

# ---------- weekly activity ----------
weeks = pd.date_range("2026-01-05", periods=44, freq="W-MON")
activity = pd.DataFrame([dict(week=w.date(), rep=r,
                              emails_sent=int(rng.gamma(4, 18)), contacts_added=int(rng.gamma(2, 10)),
                              tasks_created=int(rng.gamma(2, 4)), meetings=int(rng.poisson(2)))
                         for w in weeks for r in REPS])
activity["emails_sent"] *= np.where(activity.rep == REPS[0], 2, 1)

for name, df in {"leads": leads, "deals": deals, "closed_won": won, "tickets": tickets,
                 "weekly_activity": activity}.items():
    df.to_csv(DATA / f"{name}.csv", index=False)

# ---------- KPIs ----------
stage_cnt = leads.lifecycle_stage.value_counts()
n_lead, n_mql, n_sql = len(leads), (leads.lead_score >= 15).sum(), (leads.lead_score >= 30).sum()
n_opp, n_cust = len(deals), len(won)
kpi = {
    "revenue_ytd": round(won.amount.sum(), 2), "orders": n_cust,
    "avg_order_value": round(won.amount.mean(), 2),
    "avg_sales_cycle_days": round(deals[deals.pipeline == "Sales"].sales_cycle_days.mean(), 1),
    "win_rate": round(n_cust / max((deals.stage.isin(["Closed Won", "Closed Lost"])).sum(), 1), 3),
    "open_pipeline": round(deals[~deals.stage.isin(["Closed Won", "Closed Lost"])].amount.sum(), 2),
    "weighted_forecast": round(deals[~deals.stage.isin(["Closed Won", "Closed Lost"])].weighted_amount.sum(), 2),
    "mql_to_sql": round(n_sql / n_mql, 4), "sql_to_opp": round(n_opp / n_sql, 4),
    "lead_to_customer": round(n_cust / n_lead, 5),
    "missing_product_on_deal": int((deals["product"] == "").sum()),
}
pd.Series(kpi).to_csv(DATA / "kpi_summary.csv", header=["value"])
print(pd.Series(kpi).to_string())

# ---------- charts ----------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#9AA5B1"
fig, ax = plt.subplots(2, 3, figsize=(16, 8.5))
fig.suptitle("RB Tech | Sales Performance & Ops KPIs (synthetic data)", fontsize=14, weight="bold")

m = won.groupby("close_month").amount.sum()
ax[0, 0].bar(m.index.str[-2:], m.values / 1000, color=BLUE)
ax[0, 0].set(title=f"Closed-won revenue by month  (YTD ${kpi['revenue_ytd']/1000:,.0f}K)", ylabel="$K")

r = won.groupby("owner").amount.sum().sort_values()
ax[0, 1].barh(r.index, r.values / 1000, color=TEAL)
ax[0, 1].set(title="Revenue by rep", xlabel="$K")

stages = ["Lead", "MQL", "SQL", "Opportunity", "Customer"]
vals = [n_lead, n_mql, n_sql, n_opp, n_cust]
ax[0, 2].barh(stages[::-1], vals[::-1], color=[GOLD, GOLD, BLUE, BLUE, BLUE][::-1])
ax[0, 2].set_xscale("log")
for y, v in enumerate(vals[::-1]):
    ax[0, 2].text(v * 1.1, y, f"{v:,}", va="center")
ax[0, 2].set(title=f"Funnel (log scale) | lead to customer {kpi['lead_to_customer']:.3%}")

s = deals.groupby("deal_source").amount.sum().sort_values()
ax[1, 0].barh(s.index, s.values / 1000, color=GOLD)
ax[1, 0].set(title="Pipeline value by deal source", xlabel="$K")

openx = deals[~deals.stage.isin(["Closed Won", "Closed Lost"])].groupby("forecast_category").amount.sum()
ax[1, 1].bar(openx.index, openx.values / 1000, color=[BLUE, TEAL, GREY][: len(openx)])
ax[1, 1].set(title=f"Open pipeline by forecast category  (weighted ${kpi['weighted_forecast']/1000:,.0f}K)", ylabel="$K")

t = tickets.groupby("owner").days_to_close.mean().sort_values()
ax[1, 2].barh(t.index, t.values, color=GREY)
ax[1, 2].set(title="Avg days to close support ticket", xlabel="days")

fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(CHARTS / "dashboard_overview.png", dpi=130)

# ---------- page 2: forecast and product heatmaps ----------
AS_OF = pd.Timestamp("2026-10-31")
won["m"] = pd.to_datetime(won.close_date).dt.to_period("M")
actual = won.groupby("m").amount.sum()
actual = actual.reindex(pd.period_range("2026-01", pd.Period(AS_OF, "M"), freq="M"), fill_value=0)
months_ahead = pd.period_range(pd.Period(AS_OF, "M") + 1, periods=2, freq="M")
open_ = deals[~deals.stage.isin(["Closed Won", "Closed Lost"]) & (deals.pipeline != "Non-Revenue (Free Sample)") & (deals.pipeline != "Custom Project")].copy()
open_["m"] = pd.to_datetime(open_.close_date).dt.to_period("M").clip(lower=months_ahead[0])   # overdue deals roll into next month
open_ = open_[open_.m <= months_ahead[-1]]
w_by_cat = open_.pivot_table(index="m", columns="forecast_category", values="weighted_amount", aggfunc="sum", fill_value=0).reindex(months_ahead, fill_value=0)
run_rate = actual.tail(3).mean()
base = (w_by_cat.sum(axis=1) + run_rate * .8).rename("base")                    # weighted pipeline plus 80% of the recent run rate for deals not yet created
low = base * .65                                                                # cautious: best-case and pipeline deals slip
high = base * 1.35                                                              # upside: best-case deals close faster
fc = pd.DataFrame({"low": low, "base": base, "high": high}).round(0)
fc.to_csv(DATA / "forecast_range.csv")
cum_actual = actual.cumsum()
heat_region = won.pivot_table(index="product", columns="region", values="amount", aggfunc="sum", fill_value=0)
heat_qtr = won.pivot_table(index="product", columns="close_quarter", values="amount", aggfunc="sum", fill_value=0)
heat_rep = won.pivot_table(index="product", columns="owner", values="amount", aggfunc="sum", fill_value=0)
heat_region.to_csv(DATA / "product_by_region.csv"); heat_qtr.to_csv(DATA / "product_by_quarter.csv"); heat_rep.to_csv(DATA / "product_by_rep.csv")

fig2, a = plt.subplots(2, 3, figsize=(16, 8.8))
fig2.suptitle("RB Tech | Forecast and product performance (synthetic data)", fontsize=14, weight="bold")
am = [m.strftime("%b") for m in actual.index]
fm = [m.strftime("%b") for m in months_ahead]
a[0, 0].bar(am, actual.values / 1000, color=BLUE, label="Actual (closed-won)")
a[0, 0].tick_params(axis="x", labelsize=8)
a[0, 0].set(title="Revenue closed so far, by month", ylabel="$K")
a[0, 0].legend(fontsize=8)
tot_closed = actual.sum() / 1000
ye = {"Closed so far": tot_closed, "Low": tot_closed + fc.low.sum() / 1000, "Base": tot_closed + fc.base.sum() / 1000, "High": tot_closed + fc.high.sum() / 1000}
a[0, 1].bar(list(ye), list(ye.values()), color=[BLUE, GREY, GOLD, TEAL])
for i_, v_ in enumerate(ye.values()):
    a[0, 1].text(i_, v_ + 1.5, f"${v_:,.0f}K", ha="center", weight="bold")
a[0, 1].set(title="Where the year may end: low, base and high", ylabel="$K")
a[0, 1].text(.5, -.16, f"Forecast for {fm[0]} and {fm[1]}: base = weighted pipeline + 80% of recent run rate; low = base x 0.65; high = base x 1.35", transform=a[0, 1].transAxes, ha="center", fontsize=7.5, color="#444")
bot = np.zeros(len(w_by_cat))
for col_, c_ in [("COMMIT", TEAL), ("BEST_CASE", GOLD), ("PIPELINE", GREY)]:
    if col_ in w_by_cat:
        a[0, 2].bar([str(m)[-5:] for m in w_by_cat.index], w_by_cat[col_] / 1000, bottom=bot, color=c_, label=col_.replace("_", " ").title())
        bot += w_by_cat[col_].values / 1000
a[0, 2].legend(fontsize=7)
a[0, 2].set(title="Weighted open pipeline by forecast category", ylabel="$K")
def heat(ax, df, title):
    im = ax.imshow(df.values / 1000, cmap="Blues", aspect="auto")
    ax.set_xticks(range(df.shape[1]), [c.replace("United States", "US") for c in df.columns], rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(df.shape[0]), [i.replace(" 1x10^6", "") for i in df.index], fontsize=8)
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            v = df.values[i, j] / 1000
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7, color="white" if v > df.values.max() / 1000 * .55 else "black")
    ax.set_title(title)
heat(a[1, 0], heat_region, "Product by region, closed-won ($K)")
heat(a[1, 1], heat_qtr, "Product by quarter, closed-won ($K)")
heat(a[1, 2], heat_rep, "Product by rep, closed-won ($K)")
fig2.tight_layout(rect=[0, 0, 1, .95])
fig2.savefig(CHARTS / "dashboard_forecast_and_products.png", dpi=130)
print("forecast", fc.to_dict("list"))
print("done")
