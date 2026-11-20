"""CRM migration, backup and data-governance model for RB Tech (fictional).

Simulates a move from a legacy CRM to a new one: record reconciliation by object, field-mapping quality,
duplicate resolution, a data-quality score before and after, and a backup / restore-test schedule.
All data is invented. Run: python scripts/migration_and_governance.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(1301)

# ---------- 1. record reconciliation by object ----------
OBJ = {"Companies": 9200, "Contacts": 41800, "Deals": 6100, "Activities (emails, calls, notes)": 188000, "Products": 420, "Quotes": 5300}
rec = []
for o, n in OBJ.items():
    dup = int(n * rng.uniform(.04, .13)) if o in ("Companies", "Contacts") else 0
    junk = int(n * rng.uniform(.01, .05)) if o != "Products" else 0
    migrated = n - dup - junk
    missing = int(migrated * rng.uniform(.0, .004))           # lost in load, found by reconciliation, reloaded
    rec.append(dict(object=o, source_records=n, duplicates_merged=dup, junk_removed=junk, loaded=migrated - missing,
                    missing_found=missing, reloaded=missing, final_in_target=migrated, reconciled=True))
rec = pd.DataFrame(rec)
rec["match_rate"] = (rec.final_in_target / (rec.source_records - rec.duplicates_merged - rec.junk_removed)).round(4)
rec.to_csv(DATA / "reconciliation_by_object.csv", index=False)

# ---------- 2. field mapping: quality by field before and after ----------
FIELDS = ["Company name", "Domain", "Country", "State or region", "Industry or segment", "Contact email", "Job title",
          "Lead source", "Deal amount", "Close date", "Owner", "Product interest"]
before = rng.uniform(.52, .93, len(FIELDS)).round(2)
after = np.minimum(.99, before + rng.uniform(.06, .38, len(FIELDS))).round(2)
fm = pd.DataFrame({"field": FIELDS, "fill_rate_legacy": before, "fill_rate_after_cleanup": after,
                   "rule": ["Standard casing, no legal suffix duplicates", "Required; used as match key", "ISO country list", "Picklist by country",
                            "Ten-value segment picklist", "Valid format; verified", "Standard role list", "Required at creation",
                            "Required past quote stage", "Required past quote stage", "Required; no unowned records", "Picklist of six areas"]})
fm.to_csv(DATA / "field_quality_before_after.csv", index=False)

# ---------- 3. data-quality score ----------
DIM = {"Completeness": (.68, .94), "Uniqueness (no duplicates)": (.81, .98), "Validity (format and picklists)": (.72, .96),
       "Ownership (record has an owner)": (.77, .99), "Freshness (touched in 12 months)": (.46, .71)}
dq = pd.DataFrame({"dimension": list(DIM), "before": [v[0] for v in DIM.values()], "after": [v[1] for v in DIM.values()]})
dq.loc[len(dq)] = ["Overall", dq.before.mean().round(2), dq.after.mean().round(2)]
dq.to_csv(DATA / "data_quality_score.csv", index=False)

# ---------- 4. backup and restore-test schedule ----------
bk = pd.DataFrame([
    ["CRM objects (companies, contacts, deals, tickets)", "Weekly full export plus daily change export", "Cloud storage with versioning", "90 days daily, 3 years monthly", "Quarterly restore test"],
    ["Activity history (emails, calls, notes)", "Monthly export", "Cloud storage", "3 years", "Annual sample check"],
    ["Property definitions and workflows", "On every change; monthly full copy", "Version-controlled documentation", "Indefinitely", "Compared at each release"],
    ["Reports and dashboards (BI model)", "On every release", "Version-controlled file store", "Last 10 versions", "Opened and refreshed quarterly"],
    ["Integration settings and mappings", "On every change", "Documentation repository", "Indefinitely", "Reviewed each quarter"]],
    columns=["asset", "backup method and frequency", "location", "retention", "restore test"])
bk.to_csv(DATA / "backup_schedule.csv", index=False)

print(rec.to_string(index=False)); print(dq.to_string(index=False))

plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(2, 2, figsize=(15, 9.5))
fig.suptitle("RB Tech | CRM migration and data governance (synthetic data)", fontsize=13, weight="bold")
r = rec[rec.object != "Activities (emails, calls, notes)"]
x = np.arange(len(r))
ax[0, 0].bar(x, r.source_records, color=GREY, label="Source records")
ax[0, 0].bar(x, r.final_in_target, color=BLUE, label="Loaded in new CRM")
ax[0, 0].set_xticks(x, [o[:12] for o in r.object])
ax[0, 0].legend()
ax[0, 0].set(title="Record reconciliation by object (activities not shown: 188K)", ylabel="records")
d = dq.iloc[:-1]
y = np.arange(len(d))
ax[0, 1].barh(y + .2, d.before * 100, .4, color=RED, label="Before")
ax[0, 1].barh(y - .2, d.after * 100, .4, color=TEAL, label="After")
ax[0, 1].set_yticks(y, d.dimension)
ax[0, 1].legend()
ax[0, 1].set(title=f"Data-quality score by dimension (overall {dq.before.iloc[-1]:.0%} to {dq.after.iloc[-1]:.0%})", xlabel="%")
f = fm.sort_values("fill_rate_after_cleanup")
yy = np.arange(len(f))
ax[1, 0].barh(yy + .2, f.fill_rate_legacy * 100, .4, color=RED, label="Legacy")
ax[1, 0].barh(yy - .2, f.fill_rate_after_cleanup * 100, .4, color=TEAL, label="After cleanup")
ax[1, 0].set_yticks(yy, f.field)
ax[1, 0].legend()
ax[1, 0].set(title="Field fill rate before and after", xlabel="% of records filled")
ax[1, 1].axis("off")
steps = ["1  Inventory objects, fields, integrations", "2  Define keys, picklists, owners", "3  Clean and dedupe in staging", "4  Trial load and reconcile counts",
         "5  Freeze legacy; final load", "6  Reconcile again; sample-check 200 records", "7  Cut over; keep legacy read-only 90 days",
         "8  Quarterly restore test and monthly quality check"]
ax[1, 1].set_title("Migration and governance runbook")
for i, s in enumerate(steps):
    ax[1, 1].text(0, .95 - i * .12, s, fontsize=10, va="top")
fig.tight_layout(rect=[0, 0, 1, .95])
fig.savefig(CHARTS / "migration_dashboard.png", dpi=125)
print("done")
