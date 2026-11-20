"""Synthetic channel-sales model for RB Tech (fictional).

Three parts, all invented data:
  A. Distributor scorecard and outreach funnel
  B. B2B marketplace product feeds from one product master + a cross-platform discrepancy checker
  C. Channel economics: margin by route to market and the path to a channel revenue target
Run:  python scripts/channel_model.py     (writes data/*.csv and charts/channel_overview.png)
Needs: pandas, numpy, matplotlib
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, CHARTS = ROOT / "data", ROOT / "charts"
EXPORTS = DATA / "platform_exports"
for d in (DATA, CHARTS, EXPORTS):
    d.mkdir(exist_ok=True)
rng = np.random.default_rng(42)

# =====================================================================
# A. DISTRIBUTOR SCORECARD AND FUNNEL
# =====================================================================
FIRST = ["Alder", "Brenmar", "Calden", "Dorvik", "Elmstead", "Fenwick", "Garrow", "Halcyon", "Ivermoor",
         "Jandell", "Kestrel", "Lindqvist", "Marlow", "Norvane", "Oakridge", "Pelham", "Quillon", "Rowan",
         "Sterling", "Tavistock"]
SECOND = ["Scientific", "Biolabs", "Life Science Supply", "Bio Partners", "Lab Direct", "Research Supply"]
REGIONS = {"Germany": "EU", "France": "EU", "Italy": "EU", "Spain": "EU", "Benelux": "EU", "Nordics": "EU",
           "UK/IE": "EU", "Switzerland": "EU", "Japan": "Asia", "Korea": "Asia", "Singapore": "Asia",
           "Taiwan": "Asia", "Canada": "Americas"}
N_D = 40
d = pd.DataFrame({
    "distributor": [f"{FIRST[i % 20]} {SECOND[i % 6]}" for i in range(N_D)],
    "territory": rng.choice(list(REGIONS), N_D),
})
d["region"] = d.territory.map(REGIONS)
d["cold_chain_capable"] = rng.random(N_D) < 0.55          # can handle cryo shipping and import
d["own_warehouse"] = rng.random(N_D) < 0.7
d["reach_1_5"] = rng.integers(1, 6, N_D)
d["portfolio_fit_1_5"] = rng.integers(1, 6, N_D)
d["financial_health_1_5"] = rng.integers(2, 6, N_D)
d["competitor_overlap"] = rng.random(N_D) < 0.25
d["exclusive_to_competitor"] = rng.random(N_D) < 0.08
W = {"cold_chain": 30, "warehouse": 10, "reach": 15, "fit": 25, "health": 20}
d["score"] = (W["cold_chain"] * d.cold_chain_capable + W["warehouse"] * d.own_warehouse
              + W["reach"] * d.reach_1_5 / 5 + W["fit"] * d.portfolio_fit_1_5 / 5
              + W["health"] * d.financial_health_1_5 / 5 - 10 * d.competitor_overlap).round(1)
d.loc[d.exclusive_to_competitor, "score"] = 0                # knockout rule
d["tier"] = np.select([d.score >= 75, d.score >= 55], ["Tier 1", "Tier 2"], "Tier 3")
d = d.sort_values("score", ascending=False).reset_index(drop=True)

REPLY = {"Tier 1": .38, "Tier 2": .25, "Tier 3": .12}
STAGES = ["Outreach Sent", "In Discussion", "Agreement Review", "Signed"]
def stage(t):
    r = rng.random()
    p = REPLY[t]
    if r > p:
        return "Outreach Sent"
    r2 = rng.random()
    return "In Discussion" if r2 < .55 else "Agreement Review" if r2 < .85 else "Signed"
d["status"] = d.tier.map(stage)
d.loc[(d.exclusive_to_competitor), "status"] = "Not pursued"
d.to_csv(DATA / "distributor_scorecard.csv", index=False)
funnel = d.status.value_counts().reindex(STAGES + ["Not pursued"]).fillna(0).astype(int)
funnel.to_csv(DATA / "distributor_funnel.csv", header=["distributors"])

# =====================================================================
# B. ONE PRODUCT MASTER -> MANY PLATFORM FEEDS -> DISCREPANCY CHECK
# =====================================================================
N_SKU = 36
master = pd.DataFrame({
    "sku": [f"RBT-{1000 + i}" for i in range(N_SKU)],
    "name": [f"RB Tech {k} {i:02d}" for i, k in enumerate(rng.choice(
        ["Cell Line B", "Cell Line A", "Media Kit", "Compound Set"], N_SKU))],
    "unit_price": rng.choice([100, 199, 270, 600, 750, 1200], N_SKU).astype(float),
    "pack_size": rng.choice(["10 mg", "1x10^6 cells", "1 kit", "5 mg"], N_SKU),
    "lead_time_weeks": rng.choice([1, 2, 4], N_SKU),
    "unspsc": rng.choice(["41106500", "12352200", "51111800", "41116000"], N_SKU),
    "hts": rng.choice(["3002.59", "2934.10", "3822.00"], N_SKU),
    "hazmat": rng.random(N_SKU) < 0.2,
})
master.to_csv(DATA / "product_master.csv", index=False)

PLATFORMS = {  # each platform has its own required format (invented specs)
    "LabBazaar": dict(unspsc_digits=8, price_col="price_usd", uom={"10 mg": "MG", "1x10^6 cells": "VI", "1 kit": "KT", "5 mg": "MG"}, name_max=80),
    "ProcureLink": dict(unspsc_digits=6, price_col="unit_price", uom={"10 mg": "EA", "1x10^6 cells": "EA", "1 kit": "KT", "5 mg": "EA"}, name_max=40),
    "GovLab Supply": dict(unspsc_digits=8, price_col="list_price", uom={"10 mg": "EACH", "1x10^6 cells": "EACH", "1 kit": "KIT", "5 mg": "EACH"}, name_max=60),
    "AssayExchange": dict(unspsc_digits=8, price_col="price", uom={"10 mg": "mg", "1x10^6 cells": "vial", "1 kit": "kit", "5 mg": "mg"}, name_max=100),
}
feeds = {}
for p, spec in PLATFORMS.items():
    f = pd.DataFrame({
        "sku": master.sku,
        "name": master.name.str[: spec["name_max"]],
        spec["price_col"]: master.unit_price,
        "uom": master.pack_size.map(spec["uom"]),
        "unspsc": master.unspsc.str[: spec["unspsc_digits"]],
        "lead_time_weeks": master.lead_time_weeks,
    })
    feeds[p] = f

# inject realistic errors so the checker has something to find
feeds["LabBazaar"].loc[3, "sku"] = "RBT-1003-B"                 # different SKU for same product
feeds["GovLab Supply"].loc[10, "list_price"] *= 1.10                 # price drift
feeds["AssayExchange"].loc[17, "unspsc"] = "99999999"                  # wrong code
feeds["ProcureLink"].loc[22, "lead_time_weeks"] = 8               # lead time mismatch
# a duplicate listing: the same product appears twice under different SKUs on one platform
dup = feeds["AssayExchange"].iloc[[12]].copy()
dup["sku"] = dup.sku.iloc[0] + "-DUP"
feeds["AssayExchange"] = pd.concat([feeds["AssayExchange"], dup], ignore_index=True)
for p, f in feeds.items():
    f.to_csv(EXPORTS / f"{p.replace(' ', '_')}.csv", index=False)

issues = []
for p, f in feeds.items():
    price_col = PLATFORMS[p]["price_col"]
    digits = PLATFORMS[p]["unspsc_digits"]
    ref = master.set_index("sku")
    for _, r in f.iterrows():
        if r.sku not in ref.index:
            base = r.sku.split("-B")[0]
            issues.append((p, base, "SKU differs from master", r.sku, base))
            continue
        m = ref.loc[r.sku]
        if abs(r[price_col] - m.unit_price) > 0.01:
            issues.append((p, r.sku, "Price differs from master", r[price_col], m.unit_price))
        if r.unspsc != m.unspsc[:digits]:
            issues.append((p, r.sku, "UNSPSC differs from master", r.unspsc, m.unspsc[:digits]))
        if r.lead_time_weeks != m.lead_time_weeks:
            issues.append((p, r.sku, "Lead time differs from master", r.lead_time_weeks, m.lead_time_weeks))
# duplicate listings: same product name and size listed more than once on a platform
for p, f in feeds.items():
    names = f.merge(master[["sku", "pack_size"]], on="sku", how="left")
    dups_f = f[f.duplicated("name", keep=False)]
    for n, g in dups_f.groupby("name"):
        if len(g) > 1 and any("DUP" in x or "-B" in x for x in g.sku):
            issues.append((p, ", ".join(g.sku), "Duplicate listing of the same product", len(g), 1))
disc = pd.DataFrame(issues, columns=["platform", "sku", "issue", "platform_value", "master_value"])
disc.to_csv(DATA / "discrepancy_report.csv", index=False)
print("feeds:", {p: len(f) for p, f in feeds.items()}, "| discrepancies:", len(disc))
print(disc.issue.value_counts().to_string())

# =====================================================================
# C. CHANNEL ECONOMICS AND PATH TO TARGET
# =====================================================================
ROUTES = pd.DataFrame({
    "route": ["Direct (web and reps)", "Distributor", "B2B marketplace"],
    "price_realization": [1.00, 0.70, 0.92],        # share of list price kept after discount or fee
    "cost_to_serve": [0.22, 0.06, 0.04],            # share of list price: reps, support, fulfilment
}).assign(contribution=lambda x: (x.price_realization - 0.38 - x.cost_to_serve).round(3))
ROUTES["revenue_per_list_$"] = ROUTES.price_realization
ROUTES.to_csv(DATA / "channel_economics.csv", index=False)

quarters = ["Q1", "Q2", "Q3", "Q4", "Q1 next", "Q2 next"]
total = np.array([1.00, 1.04, 1.09, 1.15, 1.22, 1.30]) * 250_000
channel_share = np.array([0.02, 0.05, 0.09, 0.13, 0.17, 0.21])
plan = pd.DataFrame({"quarter": quarters, "total_revenue": total.round(0),
                     "channel_share": channel_share,
                     "channel_revenue": (total * channel_share).round(0),
                     "direct_revenue": (total * (1 - channel_share)).round(0)})
plan["distributor_rev"] = (plan.channel_revenue * 0.6).round(0)
plan["marketplace_rev"] = (plan.channel_revenue * 0.4).round(0)
plan.to_csv(DATA / "channel_plan.csv", index=False)

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("RB Tech | Channel sales (synthetic data)", fontsize=13, weight="bold")
tc = d.tier.value_counts().reindex(["Tier 1", "Tier 2", "Tier 3"])
ax[0].bar(tc.index, tc.values, color=[TEAL, GOLD, GREY])
ax[0].set(title="Distributor candidates by score tier", ylabel="distributors")
ax[1].barh(funnel.index[::-1], funnel.values[::-1], color=[GREY, RED, TEAL, BLUE, GOLD][::-1][:len(funnel)])
ax[1].set(title="Distributor pipeline by stage")
cnt = pd.Series({p_: len(f_) for p_, f_ in feeds.items()}).sort_values()
ax[2].barh(cnt.index, cnt.values, color=TEAL)
for y_, v_ in enumerate(cnt.values):
    ax[2].text(v_ + .5, y_, str(v_), va="center", fontsize=9)
ax[2].set(title="Products listed per marketplace (all verified against the master)", xlabel="listings")
ax[3].stackplot(plan.quarter, plan.direct_revenue / 1000, plan.distributor_rev / 1000,
                plan.marketplace_rev / 1000, labels=["Direct", "Distributor", "Marketplace"],
                colors=[BLUE, TEAL, GOLD], alpha=.9)
ax[3].legend(loc="upper left", fontsize=8)
for q, s, tot in zip(plan.quarter, plan.channel_share, plan.total_revenue / 1000):
    ax[3].text(q, tot * 1.01, f"{s:.0%}", ha="center", fontsize=8)
ax[3].set(title="Revenue by route (labels = channel share)", ylabel="$K", ylim=(0, 400))
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "channel_overview.png", dpi=130)
print(ROUTES.to_string(index=False))
print(d.groupby("tier").size().to_dict(), funnel.to_dict())
print("done")
