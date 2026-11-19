"""Voice-of-customer program model for Aurelis Life Sciences (fictional): capture, tag, visualise after trade shows.

Generates ~480 synthetic VOC entries from trade shows, webinars, tickets and surveys, then builds the
post-event dashboard: themes by event, theme x segment heatmap, sentiment by product, competitor mentions,
objection and request rankings, and event follow-up conversion.
All entries are invented. Run: python scripts/voc_program.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(404)

EVENTS = {  # name: (date, volume weight, lead conversion, deal conversion)
    "Neuroscience Annual Meeting": ("2026-02-12", 1.0, .46, .13),
    "Toxicology Congress": ("2026-03-25", 0.9, .40, .11),
    "Lab Automation Expo": ("2026-04-18", 0.7, .35, .08),
    "Stem Cell Research Summit": ("2026-06-10", 1.1, .52, .16),
    "Regional Biotech Showcase": ("2026-09-03", 0.5, .44, .12),
    "Customer webinar series": ("2026-10-05", 0.6, .30, .07),
}
SEGMENTS = {"Academia": .38, "Biotech": .17, "Pharma": .09, "CRO": .09, "CGT Developer": .08, "Hospital": .05,
            "Core facility": .05, "Nonprofit foundation": .03, "Government": .03, "Distributor": .03}
THEMES = {"Product performance": .17, "Documentation": .08, "Pricing and quotes": .14, "Delivery and logistics": .09,
          "Application support": .12, "Competitor information": .10, "Product request": .14, "Testimonial": .08,
          "Objection: evidence or data": .08}
PRODUCTS = ["Endothelial cells", "Progenitor cells", "Neural media kit", "Small molecules", "Expansion medium", "Custom services"]
COMPETITORS = ["Vendor Alpha", "Vendor Beta", "Vendor Gamma", "Vendor Delta", "In-house protocol"]
SOURCES = {"Booth conversation": .55, "Support ticket": .17, "Customer survey": .13, "Email": .10, "Webinar question": .05}

# theme sentiment tendency (negative for objections, positive for testimonials)
SENT = {"Product performance": 0.0, "Documentation": -0.5, "Pricing and quotes": -0.6, "Delivery and logistics": -0.3,
        "Application support": 0.1, "Competitor information": -0.2, "Product request": 0.4, "Testimonial": 1.6,
        "Objection: evidence or data": -1.1}
rows = []
n_total = 480
w = np.array([v[1] for v in EVENTS.values()])
alloc = (w / w.sum() * n_total).round().astype(int)
for (ev, (d, _, lc, dc)), n in zip(EVENTS.items(), alloc):
    date0 = pd.Timestamp(d)
    for i in range(n):
        seg = rng.choice(list(SEGMENTS), p=list(SEGMENTS.values()))
        theme = rng.choice(list(THEMES), p=np.array(list(THEMES.values())) / sum(THEMES.values()))
        src = "Webinar question" if ev == "Customer webinar series" else rng.choice(
            [k for k in SOURCES if k != "Webinar question"], p=np.array([.62, .2, .1, .08]))
        prod = rng.choice(PRODUCTS)
        sent = int(np.clip(round(rng.normal(SENT[theme], .9)), -2, 2))
        comp = rng.choice(COMPETITORS) if theme in ("Competitor information", "Objection: evidence or data") or rng.random() < .06 else ""
        lead = rng.random() < lc
        deal = lead and rng.random() < dc / lc
        rows.append(dict(voc_id=f"VOC-{(date0 + pd.Timedelta(days=int(rng.integers(0, 3)))).strftime('%Y%m%d')}-{i + 1}",
                         event=ev, event_date=d, source=src, segment=seg, role=rng.choice(
                             ["PI / lab head", "Scientist", "Director", "Procurement", "Founder / executive"], p=[.2, .38, .17, .1, .15]),
                         theme=theme, product=prod, sentiment=sent, competitor=comp,
                         contacts_count=int(rng.choice([1, 1, 1, 2, 3])),
                         became_lead=lead, became_deal=deal,
                         action=("Send protocol and data" if theme == "Application support" else
                                 "Route to product management" if theme == "Product request" else
                                 "Send reference and data pack" if theme.startswith("Objection") else
                                 "Request permission to quote" if theme == "Testimonial" else
                                 "Follow up within 48 hours")))
voc = pd.DataFrame(rows)
voc.to_csv(DATA / "voc_entries.csv", index=False)

# ---------------- analysis ----------------
ev_theme = voc.pivot_table(index="event", columns="theme", values="voc_id", aggfunc="count", fill_value=0)
ev_theme.to_csv(DATA / "events_by_theme.csv")
heat = voc.pivot_table(index="theme", columns="segment", values="voc_id", aggfunc="count", fill_value=0)
heat.to_csv(DATA / "theme_by_segment.csv")
sent_prod = voc.groupby("product").sentiment.mean().round(2).sort_values()
sent_prod.to_csv(DATA / "sentiment_by_product.csv", header=["avg_sentiment"])
comp = voc[voc.competitor != ""].groupby("competitor").agg(mentions=("voc_id", "count"), avg_sentiment=("sentiment", "mean")).round(2)
comp.to_csv(DATA / "competitor_mentions.csv")
objections = voc[voc.theme == "Objection: evidence or data"]
requests = voc[voc.theme == "Product request"].groupby("product").size().sort_values(ascending=False)
requests.to_csv(DATA / "product_requests.csv", header=["requests"])
ev_roi = voc.groupby("event").agg(entries=("voc_id", "count"), leads=("became_lead", "sum"), deals=("became_deal", "sum")).assign(
    lead_rate=lambda d: (d.leads / d.entries).round(2), deal_rate=lambda d: (d.deals / d.entries).round(2))
ev_roi.to_csv(DATA / "event_followup_conversion.csv")
print(ev_roi.to_string())
print("negative share:", round((voc.sentiment < 0).mean(), 2), "| testimonials:", int((voc.theme == "Testimonial").sum()))

# ---------------- dashboard ----------------
plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(2, 3, figsize=(18, 9))
fig.suptitle("Aurelis Life Sciences | Voice of customer after trade shows (synthetic data)", fontsize=13, weight="bold")
cols = plt.cm.tab20(np.linspace(0, 1, len(ev_theme.columns)))
bottom = np.zeros(len(ev_theme))
for c, col in zip(ev_theme.columns, cols):
    ax[0, 0].barh([e[:24] for e in ev_theme.index], ev_theme[c], left=bottom, color=col, label=c)
    bottom += ev_theme[c].values
ax[0, 0].legend(fontsize=6, loc="lower right", ncol=1)
ax[0, 0].set(title="VOC entries by event and theme", xlabel="entries")
im = ax[0, 1].imshow(heat.values, cmap="Blues", aspect="auto")
ax[0, 1].set_xticks(range(len(heat.columns)), [c[:10] for c in heat.columns], rotation=60, ha="right", fontsize=7)
ax[0, 1].set_yticks(range(len(heat.index)), [t[:24] for t in heat.index], fontsize=7)
for i in range(heat.shape[0]):
    for j in range(heat.shape[1]):
        ax[0, 1].text(j, i, heat.values[i, j], ha="center", va="center", fontsize=6,
                      color="white" if heat.values[i, j] > heat.values.max() * .55 else "black")
ax[0, 1].set(title="Theme by segment (count)")
ax[0, 2].barh(sent_prod.index, sent_prod.values, color=[RED if v < 0 else TEAL for v in sent_prod.values])
ax[0, 2].axvline(0, color="k", lw=.6)
ax[0, 2].set(title="Average sentiment by product (-2 to +2)", xlabel="sentiment")
c = comp.sort_values("mentions")
ax[1, 0].barh(c.index, c.mentions, color=[RED if v < 0 else GOLD for v in c.avg_sentiment])
ax[1, 0].set(title="Competitor mentions", xlabel="mentions")
rq = requests.sort_values()
ax[1, 1].barh(rq.index, rq.values, color=BLUE)
ax[1, 1].set(title="Product requests by product area", xlabel="requests")
x = np.arange(len(ev_roi))
ax[1, 2].bar(x - .2, ev_roi.lead_rate * 100, .4, color=GOLD, label="Became a lead")
ax[1, 2].bar(x + .2, ev_roi.deal_rate * 100, .4, color=TEAL, label="Became a deal")
ax[1, 2].set_xticks(x, [e[:14] for e in ev_roi.index], rotation=35, ha="right", fontsize=7)
ax[1, 2].legend(fontsize=8)
ax[1, 2].set(title="Follow-up conversion by event (% of VOC entries)", ylabel="%")
fig.tight_layout(rect=[0, 0, 1, .95])
fig.savefig(CHARTS / "voc_dashboard.png", dpi=125)
print("done")
