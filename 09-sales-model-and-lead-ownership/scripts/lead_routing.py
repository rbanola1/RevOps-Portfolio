"""Synthetic inside/outside sales model: lead routing, ownership rules and conflict detection.

Fictional company RB Tech. Reps, accounts and leads are invented.
Compares an unstructured process (anyone grabs a lead) with a rules-based process
(route by criteria + "research first" ownership check + mandatory associations).
Run: python scripts/lead_routing.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(5)

REPS = {"Inside A": "Inside", "Inside B": "Inside", "Outside A": "Outside", "Outside B": "Outside",
        "BD A": "BD"}
N_ACC, N_LEADS = 700, 3000

# ---------------- accounts with parent/child structure ----------------
acc = pd.DataFrame({"account_id": [f"A{i:04d}" for i in range(N_ACC)],
                    "segment": rng.choice(["Academic", "Small biotech", "Service lab", "Mid-size pharma",
                                           "Big pharma"], N_ACC, p=[.45, .2, .1, .15, .1])})
acc["parent_id"] = np.where(rng.random(N_ACC) < .12, rng.choice(acc.account_id, N_ACC), "")
acc.loc[acc.parent_id == acc.account_id, "parent_id"] = ""
acc["owner"] = np.where(acc.segment.isin(["Academic", "Small biotech", "Service lab"]),
                        rng.choice(["Inside A", "Inside B"], N_ACC),
                        np.where(acc.segment == "Mid-size pharma", rng.choice(["Outside A", "Outside B"], N_ACC),
                                 rng.choice(["BD A", "Outside A"], N_ACC)))

# ---------------- inbound leads ----------------
leads = pd.DataFrame({
    "lead_id": [f"L{i:05d}" for i in range(N_LEADS)],
    "account_id": rng.choice(acc.account_id, N_LEADS),
    "created": pd.Timestamp("2026-01-05") + pd.to_timedelta(rng.integers(0, 300, N_LEADS), unit="D"),
    "source": rng.choice(["Web form", "Phone", "General email", "Trade show", "Event", "Referral"],
                         N_LEADS, p=[.34, .08, .18, .20, .10, .10]),
    "product_category": rng.choice(["RUO product", "Therapeutics", "Custom service", "Strategic RUO"],
                                   N_LEADS, p=[.62, .08, .12, .18]),
    "deal_kits": rng.choice([1, 2, 5, 10, 20, 40], N_LEADS, p=[.3, .25, .2, .12, .08, .05]),
    "region": rng.choice(["Domestic", "International"], N_LEADS, p=[.8, .2]),
})
leads = leads.merge(acc[["account_id", "segment", "owner"]].rename(columns={"owner": "account_owner"}),
                    on="account_id")

# ---------------- rules-based routing (criteria table) ----------------
def route(r):
    if r.product_category in ("Therapeutics", "Custom service"):
        return "BD A"
    if r.source in ("Trade show", "Event", "Referral") or r.deal_kits > 20 or r.segment in ("Mid-size pharma", "Big pharma"):
        return "Outside A" if r.name % 2 == 0 else "Outside B"
    return "Inside A" if r.name % 2 == 0 else "Inside B"

leads["lane_rule"] = leads.apply(route, axis=1)
leads["lane_type"] = leads.lane_rule.map(REPS)

# research-first: if the account already has an owner, that owner handles it
leads["assigned_rules"] = leads.account_owner                       # owner check wins
new_account_mask = rng.random(N_LEADS) < 0.12                        # account had no owner yet
leads.loc[new_account_mask, "assigned_rules"] = leads.loc[new_account_mask, "lane_rule"]

# unstructured baseline: whoever replies first, regardless of owner
leads["assigned_baseline"] = rng.choice(list(REPS), N_LEADS, p=[.3, .3, .15, .15, .1])

def conflicts(col):
    """accounts touched by more than one rep within a 30-day window"""
    d = leads.sort_values("created")
    out = 0
    for _, g in d.groupby("account_id"):
        if len(g) < 2:
            continue
        t = g.created.values
        r = g[col].values
        hit = False
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                if (t[j] - t[i]) / np.timedelta64(1, "D") <= 30 and r[i] != r[j]:
                    hit = True
                    break
            if hit:
                break
        out += hit
    return out
base_conf, rule_conf = conflicts("assigned_baseline"), conflicts("assigned_rules")
multi_acc = int((leads.account_id.value_counts() > 1).sum())

# ---------------- response time and SLA by lane ----------------
SLA_H = {"Inside": 24, "Outside": 72, "BD": 72}
leads["lane_final"] = leads.assigned_rules.map(REPS)
def resp(lane, rule):
    mean = {"Inside": 9, "Outside": 40, "BD": 44}[lane]
    return rng.gamma(2.0, mean / 2.0) if rule else rng.gamma(2.0, mean * 1.6 / 2.0)
leads["response_hours_rules"] = [resp(l, True) for l in leads.lane_final]
leads["response_hours_baseline"] = [resp(REPS[a], False) for a in leads.assigned_baseline]
leads["sla_hours"] = leads.lane_final.map(SLA_H)
sla_rules = float((leads.response_hours_rules <= leads.sla_hours).mean())
sla_base = float((leads.response_hours_baseline <= leads.assigned_baseline.map(REPS).map(SLA_H)).mean())

# ---------------- data completeness: owners and associations ----------------
n = N_LEADS
comp = pd.DataFrame({
    "metric": ["Deals associated to company AND contact", "Contact, deal and company owner all set",
               "Duplicate company records per 1,000"],
    "before": [0.62, 0.55, 38], "after": [0.97, 0.96, 6]})
# simulate the after from enforcement: mandatory fields + duplicate check at creation
sim_assoc = rng.random(n) < .97
comp.loc[0, "after"] = round(float(sim_assoc.mean()), 3)
comp.to_csv(DATA / "data_completeness.csv", index=False)

# ---------------- outputs ----------------
leads.drop(columns=["response_hours_baseline"]).to_csv(DATA / "leads_routed.csv", index=False)
acc.to_csv(DATA / "accounts.csv", index=False)
summary = pd.Series({
    "leads": N_LEADS, "accounts": N_ACC, "accounts_with_multiple_leads": multi_acc,
    "accounts_with_rep_conflict_baseline": base_conf, "accounts_with_rep_conflict_rules": rule_conf,
    "sla_met_baseline": round(sla_base, 3), "sla_met_rules": round(sla_rules, 3),
})
summary.to_csv(DATA / "kpi_summary.csv", header=["value"])
print(summary.to_string())
print(leads.groupby("lane_final").size().to_string())

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("RB Tech | Inside / outside sales model (synthetic data)", fontsize=13, weight="bold")
lane = leads.lane_final.value_counts().reindex(["Inside", "Outside", "BD"])
ax[0].bar(lane.index, lane.values, color=[TEAL, BLUE, GOLD])
ax[0].set(title="Leads by lane after routing rules", ylabel="leads")
ax[1].bar(["No rules", "Rules + research first"], [base_conf, rule_conf], color=[RED, TEAL])
ax[1].set(title="Accounts with 2+ reps in 30 days", ylabel="accounts")
for i, v in enumerate([base_conf, rule_conf]):
    ax[1].text(i, v + 1, str(v), ha="center")
ax[2].bar(["No rules", "Rules"], [sla_base * 100, sla_rules * 100], color=[RED, TEAL])
ax[2].set(title="Responses within lane SLA (%)", ylim=(0, 100))
for i, v in enumerate([sla_base * 100, sla_rules * 100]):
    ax[2].text(i, v + 1.5, f"{v:.0f}%", ha="center")
x = np.arange(2)
ax[3].bar(x - .2, comp.before[:2] * 100, .4, color=GREY, label="Before")
ax[3].bar(x + .2, comp.after[:2] * 100, .4, color=TEAL, label="After")
ax[3].set_xticks(x, ["Deal linked to\ncompany + contact", "All three\nowners set"])
ax[3].legend(fontsize=8)
ax[3].set(title="Ownership data completeness (%)", ylim=(0, 105))
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "sales_model_overview.png", dpi=130)
print("done")
