"""Synthetic CRM cleanup, industry segmentation and lead scoring for RB Tech (fictional).

All contacts, counts and rules-of-thumb outputs are invented. The method is what matters:
  1. audit the marketing-contact tier, 2. demote low-value contacts, 3. promote engaged ones,
  4. fill a clean Segment field from messy Industry values, 5. score engagement with decay.
Run:  python scripts/crm_cleanup.py      (writes data/*.csv and charts/*.png)
Needs: pandas, numpy, matplotlib
"""
import re
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
rng = np.random.default_rng(11)
N, TIER_LIMIT = 60000, 50000
TODAY = pd.Timestamp("2026-11-01")

# ---------------- 1. build a messy CRM ----------------
RAW_INDUSTRY = {  # messy picklist values -> clean segment (the mapping table)
    "Biotechnology": "Biotech", "Biotech Research": "Biotech", "Pharmaceuticals": "Pharma",
    "Pharma / Drug Dev": "Pharma", "Higher Education": "Academia", "University": "Academia",
    "Research": "Academia", "Hospitals & Health Care": "Hospital", "Medical Center": "Hospital",
    "Government Administration": "Government", "Non-profit": "Nonprofit Foundation",
    "Contract Research": "CRO", "Life Sciences": "Biotech", "Medical Devices": "Biotech",
    "Cell Therapy": "CGT Developer", "Gene Therapy": "CGT Developer", "Distribution": "Distributor",
    "Core Facility": "Core",
}
TITLE_RULES = [  # fallback rules to fill blanks from job title or company name
    (r"professor|postdoc|graduate|phd student|lab manager|pi\b", "Academia"),
    (r"cell therapy|car-t|gene therapy|cgt", "CGT Developer"),
    (r"cro\b|contract research|preclinical services", "CRO"),
    (r"director.*(r&d|research)|vp.*(r&d|research)|scientist", "Biotech"),
    (r"clinical|physician|hospital", "Hospital"),
    (r"procurement|purchasing", "Biotech"),
]
TITLES = ["Postdoctoral Fellow", "Professor", "Research Scientist", "Graduate Student", "Lab Manager",
          "Director of R&D", "VP Research", "Procurement Specialist", "Clinical Researcher",
          "CGT Process Scientist", "CRO Project Lead", "Core Facility Manager", "Marketing Manager",
          "Consultant", "Unknown"]
REGIONS = {"US": .60, "EU/UK/CH": .22, "Canada": .06, "Asia": .09, "Other": .03}

df = pd.DataFrame({
    "contact_id": [f"C{300000 + i}" for i in range(N)],
    "email": [f"user{rng.integers(0, int(N * .93))}@example{rng.integers(1, 400)}.org" for _ in range(N)],
    "job_title": rng.choice(TITLES, N),
    "region": rng.choice(list(REGIONS), N, p=list(REGIONS.values())),
    "created": TODAY - pd.to_timedelta(rng.integers(30, 1400, N), unit="D"),
})
raw_keys = list(RAW_INDUSTRY)
has_ind = rng.random(N) > 0.45                     # about 45% have no industry at all
df["industry_raw"] = np.where(has_ind, rng.choice(raw_keys, N), "")
df["source"] = rng.choice(["List import", "Form", "Event scan", "Sales added"], N, p=[.72, .12, .10, .06])
df["marketing_contact"] = rng.random(N) < np.where(df.source == "List import", .88, .55)
df["lifecycle"] = rng.choice(["Lead", "MQL", "SQL", "Opportunity", "Customer"], N,
                             p=[.90, .075, .015, .007, .003])
# engagement history
opened_ever = rng.random(N) < 0.26
df["last_open_days"] = np.where(opened_ever, rng.integers(1, 700, N), 9999)
df["ever_clicked"] = opened_ever & (rng.random(N) < 0.10)
df["sales_reply_days"] = np.where(rng.random(N) < 0.012, rng.integers(1, 400, N), 9999)
df["sales_click_days"] = np.where(rng.random(N) < 0.02, rng.integers(1, 400, N), 9999)
df["target_persona"] = df.job_title.isin(["Research Scientist", "Director of R&D", "VP Research",
                                          "Professor", "CGT Process Scientist", "Procurement Specialist"])

# ---------------- 2. engagement score with decay ----------------
def score(r):
    pts = 0.0
    for days, p in ((r.last_open_days, 5), (r.sales_click_days, 12), (r.sales_reply_days, 30)):
        if days < 9999:
            pts += p * (0.8 ** (days / 90))        # 20% decay every 3 months
    pts += 10 * 0.8 ** (r.last_open_days / 90) if r.ever_clicked and r.last_open_days < 9999 else 0
    return min(round(pts), 100)
df["engagement_score"] = df.apply(score, axis=1)

# ---------------- 3. dedupe ----------------
before = len(df)
df["email_norm"] = df.email.str.lower().str.strip()
dups = df.duplicated("email_norm", keep="first")
dup_count = int(dups.sum())
df = df[~dups].copy()

# ---------------- 4. audit the marketing tier ----------------
mk_before = int(df.marketing_contact.sum())
# protected: pipeline/customers, target personas, and anyone a person added on purpose (form, sales)
protected = (df.lifecycle.isin(["Opportunity", "Customer"]) | df.target_persona
             | df.source.isin(["Form", "Sales added"]) | (df.created > TODAY - pd.Timedelta(days=180)))
