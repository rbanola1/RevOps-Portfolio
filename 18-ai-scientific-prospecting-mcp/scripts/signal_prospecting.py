"""Synthetic run of the signal-based scientific prospecting workflow (lead database + AI assistant over MCP).

Writes data/candidates.csv, data/funnel.csv, data/tier_summary.csv, data/method_comparison.csv
and charts/prospecting_dashboard.png. Every name, organisation and number is generated.
"""
import hashlib
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(18)
N = 2400

SIGNALS = ["New grant (12 mo)", "Recent paper (6 mo)", "Clinical trial", "Conference poster", "New lab / new role"]
SIG_P = [0.32, 0.38, 0.06, 0.14, 0.10]
SEGMENTS = ["Academic lab", "Research institute", "Pharma / biotech", "CRO", "Hospital research"]
SEG_P = [0.46, 0.14, 0.20, 0.10, 0.10]
PERSONAS = ["Tissue biology", "In vitro toxicology", "Organ-on-chip / MPS", "Stem cell biology", "Assay development"]


def lead_id(name, org):
    """Stable ID from the person and organisation, so results from any tool map back to the same row."""
    return "L-" + hashlib.md5(f"{name.lower()}|{org.lower()}".encode()).hexdigest()[:6].upper()


df = pd.DataFrame({
    "name": [f"Researcher {i:04d}" for i in range(N)],
    "organisation": [f"Org {rng.integers(1, 650):03d}" for _ in range(N)],
    "segment": rng.choice(SEGMENTS, N, p=SEG_P),
    "persona": rng.choice(PERSONAS, N),
    "signal": rng.choice(SIGNALS, N, p=SIG_P),
    "signal_age_days": rng.integers(5, 365, N),
})
df["lead_id"] = [lead_id(n, o) for n, o in zip(df.name, df.organisation)]

# 1 CRM suppression: email, name + organisation and profile-handle keys against the CRM export
df["in_crm"] = rng.random(N) < 0.36
df["status"] = np.where(df.in_crm, "Suppressed: already in CRM", "Net new")

# 2 Fit score from persona match, segment and signal recency, then tiers
seg_w = {"Pharma / biotech": 30, "CRO": 28, "Hospital research": 22, "Research institute": 20, "Academic lab": 18}
sig_w = {"New grant (12 mo)": 30, "Clinical trial": 28, "Recent paper (6 mo)": 25, "New lab / new role": 22, "Conference poster": 18}
recency = np.clip(30 - df.signal_age_days / 12, 0, 30)
df["fit_score"] = (df.segment.map(seg_w) + df.signal.map(sig_w) + recency + rng.normal(10, 6, N)).round().clip(0, 100)
cuts = df.fit_score.quantile([0.35, 0.75]).tolist()  # top 25% = A, next 40% = B, rest = C
df["tier"] = pd.cut(df.fit_score, [-1, cuts[0], cuts[1], 101], labels=["C", "B", "A"]).astype(str)

# 3 Email coverage: database first, then a gap-fill pass for the rest, then verification
net = ~df.in_crm
db_hit = rng.random(N) < 0.68
gap_hit = (~db_hit) & (rng.random(N) < 0.48)
df["email_source"] = np.select([net & db_hit, net & gap_hit], ["Lead database", "Gap-fill pass"], "None found")
has_email = net & (db_hit | gap_hit)
deliverable = has_email & (rng.random(N) < 0.93)
df["email_status"] = np.select([deliverable, has_email], ["Verified", "Bounced on verify"], "No email")
df.loc[df.in_crm, ["email_source", "email_status"]] = "n/a"

# 4 Outreach: personalised drafts for verified A/B leads, reviewed by a person, sent from the CRM
ready = deliverable & df.tier.isin(["A", "B"])
reply_p = np.where(df.tier == "A", 0.085, 0.045)
df["sequenced"] = ready
df["replied"] = ready & (rng.random(N) < reply_p)
df["meeting"] = df.replied & (rng.random(N) < 0.45)

os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE, "charts"), exist_ok=True)
df.to_csv(os.path.join(BASE, "data", "candidates.csv"), index=False)

funnel = pd.DataFrame({
    "stage": ["Candidates from signal search", "Net new after CRM check", "Email found", "Verified deliverable",
              "Tier A/B sequenced", "Replied", "Meeting or sample request"],
    "count": [N, int(net.sum()), int(has_email.sum()), int(deliverable.sum()), int(ready.sum()),
              int(df.replied.sum()), int(df.meeting.sum())],
})
funnel.to_csv(os.path.join(BASE, "data", "funnel.csv"), index=False)

tiers = (df[net].groupby("tier").agg(leads=("lead_id", "count"), verified=("email_status", lambda s: (s == "Verified").sum()),
                                     replied=("replied", "sum"), meetings=("meeting", "sum")).reindex(["A", "B", "C"]))
tiers.to_csv(os.path.join(BASE, "data", "tier_summary.csv"))

comparison = pd.DataFrame({
    "metric": ["Share of list already in CRM", "Email coverage on net-new", "Bounce rate after verify",
               "Analyst hours per 100 ready leads", "Reply rate (sequenced)"],
    "keyword_list_export": [0.62, 0.55, 0.09, 6.0, 0.02],
    "signal_search_with_mcp": [round(df.in_crm.mean(), 2), round(has_email[net].mean(), 2),
                               round(1 - deliverable.sum() / has_email.sum(), 2), 1.5,
                               round(df.replied.sum() / ready.sum(), 3)],
})
comparison.to_csv(os.path.join(BASE, "data", "method_comparison.csv"), index=False)

# Dashboard
fig, ax = plt.subplots(1, 3, figsize=(16, 5.2))
ax[0].barh(funnel.stage[::-1], funnel["count"][::-1], color="#3b6ea8")
for i, v in enumerate(funnel["count"][::-1]):
    ax[0].text(v + 20, i, f"{v:,}", va="center", fontsize=9)
ax[0].set_title("Prospecting funnel")
ax[0].spines[["top", "right"]].set_visible(False)

src = df[net].email_source.value_counts().reindex(["Lead database", "Gap-fill pass", "None found"])
ax[1].bar(src.index, src.values, color=["#3b6ea8", "#7fa7d6", "#c9c9c9"])
ax[1].set_title("Where net-new emails came from")
ax[1].spines[["top", "right"]].set_visible(False)

m = comparison.set_index("metric").loc[["Share of list already in CRM", "Bounce rate after verify", "Reply rate (sequenced)"]]
x = np.arange(len(m))
ax[2].bar(x - 0.2, m.keyword_list_export * 100, 0.4, label="Keyword list export", color="#c9c9c9")
ax[2].bar(x + 0.2, m.signal_search_with_mcp * 100, 0.4, label="Signal search + MCP", color="#3b6ea8")
ax[2].set_xticks(x, ["Already in CRM", "Bounce", "Reply"])
ax[2].set_ylabel("%")
ax[2].set_title("Old method vs new method")
ax[2].legend(frameon=False)
ax[2].spines[["top", "right"]].set_visible(False)

fig.suptitle("RB Tech: signal-based scientific prospecting (synthetic)", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(BASE, "charts", "prospecting_dashboard.png"), dpi=130)

print(funnel.to_string(index=False))
print(tiers)
print(comparison.to_string(index=False))
