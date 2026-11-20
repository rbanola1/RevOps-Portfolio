"""Partner onboarding and pricing governance for Aurelis Life Sciences (fictional).

Ten synthetic channel partners (regional distributors and marketplaces): onboarding cycle time by step,
partner scorecard, and a catalog audit that finds SKU, price, pack-size and lead-time mismatches for the same product
across partners. All data is invented. Run: python scripts/partner_program.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(1401)

PARTNERS = [("Northlab Distribution", "Distributor", "North America"), ("Eurobio Supply", "Distributor", "Europe"),
            ("Pacific Sciences", "Distributor", "Asia Pacific"), ("Alpine Reagents", "Distributor", "Europe"),
            ("LabBazaar", "Marketplace", "Global"), ("ProcureLink", "Marketplace", "North America"),
            ("GovLab Supply", "Government marketplace", "North America"), ("AssayExchange", "Marketplace", "Global"),
            ("Southern Cross Scientific", "Distributor", "Asia Pacific"), ("Iberia Life Sciences", "Distributor", "Europe")]
STEPS = {"Due diligence and fit": 7, "Agreement and legal review": 21, "Vendor registration and forms": 10,
         "Catalog and pricing sheet": 12, "Training and launch": 7}

# ---------- 1. onboarding cycle time ----------
rows = []
for name, kind, region in PARTNERS:
    mult = {"Marketplace": 1.15, "Government marketplace": 1.5}.get(kind, 1.0) * rng.uniform(.8, 1.3)
    d = {s: int(max(2, v * mult * rng.uniform(.7, 1.4))) for s, v in STEPS.items()}
    rows.append(dict(partner=name, type=kind, region=region, **d, total_days=sum(d.values())))
ob = pd.DataFrame(rows)
ob.to_csv(DATA / "onboarding_cycle_time.csv", index=False)

# ---------- 2. partner scorecard ----------
sc = pd.DataFrame({"partner": ob.partner, "type": ob.type})
sc["revenue_12m"] = (np.exp(rng.normal(11.3, .8, len(sc)))).round(-2)
sc["sell_through_pct"] = rng.uniform(35, 92, len(sc)).round(0)
sc["catalog_accuracy_pct"] = rng.uniform(78, 99, len(sc)).round(0)
sc["order_error_pct"] = rng.uniform(.5, 6.5, len(sc)).round(1)
sc["response_days"] = rng.uniform(1, 6, len(sc)).round(1)
z = lambda s: (s - s.min()) / (s.max() - s.min())
sc["score"] = (30 * z(sc.revenue_12m) + 25 * z(sc.sell_through_pct) + 20 * z(sc.catalog_accuracy_pct)
               + 15 * (1 - z(sc.order_error_pct)) + 10 * (1 - z(sc.response_days))).round(0)
sc["tier"] = pd.cut(sc.score, [-1, 39, 64, 100], labels=["Review", "Maintain", "Grow"])
sc = sc.sort_values("score", ascending=False)
sc.to_csv(DATA / "partner_scorecard.csv", index=False)

# ---------- 3. catalog audit: same product, different data across partners ----------
PRODUCTS = [("Endothelial cells, 1 vial", "EC-1001", 620, "1 vial", 5), ("Endothelial medium, 500 mL", "EM-2010", 185, "500 mL", 3),
            ("Progenitor cells, 1 vial", "PC-1100", 540, "1 vial", 5), ("Neural media kit", "NM-3000", 410, "1 kit", 7),
            ("Small molecule A, 10 mg", "SM-4101", 95, "10 mg", 4), ("Small molecule B, 50 mg", "SM-4102", 260, "50 mg", 4),
            ("Expansion medium, 100 mL", "XM-5200", 120, "100 mL", 3), ("Cryopreservation medium, 50 mL", "CM-6001", 78, "50 mL", 3)]
cat = []
for name, sku, price, pack, lead in PRODUCTS:
    for pn, kind, _ in PARTNERS:
        if rng.random() < .75:
            p, s, pk, lt = price, sku, pack, lead
            issue = ""
            r = rng.random()
            if r < .07:
                s, issue = sku[:-1] + str(int(rng.integers(0, 9))), "SKU differs from master"
            elif r < .16:
                p, issue = round(price * rng.choice([.9, 1.12, 1.25])), "Price differs from price list"
            elif r < .22:
                pk, issue = "2 x " + pack, "Pack size differs"
            elif r < .29:
                lt, issue = lead + int(rng.integers(3, 9)), "Lead time differs"
            cat.append(dict(product=name, partner=pn, master_sku=sku, partner_sku=s, master_price=price, partner_price=p,
                            master_pack=pack, partner_pack=pk, master_lead_days=lead, partner_lead_days=lt, issue=issue))
cat = pd.DataFrame(cat)
cat.to_csv(DATA / "catalog_audit.csv", index=False)
issues = cat[cat.issue != ""]
issues.to_csv(DATA / "catalog_discrepancies.csv", index=False)
by_type = issues.groupby("issue").size().sort_values()
by_partner = (cat.assign(bad=cat.issue != "").groupby("partner").bad.mean() * 100).round(0).sort_values()
print(ob[["partner", "total_days"]].to_string(index=False)); print(sc[["partner", "score", "tier"]].to_string(index=False))
print("listings", len(cat), "| discrepancies", len(issues), round(len(issues) / len(cat) * 100), "%"); print(by_type)

plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(2, 2, figsize=(15, 9.5))
fig.suptitle("Aurelis Life Sciences | Partner onboarding and pricing governance (synthetic data)", fontsize=13, weight="bold")
o = ob.sort_values("total_days")
left = np.zeros(len(o))
for s, c in zip(STEPS, plt.cm.Blues(np.linspace(.35, .95, len(STEPS)))):
    ax[0, 0].barh(o.partner, o[s], left=left, color=c, label=s)
    left += o[s].values
ax[0, 0].legend(fontsize=7, loc="lower right")
ax[0, 0].set(title="Onboarding days by step", xlabel="days")
tc = {"Grow": TEAL, "Maintain": GOLD, "Review": RED}
s2 = sc.sort_values("score")
ax[0, 1].barh(s2.partner, s2.score, color=[tc[t] for t in s2.tier])
ax[0, 1].set(title="Partner scorecard (0 to 100; green grow, gold maintain, red review)", xlabel="score")
ax[1, 0].barh(by_type.index, by_type.values, color=RED)
ax[1, 0].set(title=f"Catalog discrepancies found ({len(issues)} of {len(cat)} listings)", xlabel="listings")
ax[1, 1].barh(by_partner.index, by_partner.values, color=[RED if v > 40 else GOLD if v > 25 else TEAL for v in by_partner.values])
ax[1, 1].set(title="Share of listings with a discrepancy, by partner", xlabel="%")
fig.tight_layout(rect=[0, 0, 1, .95])
fig.savefig(CHARTS / "partner_program_dashboard.png", dpi=125)
print("done")