demote = (df.marketing_contact & (df.last_open_days >= 365) & (~df.ever_clicked)
          & (df.sales_reply_days > 90) & (df.engagement_score < 15) & (~protected))
promote = (~df.marketing_contact & ((df.sales_reply_days <= 90) | (df.sales_click_days <= 90)
                                    | (df.engagement_score >= 30)))
df["action"] = np.select([demote, promote], ["Demote to non-marketing", "Promote to marketing"], "Keep")
df["consent_check_needed"] = promote & (df.region == "EU/UK/CH")
df["marketing_contact_after"] = (df.marketing_contact & ~demote) | (promote & ~df.consent_check_needed)
mk_after = int(df.marketing_contact_after.sum())

# ---------------- 5. segmentation ----------------
df["segment"] = df.industry_raw.map(RAW_INDUSTRY).fillna("")
def by_title(t):
    t = t.lower()
    for pat, seg in TITLE_RULES:
        if re.search(pat, t):
            return seg
    return ""
filled = df.segment == ""
df.loc[filled, "segment"] = df.loc[filled, "job_title"].map(by_title)
df["segment_source"] = np.where(df.industry_raw != "", "mapped from industry",
                                np.where(df.segment != "", "inferred from title", "unknown"))
df.loc[df.segment == "", "segment"] = "Unclassified"
cover_before = float((df.industry_raw != "").mean())
cover_after = float((df.segment != "Unclassified").mean())
before_values = df.industry_raw[df.industry_raw != ""].nunique()

df.drop(columns=["email_norm"]).to_csv(DATA / "contacts_cleaned.csv", index=False)
(df[df.action != "Keep"][["contact_id", "email", "region", "lifecycle", "engagement_score",
                          "last_open_days", "action", "consent_check_needed"]]
 .to_csv(DATA / "change_log.csv", index=False))
# small samples are committed; the full files are regenerated by this script
df.drop(columns=["email_norm"]).sample(1000, random_state=1).to_csv(DATA / "contacts_sample.csv", index=False)
df[df.action != "Keep"].sample(500, random_state=1)[["contact_id", "email", "region", "lifecycle", "engagement_score",
    "action", "consent_check_needed"]].to_csv(DATA / "change_log_sample.csv", index=False)
pd.DataFrame(list(RAW_INDUSTRY.items()), columns=["industry_raw", "segment"]).to_csv(
    DATA / "industry_to_segment_map.csv", index=False)

kpis = {"contacts_before_dedupe": before, "duplicates_removed": dup_count, "contacts_after_dedupe": len(df),
        "tier_limit": TIER_LIMIT, "marketing_contacts_before": mk_before,
        "tier_usage_before": round(mk_before / TIER_LIMIT, 3),
        "demoted": int(demote.sum()), "promoted": int((promote & ~df.consent_check_needed).sum()),
        "promoted_held_for_consent": int(df.consent_check_needed.sum()),
        "marketing_contacts_after": mk_after, "tier_usage_after": round(mk_after / TIER_LIMIT, 3),
        "pct_never_opened": round(float((df.last_open_days == 9999).mean()), 3),
        "industry_coverage_before": round(cover_before, 3), "segment_coverage_after": round(cover_after, 3),
        "distinct_industry_values_before": int(before_values), "segments_after": 10}
pd.Series(kpis).to_csv(DATA / "kpi_summary.csv", header=["value"])
print(pd.Series(kpis).to_string())

# ---------------- 6. charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(18, 4.8))
fig.suptitle("RB Tech | CRM cleanup, segmentation and scoring (synthetic data)",
             fontsize=13, weight="bold")
ax[0].bar(["Before", "After"], [mk_before, mk_after], color=[RED, TEAL])
ax[0].axhline(TIER_LIMIT, color="k", ls="--", lw=.8)
ax[0].text(0.5, TIER_LIMIT * 1.01, f"tier limit {TIER_LIMIT:,}", ha="center")
ax[0].set(title="Marketing-contact tier", ylabel="contacts")
a = df.action.value_counts().reindex(["Keep", "Demote to non-marketing", "Promote to marketing"]).fillna(0)
ax[1].barh(["Keep", "Demote", "Promote"][::-1], a.values[::-1], color=[GREY, RED, TEAL][::-1])
ax[1].set_xscale("log")
ax[1].set(title="Cleanup actions (log scale)")
ax[2].bar(["Industry\nbefore", "Segment\nafter"], [cover_before * 100, cover_after * 100], color=[GOLD, BLUE])
ax[2].set(title="Classified contacts (%)", ylim=(0, 100))
for i, v in enumerate([cover_before * 100, cover_after * 100]):
    ax[2].text(i, v + 1.5, f"{v:.0f}%", ha="center")
sc = df.engagement_score
ax[3].hist(sc[sc > 0], bins=20, color=BLUE)
ax[3].axvline(15, color=GOLD, ls="--", lw=1)
ax[3].axvline(30, color=RED, ls="--", lw=1)
ax[3].text(15.5, ax[3].get_ylim()[1] * .9, "MQL 15", color=GOLD)
ax[3].text(30.5, ax[3].get_ylim()[1] * .8, "SQL 30", color=RED)
ax[3].set(title="Engagement score (non-zero)", xlabel="score")
fig.tight_layout(rect=[0, 0, 1, .92])
fig.savefig(CHARTS / "cleanup_overview.png", dpi=130)
print("done")
