"""Synthetic support operations model for RB Tech (fictional).

Covers: ticket intake and routing, SLA performance, an AI triage agent with a human-review queue,
and an auto-reply loop with and without guardrails. All data is invented.
Run: python scripts/support_ops.py       Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(77)

# ---------------- 1. tickets ----------------
CAT = {"Spam": .50, "General inquiry": .17, "Pre-sale support": .09, "Order and shipping": .07,
       "Technical support": .06, "Custom project request": .04, "Documentation request": .03,
       "Accounting": .02, "Collaboration inquiry": .02}
TEMPLATES = {
    "Spam": ["unsubscribe me now", "seo services for your website", "congratulations you won a prize",
             "buy followers cheap", "guest post offer", "domain expiry notice"],
    "General inquiry": ["do you ship internationally", "where can I find your catalogue", "general question about products"],
    "Pre-sale support": ["quote for cell line A please", "pricing for 5 vials", "can I get a sample before ordering",
                         "bulk discount for academic lab"],
    "Order and shipping": ["where is my order", "tracking number not working", "package arrived thawed", "change delivery address"],
    "Technical support": ["cells not attaching after thaw", "protocol question for differentiation", "media storage conditions",
                          "viability low after revival"],
    "Custom project request": ["custom differentiation project proposal", "need new cell line developed", "custom service quote"],
    "Documentation request": ["need safety data sheet", "certificate of analysis for lot", "user manual download"],
    "Accounting": ["invoice copy needed", "payment sent please confirm", "tax exempt certificate attached"],
    "Collaboration inquiry": ["therapeutics collaboration proposal", "partnership opportunity", "licensing discussion"],
}
N = 600
truth = rng.choice(list(CAT), N, p=list(CAT.values()))
text = [rng.choice(TEMPLATES[c]) for c in truth]
tickets = pd.DataFrame({"ticket_id": [f"T{40000 + i}" for i in range(N)], "category": truth, "text": text,
                        "created": pd.Timestamp("2026-01-05") + pd.to_timedelta(rng.integers(0, 320 * 24, N), unit="h")})

# ---------------- 2. routing rules and owners ----------------
OWNERS = {"Pre-sale support": ("Outside rep", "Inside sales"), "General inquiry": ("Inside sales", "Operations"),
          "Order and shipping": ("Inside sales", "Outside rep"), "Technical support": ("Technical specialist", "Outside rep"),
          "Custom project request": ("Business development", "Technical specialist"),
          "Documentation request": ("Operations", "Inside sales"), "Accounting": ("Finance", "Operations"),
          "Collaboration inquiry": ("Business development", "Executive"), "Spam": ("Auto-closed", "")}
tickets["owner"] = tickets.category.map(lambda c: OWNERS[c][0])
tickets["manual_phase"] = tickets.created < pd.Timestamp("2026-06-01")    # before routing automation went live

# ---------------- 3. SLA performance before and after routing + guardrails ----------------
SLA_H = {"Pre-sale support": 4, "General inquiry": 24, "Order and shipping": 8, "Technical support": 12,
         "Custom project request": 24, "Documentation request": 24, "Accounting": 24, "Collaboration inquiry": 48,
         "Spam": 1}
def first_response(cat, manual):
    base = SLA_H[cat] * (1.9 if manual else 0.55)
    return float(rng.gamma(2.0, base / 2.0))
def close_days(cat, manual):
    if cat == "Spam":
        return float(rng.exponential(0.2 if not manual else 1.2))
    return float(rng.gamma(2.0, (4.0 if manual else 1.8) / 2.0))
tickets["first_response_h"] = [first_response(c, m) for c, m in zip(tickets.category, tickets.manual_phase)]
tickets["days_to_close"] = [close_days(c, m) for c, m in zip(tickets.category, tickets.manual_phase)]
tickets["sla_h"] = tickets.category.map(SLA_H)
tickets["sla_met"] = tickets.first_response_h <= tickets.sla_h
tickets["ces"] = np.where(tickets.category == "Spam", np.nan,
                          np.clip(rng.normal(np.where(tickets.manual_phase, 4.9, 5.8), .9), 1, 7).round(1))
real = tickets[tickets.category != "Spam"]
sla = real.groupby("manual_phase").agg(sla_met=("sla_met", "mean"), avg_close_days=("days_to_close", "mean"),
                                       ces=("ces", "mean"), tickets=("ticket_id", "count")).round(3)
sla.index = ["Routing + guardrails" if not i else "Before" for i in sla.index]
sla = sla.reindex(["Before", "Routing + guardrails"])
sla.to_csv(DATA / "sla_before_after.csv")

# ---------------- 4. AI triage agent (rule-based stand-in for an LLM) ----------------
KEYWORDS = {
    "Spam": ["unsubscribe", "seo", "prize", "followers", "guest post", "domain expiry"],
    "Pre-sale support": ["quote", "pricing", "sample", "discount", "bulk"],
    "Order and shipping": ["order", "tracking", "package", "delivery", "thawed"],
    "Technical support": ["thaw", "protocol", "storage", "viability", "attaching", "differentiation"],
    "Custom project request": ["custom", "developed", "proposal"],
    "Documentation request": ["safety data", "certificate of analysis", "manual", "download"],
    "Accounting": ["invoice", "payment", "tax exempt"],
    "Collaboration inquiry": ["collaboration", "partnership", "licensing", "therapeutics"],
    "General inquiry": ["ship", "catalogue", "general question"],
}
def triage(t):
    scores = {c: sum(k in t for k in kws) for c, kws in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    top = scores[best]
    tie = sum(v == top for v in scores.values()) > 1
    conf = 0.35 if top == 0 else (0.6 if tie else min(0.55 + 0.2 * top, 0.97))
    return (best if top else "General inquiry"), conf
res = tickets.text.map(triage)
tickets["agent_category"] = [r[0] for r in res]
tickets["agent_confidence"] = [r[1] for r in res]
# add realistic noise: the agent is wrong on a small share of ambiguous tickets
flip = rng.random(N) < 0.04
tickets.loc[flip, "agent_category"] = rng.choice(list(CAT), flip.sum())
tickets.loc[flip, "agent_confidence"] = rng.uniform(.4, .75, flip.sum())
THRESH = 0.7
tickets["auto_routed"] = tickets.agent_confidence >= THRESH
tickets["correct"] = tickets.agent_category == tickets.category
auto = tickets[tickets.auto_routed]
review = tickets[~tickets.auto_routed]
agent = pd.Series({"tickets": N, "auto_routed_share": round(len(auto) / N, 3),
                   "accuracy_auto_routed": round(float(auto.correct.mean()), 3),
                   "accuracy_review_queue_before_human": round(float(review.correct.mean()), 3),
                   "overall_accuracy_with_human_review": 1.0 if False else round(float((auto.correct.sum() + len(review)) / N), 3),
                   "spam_caught_rate": round(float(((tickets.category == "Spam") & (tickets.agent_category == "Spam")).sum()
                                                 / (tickets.category == "Spam").sum()), 3),
                   "confidence_threshold": THRESH})
agent.to_csv(DATA / "agent_performance.csv", header=["value"])
cm = pd.crosstab(tickets.category, tickets.agent_category)
cm.to_csv(DATA / "agent_confusion_matrix.csv")
tickets.drop(columns=["manual_phase"]).sample(300, random_state=2).to_csv(DATA / "tickets_sample.csv", index=False)

# ---------------- 5. auto-reply loop with and without guardrails ----------------
def loop(guard, hours=48):
    """Cumulative tickets created by an auto-reply loop with an external helpdesk robot.
    Without guardrails each ticket triggers an acknowledgement that the robot answers with a new email,
    so volume grows each hour until the other side's queue stops it. With guardrails the acknowledgement
    is skipped for auto-reply subjects and limited to one per sender per hour, so the loop never starts."""
    cumulative, per_hour = 0, []
    arriving = 1
    for h in range(hours):
        cumulative += arriving
        per_hour.append(cumulative)
        if guard:
            arriving = 0                                    # rule 1 and rule 2 break the loop immediately
        else:
            growth = 1.12 if h < 32 else 0.0                # sender's robot stops after about a day and a half
            arriving = int(np.ceil(arriving * growth * rng.uniform(.85, 1.15))) if growth else 0
    return per_hour
no_guard = loop(False)
guard = loop(True)
pd.DataFrame({"hour": range(48), "tickets_without_guardrails": no_guard, "tickets_with_guardrails": guard}
             ).to_csv(DATA / "loop_simulation.csv", index=False)
print(sla.to_string())
print(agent.to_string())
print("loop tickets after 48h: without", no_guard[-1], "with", guard[-1])

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("RB Tech | Service Hub and support agents (synthetic data)", fontsize=13, weight="bold")
cnt = tickets.category.value_counts().sort_values()
ax[0].barh(cnt.index, cnt.values, color=[GREY if c == "Spam" else BLUE for c in cnt.index])
ax[0].set(title="Ticket volume by category (spam routed out of the queue)", xlabel="tickets")
x = np.arange(2)
ax[1].bar(x - .2, sla.sla_met * 100, .4, color=[RED, TEAL], label="First-response SLA met %")
for i, v in enumerate(sla.sla_met * 100):
    ax[1].text(i - .2, v + 1, f"{v:.0f}%", ha="center")
ax2 = ax[1].twinx()
ax2.bar(x + .2, sla.avg_close_days, .4, color=GOLD, label="Avg days to close")
ax2.spines["top"].set_visible(False)
ax[1].set_xticks(x, sla.index)
ax[1].set(title="Routing and guardrails: SLA and close time", ylim=(0, 110), ylabel="SLA met %")
ax2.set_ylabel("days")
ax[2].bar(["Auto-routed", "Human review"], [len(auto), len(review)], color=[TEAL, GOLD])
ax[2].set(title=f"AI triage: {len(auto)/N:.0%} auto-routed at {THRESH:.0%} confidence", ylabel="tickets")
ax[2].text(0, len(auto) * .5, f"accuracy\n{auto.correct.mean():.0%}", ha="center", color="white", weight="bold")
ax[3].plot(range(48), no_guard, color=RED, label="No guardrails")
ax[3].plot(range(48), guard, color=TEAL, label="With guardrails")
ax[3].set_yscale("log")
ax[3].legend(fontsize=8)
ax[3].set(title="Loop guardrails: runaway tickets stopped (each gridline is 10x)", xlabel="hours", ylabel="tickets created")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "support_overview.png", dpi=130)
print("done")
