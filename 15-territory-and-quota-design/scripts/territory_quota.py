"""Territory design and quota setting for RB Tech (fictional).

3,200 synthetic target accounts around US research hubs. Compares three ways to split accounts between four reps
(by state group, by equal account count, by balanced market potential), then sets quotas top-down and bottom-up,
tests them against rep capacity, and simulates attainment. All data is invented.
Run: python scripts/territory_quota.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(1501)

# research hubs: name, lat, lon, weight, average account potential multiplier
HUBS = [("Boston", 42.36, -71.06, 1.9, 1.5), ("New York", 40.71, -74.0, 1.2, 1.1), ("Philadelphia", 39.95, -75.17, .9, 1.0),
        ("Baltimore-DC", 39.0, -77.0, 1.0, 1.1), ("Research Triangle", 35.9, -78.9, .8, 1.0), ("Atlanta", 33.75, -84.39, .6, .8),
        ("Cleveland", 41.5, -81.69, .5, .8), ("Chicago", 41.88, -87.63, 1.0, .9), ("Ann Arbor", 42.28, -83.74, .6, .9),
        ("Minneapolis", 44.98, -93.27, .5, .8), ("Houston", 29.76, -95.37, .6, .9), ("Denver", 39.74, -104.99, .5, .8),
        ("Seattle", 47.6, -122.33, .8, 1.1), ("Bay Area", 37.5, -122.2, 1.8, 1.7), ("San Diego", 32.72, -117.16, 1.3, 1.3),
        ("Los Angeles", 34.05, -118.24, .8, 1.0)]
w = np.array([h[3] for h in HUBS]); w = w / w.sum()
N = 3200
hub_idx = rng.choice(len(HUBS), N, p=w)
lat = np.array([HUBS[i][1] for i in hub_idx]) + rng.normal(0, .55, N)
lon = np.array([HUBS[i][2] for i in hub_idx]) + rng.normal(0, .7, N)
segment = rng.choice(["Academia", "Biotech", "Pharma", "CRO", "CGT developer", "Core facility"], N, p=[.38, .22, .1, .1, .12, .08])
seg_pot = {"Academia": 1, "Biotech": 1.6, "Pharma": 3.2, "CRO": 1.8, "CGT developer": 2.2, "Core facility": .9}
potential = np.round(np.array([HUBS[i][4] for i in hub_idx]) * np.array([seg_pot[s] for s in segment]) * rng.lognormal(7.6, .5, N), -2)
acc = pd.DataFrame(dict(account_id=[f"A-{3000 + i}" for i in range(N)], hub=[HUBS[i][0] for i in hub_idx], lat=lat.round(3), lon=lon.round(3),
                        segment=segment, potential=potential))
acc["current_customer"] = rng.random(N) < .22
acc.to_csv(DATA / "accounts.csv", index=False)
REPS = ["Rep 1", "Rep 2", "Rep 3", "Rep 4"]

# ---------- three ways to split ----------
def by_geography(a):
    """Vertical bands by longitude: simple, but ignores potential."""
    q = np.quantile(a.lon, [.25, .5, .75])
    return np.digitize(a.lon, q)

def by_account_count(a):
    """Sort west to east and cut into four groups of equal account count."""
    order = a.lon.rank(method="first")
    return np.minimum((order / len(a) * 4).astype(int), 3)

def by_balanced_potential(a):
    """Greedy: place hubs (kept whole, so a rep owns whole metro areas) on the rep with the least potential so far."""
    # hubs are ordered west to east (contiguous territories) and cut where cumulative potential crosses each quarter;
    # a large hub with more than one quarter of potential is split by account so no rep is over-loaded
    hub_lon = a.groupby("hub").lon.mean().sort_values()
    total = a.potential.sum()
    own = pd.Series(0, index=a.index, dtype=int)
    cum = 0.0
    for h in hub_lon.index:
        idx = a.index[a.hub == h]
        pots = a.loc[idx].sort_values("lon").potential
        for i, p in pots.items():
            own[i] = min(3, int((cum + p / 2) / total * 4))
            cum += p
    return own.values

methods = {"Equal longitude bands": by_geography(acc), "Equal account count": by_account_count(acc), "Balanced potential": by_balanced_potential(acc)}
rows = []
for name, assign in methods.items():
    g = pd.DataFrame({"rep": assign, "potential": acc.potential, "customer": acc.current_customer}).groupby("rep").agg(
        accounts=("potential", "size"), potential=("potential", "sum"), customers=("customer", "sum"))
    rows.append(dict(method=name, accounts_min=int(g.accounts.min()), accounts_max=int(g.accounts.max()),
                     potential_min_k=round(g.potential.min() / 1e3), potential_max_k=round(g.potential.max() / 1e3),
                     potential_spread_pct=round((g.potential.max() - g.potential.min()) / g.potential.mean() * 100)))
cmp_ = pd.DataFrame(rows)
cmp_.to_csv(DATA / "territory_methods_compared.csv", index=False)
acc["rep"] = [REPS[i] for i in methods["Balanced potential"]]
terr = acc.groupby("rep").agg(accounts=("account_id", "count"), customers=("current_customer", "sum"), potential=("potential", "sum")).round(0)
terr["hubs"] = acc.groupby("rep").hub.agg(lambda s: ", ".join(sorted(s.unique())))
terr.to_csv(DATA / "territory_assignment.csv")
acc.to_csv(DATA / "accounts.csv", index=False)

# ---------- quota: top-down vs bottom-up ----------
COMPANY_TARGET = 3_800_000     # synthetic new plus expansion revenue target for the territories
share = terr.potential / terr.potential.sum()
top_down = (COMPANY_TARGET * share).round(-3)
# bottom-up: each rep's expected = customers x expansion value + open pipeline x win rate + new accounts x capacity-limited conversion
cust_rev = acc[acc.current_customer].groupby("rep").potential.sum() * .28
pipe = pd.Series(rng.uniform(.55, .85, 4), index=REPS) * share * COMPANY_TARGET * 1.9 * .29      # pipeline x win rate (29%)
new_cap = pd.Series(rng.uniform(.9, 1.1, 4), index=REPS) * 300_000                                  # capacity for new-account wins
bottom_up = (cust_rev + pipe + new_cap).round(-3)
q = pd.DataFrame({"top_down_quota": top_down, "bottom_up_estimate": bottom_up})
q["gap"] = q.bottom_up_estimate - q.top_down_quota
q["recommended_quota"] = (0.6 * q.top_down_quota + 0.4 * q.bottom_up_estimate).round(-3)
q.loc["Total"] = q.sum()
q.round(0).to_csv(DATA / "quota_setting.csv")

# ---------- attainment simulation: what share of reps hit 100% under each quota rule ----------
sims = 4000
actual_mean = q.bottom_up_estimate.iloc[:4].values * 1.10      # bottom-up estimates are cautious; actual results run about 10% higher
outcomes = {}
for label, quota in {"Top-down only": q.top_down_quota.iloc[:4].values, "Recommended blend": q.recommended_quota.iloc[:4].values,
                     "Bottom-up only": q.bottom_up_estimate.iloc[:4].values}.items():
    att = rng.normal(actual_mean, actual_mean * .22, size=(sims, 4)) / quota
    outcomes[label] = att
att_tbl = pd.DataFrame({k: dict(median_attainment=np.median(v), share_of_reps_at_100pct=(v >= 1).mean(), share_below_70pct=(v < .7).mean())
                        for k, v in outcomes.items()}).T.round(2)
att_tbl.to_csv(DATA / "attainment_simulation.csv")
print(cmp_.to_string(index=False)); print(terr[["accounts", "customers", "potential"]]); print(q.round(0)); print(att_tbl)

# ---------- international leads: route by country group, not by rep geography ----------
INTL = {"Canada": (110, "Rep 1 or Rep 4 by province group", 1.0), "United Kingdom and Ireland": (90, "Distributor", 1.0), "Germany, France, Benelux": (140, "Distributor", 1.1),
        "Nordics and Switzerland": (60, "Distributor", 1.3), "Japan and Korea": (80, "Distributor", 1.2), "China, Singapore, Australia": (90, "Distributor", .9),
        "Rest of world": (50, "Inside sales queue, quote only", .5)}
irows = []
for c, (n, route, mult) in INTL.items():
    pot = np.round(rng.lognormal(7.5, .5, n) * mult, -2)
    big = pot > 5000
    for i in range(n):
        irows.append(dict(country_group=c, potential=pot[i], default_route=route,
                          final_route=("Direct rep, with distributor informed" if big[i] and route == "Distributor" else route)))
intl = pd.DataFrame(irows)
intl.to_csv(DATA / "international_routing.csv", index=False)
intl_sum = intl.groupby(["country_group", "final_route"]).agg(accounts=("potential", "size"), potential=("potential", "sum")).reset_index()
intl_sum.to_csv(DATA / "international_routing_summary.csv", index=False)
print(intl_sum.to_string(index=False))

# ---------- compensation plan: design and cost ----------
OTE, VAR_SHARE = 150_000, .40                           # on-target earnings; 60/40 base to variable
base, variable = OTE * (1 - VAR_SHARE), OTE * VAR_SHARE
quota_ref = q.recommended_quota.iloc[:4].mean()
rate = variable / quota_ref                                # commission rate at 100% attainment
def payout(att, accelerator=True):
    att = np.asarray(att, dtype=float)
    tier1 = np.clip(att, 0, .5) * .5                      # first 50% of quota paid at half rate
    tier2 = np.clip(att - .5, 0, .5) * 1.0                # 50% to 100% at full rate
    tier3 = np.clip(att - 1, 0, .5) * (1.5 if accelerator else 1.0)   # 100% to 150% at 1.5x
    tier4 = np.clip(att - 1.5, 0, None) * (2.0 if accelerator else 1.0)
    return (tier1 + tier2 + tier3 + tier4) * quota_ref * rate
curve = pd.DataFrame({"attainment": np.arange(0, 2.01, .1)})
curve["variable_pay"] = payout(curve.attainment).round(0)
curve["total_pay"] = (curve.variable_pay + base).round(0)
curve["pay_flat_rate"] = (payout(curve.attainment, False) + base).round(0)
curve.to_csv(DATA / "comp_payout_curve.csv", index=False)
att_sim = outcomes["Recommended blend"]
rev_sim = att_sim * q.recommended_quota.iloc[:4].values
pay_sim = payout(att_sim) + base
cost_ratio = pay_sim.sum(axis=1).mean() / rev_sim.sum(axis=1).mean()
plan = pd.DataFrame({"item": ["On-target earnings per rep", "Base salary (60%)", "Target variable (40%)", "Commission rate at 100% of quota",
                              "Accelerator above 100% attainment", "Rate below 50% of quota", "Average cost of sales (pay / revenue), simulated",
                              "Share of reps paid above target", "Share of reps paid under 70% of target variable"],
                     "value": [OTE, base, variable, f"{rate:.1%}", "1.5x to 150%, 2x beyond", "0.5x", f"{cost_ratio:.1%}",
                               f"{(att_sim >= 1).mean():.0%}", f"{((payout(att_sim) / variable) < .7).mean():.0%}"]})
plan.to_csv(DATA / "comp_plan_summary.csv", index=False)
print(plan.to_string(index=False))

plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
RC = [BLUE, TEAL, GOLD, RED]
fig, ax = plt.subplots(2, 3, figsize=(18, 9.2))
fig.suptitle("RB Tech | Territory design and quota setting (synthetic data)", fontsize=13, weight="bold")
for r, c in zip(REPS, RC):
    s = acc[acc.rep == r]
    ax[0, 0].scatter(s.lon, s.lat, s=np.sqrt(s.potential) / 14, color=c, alpha=.45, label=r)
ax[0, 0].set(title="Balanced-potential territories (bubble = account potential)", xlabel="longitude", ylabel="latitude")
ax[0, 0].legend(fontsize=7, markerscale=1.5)
x = np.arange(3); wdt = .2
for i, r in enumerate(range(4)):
    pots = []
    for assign in methods.values():
        pots.append(acc.potential.groupby(assign).sum().iloc[r] / 1e6)
    ax[0, 1].bar(x + (i - 1.5) * wdt, pots, wdt, color=RC[i], label=REPS[i])
ax[0, 1].set_xticks(x, ["Longitude\nbands", "Equal account\ncount", "Balanced\npotential"])
ax[0, 1].legend(fontsize=7)
ax[0, 1].set(title="Account potential per rep by method ($M)", ylabel="$M")
ax[0, 2].bar(cmp_.method.str.replace(" ", "\n", n=1), cmp_.potential_spread_pct, color=[RED, GOLD, TEAL])
for i, v in enumerate(cmp_.potential_spread_pct):
    ax[0, 2].text(i, v + 1, f"{v}%", ha="center", weight="bold")
ax[0, 2].set(title="Gap between richest and poorest territory (% of average)", ylabel="%")
qq = q.iloc[:4]
xx = np.arange(4)
ax[1, 0].bar(xx - .27, qq.top_down_quota / 1e3, .27, color=GREY, label="Top-down")
ax[1, 0].bar(xx, qq.bottom_up_estimate / 1e3, .27, color=BLUE, label="Bottom-up")
ax[1, 0].bar(xx + .27, qq.recommended_quota / 1e3, .27, color=TEAL, label="Recommended")
ax[1, 0].set_xticks(xx, REPS)
ax[1, 0].legend(fontsize=7)
ax[1, 0].set(title="Quota by rep: three views ($K)", ylabel="$K")
for (k, v), c in zip(outcomes.items(), [RED, TEAL, GOLD]):
    ax[1, 1].hist(v.ravel(), bins=40, alpha=.55, color=c, label=k, range=(.3, 1.8))
ax[1, 1].axvline(1, color="k", lw=.8)
ax[1, 1].legend(fontsize=7)
ax[1, 1].set(title="Simulated quota attainment (1.0 = 100%)", xlabel="attainment")
ax[1, 2].barh(att_tbl.index, att_tbl.share_of_reps_at_100pct * 100, color=[RED, TEAL, GOLD])
for i, v in enumerate(att_tbl.share_of_reps_at_100pct * 100):
    ax[1, 2].text(v + 1, i, f"{v:.0f}%", va="center", weight="bold")
ax[1, 2].set(title="Reps hitting 100% of quota (simulated)", xlabel="% of rep-years")
ax[1, 2].set_xlim(0, 100)
fig.tight_layout(rect=[0, 0, 1, .95])
fig.savefig(CHARTS / "territory_quota_dashboard.png", dpi=125)
fig2, a2 = plt.subplots(1, 2, figsize=(14, 5.2))
fig2.suptitle("International routing and compensation plan design (synthetic data)", fontsize=12, weight="bold")
piv = intl_sum.pivot_table(index="country_group", columns="final_route", values="accounts", aggfunc="sum", fill_value=0)
piv.plot(kind="barh", stacked=True, ax=a2[0], color=plt.cm.Blues(np.linspace(.35, .9, piv.shape[1])))
a2[0].set(title="International accounts by country group and route", xlabel="accounts", ylabel="")
a2[0].legend(fontsize=7, loc="lower right")
a2[1].plot(curve.attainment * 100, curve.total_pay / 1e3, color=TEAL, lw=2.2, label="Tiered plan with accelerator")
a2[1].plot(curve.attainment * 100, curve.pay_flat_rate / 1e3, color=GREY, lw=1.6, ls="--", label="Flat commission rate")
a2[1].axvline(100, color="k", lw=.6)
a2[1].axhline(OTE / 1e3, color=GOLD, lw=.8)
a2[1].text(2, OTE / 1e3 + 3, "on-target earnings", color=GOLD)
a2[1].set(title="Rep pay by quota attainment ($K): 60% base, 40% variable", xlabel="% of quota", ylabel="$K total pay")
a2[1].legend(fontsize=8)
fig2.tight_layout(rect=[0, 0, 1, .92])
fig2.savefig(CHARTS / "intl_and_comp_plan.png", dpi=125)
print("done")
