"""Shipping-charge optimization for RB Tech (fictional): four methods, one decision.

The question: what flat shipping charge covers real delivery cost without hurting competitiveness?
Methods (the same triangulation used in practice, rebuilt on invented numbers):
  1. Expert estimate            2. Historical average
  3. Monte Carlo simulation     4. Statistical (normal) model
Plus a charge-vs-margin curve and a sensitivity check.
All rates, costs and volumes are synthetic. Run: python scripts/shipping_simulation.py
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
DATA.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)
rng = np.random.default_rng(2025)

# ---------------- inputs (all invented) ----------------
PACKAGE = dict(weight_lb=25, dims_in="13x14x15", kits_per_box=3)
FIXED = dict(box=12.0, dry_ice=38.0, packing_hours=1.0, labor_rate=30.0)   # cost of goods per shipment
FIXED_COST = FIXED["box"] + FIXED["dry_ice"] + FIXED["packing_hours"] * FIXED["labor_rate"]
# synthetic courier rate card: base price by zone for the same package, plus a priority premium
ZONE_RATE = {2: 58, 3: 84, 4: 110, 5: 133, 6: 153, 7: 170, 8: 188}
PRIORITY_PREMIUM = 1.18
SERVICE_MIX = {"Standard Overnight": 0.90, "Priority Overnight": 0.10}
# probability of each zone (equal-probability assumption is the baseline, as a first-pass model)
ZONE_P_EQUAL = {z: 1 / len(ZONE_RATE) for z in ZONE_RATE}

def draw(n, zone_p, mix=SERVICE_MIX, seed=None):
    r = np.random.default_rng(seed if seed is not None else rng.integers(1e9))
    zones = r.choice(list(zone_p), n, p=list(zone_p.values()))
    svc = r.choice(list(mix), n, p=list(mix.values()))
    cost = np.array([ZONE_RATE[z] for z in zones], float) * np.where(svc == "Priority Overnight",
                                                                     PRIORITY_PREMIUM, 1.0)
    cost *= 1 + r.normal(0, 0.03, n)                       # small surcharge noise (fuel, residential)
    return pd.DataFrame({"service": svc, "zone": zones, "courier_cost": cost.round(2)})

# ---------------- method 1: expert estimate ----------------
EXPERT_COURIER = 125.0

# ---------------- method 2: historical data ----------------
hist = draw(180, ZONE_P_EQUAL, seed=1)      # a past batch of actual shipments
hist.to_csv(DATA / "historical_shipments.csv", index=False)
hist_avg = hist.courier_cost.mean()

# ---------------- method 3: Monte Carlo (1,000 iterations) ----------------
sim = draw(1000, ZONE_P_EQUAL, seed=2)
sim["total_cost"] = (sim.courier_cost + FIXED_COST).round(2)
sim.to_csv(DATA / "simulation_1000_runs.csv", index=False)
sim_avg_courier = sim.courier_cost.mean()
sim_avg_total = sim.total_cost.mean()

# ---------------- method 4: statistical model ----------------
stat_min, stat_max = sim.courier_cost.min(), sim.courier_cost.max()
stat_mean = sim.courier_cost.mean()
stat_sd = sim.courier_cost.std()

methods = pd.DataFrame([
    ("Expert estimate (courier only)", EXPERT_COURIER),
    ("Historical average (courier only)", hist_avg),
    ("Monte Carlo, 1,000 runs (courier only)", sim_avg_courier),
    ("Normal model mean (courier only)", stat_mean),
], columns=["method", "avg_courier_cost"]).round(2)
methods["plus_fixed_costs"] = (methods.avg_courier_cost + FIXED_COST).round(2)
methods.to_csv(DATA / "method_comparison.csv", index=False)

# ---------------- decision: flat charge vs margin ----------------
charges = np.arange(100, 361, 10)
rows = []
for c in charges:
    margin = c - sim.total_cost
    rows.append(dict(flat_charge=c, avg_margin=margin.mean().round(2),
                     pct_shipments_below_cost=(margin < 0).mean().round(3),
                     p10_margin=np.percentile(margin, 10).round(2)))
curve = pd.DataFrame(rows)
curve.to_csv(DATA / "charge_vs_margin.csv", index=False)
BREAK_EVEN = float(sim_avg_total)
CURRENT = 100
RECOMMENDED = int(round(BREAK_EVEN / 5) * 5)          # flat charge that breaks even on average
# alternative: tiered charge by zone group, which cuts the below-cost share at a similar average
TIER = {2: 165, 3: 165, 4: 215, 5: 215, 6: 255, 7: 255, 8: 255}
tier_margin = sim.zone.map(TIER) - sim.total_cost
tier_below = float((tier_margin < 0).mean())
tier_avg_charge = float(sim.zone.map(TIER).mean())
rec_row = curve[curve.flat_charge == RECOMMENDED].iloc[0]
cur_row = curve[curve.flat_charge == CURRENT].iloc[0]
print(methods.to_string(index=False))
print(f"fixed per-shipment cost {FIXED_COST:.2f} | break-even charge {BREAK_EVEN:.2f}")
print("current:", cur_row.to_dict())
print("recommended:", rec_row.to_dict())
print(f"tiered: avg charge {tier_avg_charge:.0f}, below cost {tier_below:.1%} vs flat {rec_row.pct_shipments_below_cost:.1%}")

# ---------------- sensitivity: what moves the answer ----------------
base = sim_avg_total
def mean_total(zone_p=ZONE_P_EQUAL, mix=SERVICE_MIX, fixed=FIXED_COST):
    return draw(4000, zone_p, mix, seed=3).courier_cost.mean() + fixed
heavy_far = {z: (3 if z >= 6 else 1) / 15 for z in ZONE_RATE}
heavy_far = {z: p / sum(heavy_far.values()) for z, p in heavy_far.items()}
near = {z: (3 if z <= 3 else 1) / 13 for z in ZONE_RATE}
near = {z: p / sum(near.values()) for z, p in near.items()}
sens = pd.DataFrame([
    ("Customers skew to far zones", mean_total(zone_p=heavy_far) - base),
    ("Customers skew to near zones", mean_total(zone_p=near) - base),
    ("Priority share 10% to 30%", mean_total(mix={"Standard Overnight": .7, "Priority Overnight": .3}) - base),
    ("Dry ice cost +25%", FIXED["dry_ice"] * 0.25),
    ("Packing time 1h to 1.5h", 0.5 * FIXED["labor_rate"]),
    ("Courier rates +5%", 0.05 * sim_avg_courier),
], columns=["scenario", "change_in_avg_cost"]).round(2)
sens.to_csv(DATA / "sensitivity.csv", index=False)
print(sens.to_string(index=False))

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("RB Tech | Shipping charge optimization (synthetic data)", fontsize=13, weight="bold")
ax[0].hist(sim.total_cost, bins=30, color=BLUE, alpha=.85)
ax[0].axvline(CURRENT, color=RED, ls="--", label=f"current ${CURRENT}")
ax[0].axvline(BREAK_EVEN, color=GOLD, ls="--", label=f"avg cost ${BREAK_EVEN:,.0f}")
ax[0].axvline(RECOMMENDED, color=TEAL, ls="--", label=f"proposed ${RECOMMENDED}")
ax[0].legend(fontsize=8)
ax[0].set(title="Simulated cost per shipment (1,000 runs)", xlabel="$ per shipment")
ax[1].barh(methods.method[::-1].str.replace(r" \(courier only\)", "", regex=True),
           methods.plus_fixed_costs[::-1], color=TEAL)
ax[1].axvline(CURRENT, color=RED, ls="--")
ax[1].set(title="Four methods agree (cost incl. fixed)", xlabel="$ per shipment")
for y, v in enumerate(methods.plus_fixed_costs[::-1]):
    ax[1].text(v + 2, y, f"${v:,.0f}", va="center")
ax[2].plot(curve.flat_charge, curve.pct_shipments_below_cost * 100, color=RED, marker="o", ms=3)
ax[2].set(title="Shipments sold below cost by flat charge", xlabel="flat charge ($)", ylabel="% of shipments")
ax[2].axvline(CURRENT, color=RED, ls=":")
ax[2].axvline(RECOMMENDED, color=TEAL, ls=":")
ax[2].axhline(tier_below * 100, color=GOLD, ls="--")
ax[2].text(105, tier_below * 100 + 2, f"zone-tiered charge: {tier_below:.0%} below cost", color=GOLD)
s = sens.sort_values("change_in_avg_cost")
ax[3].barh(s.scenario, s.change_in_avg_cost, color=np.where(s.change_in_avg_cost > 0, RED, TEAL))
ax[3].axvline(0, color="k", lw=.6)
ax[3].set(title="Sensitivity: change in avg cost ($)", xlabel="$ per shipment")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "shipping_overview.png", dpi=130)
print("done")
