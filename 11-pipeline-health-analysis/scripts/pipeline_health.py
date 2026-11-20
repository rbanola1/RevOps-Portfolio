"""Pipeline health analysis for RB Tech (fictional): stage conversion, ageing, coverage, stalled deals.

Builds ~110 synthetic deals over the past year, then produces the weekly pipeline-health view:
stage conversion, deal ageing against benchmark, coverage versus quota, stalled-deal list, win rate by source,
and weighted versus unweighted pipeline.  All data is invented.
Run: python scripts/pipeline_health.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(1101)

STAGES = ["Qualified", "Needs confirmed", "Quote sent", "Negotiation", "Won"]
STAGE_PROB = {"Qualified": .10, "Needs confirmed": .25, "Quote sent": .50, "Negotiation": .75, "Won": 1.0}
BENCH_DAYS = {"Qualified": 14, "Needs confirmed": 21, "Quote sent": 18, "Negotiation": 14}   # healthy time in each stage
SOURCES = {"Inbound web": .22, "Trade show": .25, "Outbound sequence": .20, "Distributor referral": .18, "Existing customer": .15}
SEG = {"Academia": .38, "Biotech": .22, "Pharma": .12, "CRO": .12, "CGT developer": .10, "Core facility": .06}
CONT = {"Inbound web": .62, "Trade show": .70, "Outbound sequence": .60, "Distributor referral": .76, "Existing customer": .88}  # chance of moving up a stage
TODAY = pd.Timestamp("2026-10-31")

rows = []
for i in range(110):
    src = rng.choice(list(SOURCES), p=list(SOURCES.values()))
    seg = rng.choice(list(SEG), p=list(SEG.values()))
    created = TODAY - pd.Timedelta(days=int(rng.integers(5, 330)))
    amount = float(np.round(np.exp(rng.normal(8.5, .6)) / 50) * 50)
    status, reached, t = "Open", 0, created
    days_in_stage = 0
    for k in range(4):
        slow = 1.25 if seg in ("Pharma", "CGT developer") else 1.0
        stay = int(max(2, rng.gamma(2.2, BENCH_DAYS[STAGES[k]] / 2.0 * slow)))
        if t + pd.Timedelta(days=stay) > TODAY:        # still sitting in this stage
            reached, days_in_stage = k, (TODAY - t).days
            break
        t += pd.Timedelta(days=stay)
        if rng.random() > CONT[src] * (1 + .04 * k):   # lost at this stage
            status, reached, days_in_stage = "Lost", k, stay
            break
        reached = k + 1
    else:
        reached = 4
    if reached == 4 and status == "Open":
        status = "Won"
    last_act = TODAY - pd.Timedelta(days=int(rng.exponential(9))) if status == "Open" else t
    rows.append(dict(deal_id=f"D-{1000 + i}", created=created.date(), source=src, segment=seg, amount=amount,
                     stage=STAGES[reached], status=status, days_in_stage=days_in_stage,
                     last_activity=pd.Timestamp(last_act).date(), furthest_stage=STAGES[reached]))
d = pd.DataFrame(rows)
d["last_activity"] = pd.to_datetime(d.last_activity)
d.to_csv(DATA / "deals.csv", index=False)

# ---------- stage conversion (deals reaching at least each stage) ----------
order = {s: i for i, s in enumerate(STAGES)}
d["reach"] = d.furthest_stage.map(order)
funnel = pd.DataFrame({"stage": STAGES, "deals_reached": [int((d.reach >= i).sum()) for i in range(5)]})
funnel["conversion_from_prior"] = (funnel.deals_reached / funnel.deals_reached.shift(1)).round(2)
funnel.to_csv(DATA / "stage_conversion.csv", index=False)

# ---------- open pipeline, ageing, stalled ----------
op = d[d.status == "Open"].copy()
op["bench"] = op.stage.map(BENCH_DAYS)
op["age_ratio"] = (op.days_in_stage / op.bench).round(2)
op["idle_days"] = (TODAY - op.last_activity).dt.days
op["stalled"] = (op.age_ratio > 2) | (op.idle_days > 21)
op["weighted"] = op.amount * op.stage.map(STAGE_PROB)
stalled = op[op.stalled].sort_values("amount", ascending=False)
stalled[["deal_id", "source", "segment", "stage", "amount", "days_in_stage", "idle_days"]].head(40).to_csv(DATA / "stalled_deals.csv", index=False)
by_stage = op.groupby("stage").agg(deals=("deal_id", "count"), value=("amount", "sum"), weighted=("weighted", "sum"),
                                   stalled=("stalled", "sum")).reindex(STAGES[:4]).fillna(0).round(0)
by_stage.to_csv(DATA / "open_pipeline_by_stage.csv")

# ---------- coverage vs quota ----------
QUOTA = op.amount.sum() / 2.4          # synthetic quota set so reported coverage looks healthy but is not
coverage = pd.DataFrame({"measure": ["Open pipeline value", "Weighted pipeline", "Quota next quarter", "Coverage (open / quota)",
                                      "Coverage after removing stalled", "Open value needed for 3x coverage"],
                         "value": [op.amount.sum(), op.weighted.sum(), QUOTA, op.amount.sum() / QUOTA,
                                   op[~op.stalled].amount.sum() / QUOTA, QUOTA * 3]}).round(2)
coverage.to_csv(DATA / "coverage_vs_quota.csv", index=False)

# ---------- win rate by source ----------
closed = d[d.status != "Open"]
wr_src = pd.DataFrame({"closed": closed.groupby("source").size(),
                       "win_rate": closed.groupby("source").apply(lambda g: (g.status == "Won").mean(), include_groups=False),
                       "avg_won_deal": closed[closed.status == "Won"].groupby("source").amount.mean()}).round(2)
wr_src.to_csv(DATA / "win_rate_by_source.csv")

print(funnel.to_string(index=False)); print(coverage.to_string(index=False)); print(wr_src)
print("open deals", len(op), "| stalled", int(op.stalled.sum()), "| stalled value share", round(op[op.stalled].amount.sum() / op.amount.sum(), 2),
      "| overall win rate", round((closed.status == "Won").mean(), 2))

# ---------- dashboard ----------
plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(2, 3, figsize=(18, 9))
fig.suptitle("RB Tech | Pipeline health (synthetic data, as of 31 Oct 2026)", fontsize=13, weight="bold")
ax[0, 0].barh(funnel.stage[::-1], funnel.deals_reached[::-1], color=BLUE)
for y, (n, c) in enumerate(zip(funnel.deals_reached[::-1], funnel.conversion_from_prior[::-1])):
    ax[0, 0].text(n + 6, y, f"{n}" + ("" if np.isnan(c) else f"  ({c:.0%})"), va="center", fontsize=8)
ax[0, 0].set(title="Stage conversion: deals reaching each stage", xlabel="deals")
ax[0, 0].set_xlim(0, funnel.deals_reached.max() * 1.2)
x = np.arange(4)
ax[0, 1].bar(x - .2, by_stage.value / 1e3, .4, color=GREY, label="Open value")
ax[0, 1].bar(x + .2, by_stage.weighted / 1e3, .4, color=TEAL, label="Weighted")
ax[0, 1].set_xticks(x, by_stage.index, fontsize=8)
ax[0, 1].legend()
ax[0, 1].set(title="Open pipeline: value vs weighted ($K)", ylabel="$K")
cov = [op.amount.sum() / QUOTA, op[~op.stalled].amount.sum() / QUOTA]
ax[0, 2].bar(["As reported", "Without stalled deals"], cov, color=[BLUE, GOLD], width=.5)
ax[0, 2].axhline(3, color=RED, ls="--")
ax[0, 2].text(1.45, 3.05, "3x target", color=RED, ha="right")
for i, v in enumerate(cov):
    ax[0, 2].text(i, v + .05, f"{v:.1f}x", ha="center", weight="bold")
ax[0, 2].set(title="Pipeline coverage of next-quarter quota", ylabel="x quota")
ar = op.groupby("stage").age_ratio.median().reindex(STAGES[:4])
ax[1, 0].bar(ar.index, ar.values, color=[RED if v > 1.5 else TEAL for v in ar.values])
ax[1, 0].axhline(1, color="k", lw=.7)
ax[1, 0].set(title="Median time in stage vs benchmark (1.0 = on benchmark)", ylabel="ratio")
w = wr_src.win_rate.sort_values()
ax[1, 1].barh(w.index, w.values * 100, color=BLUE)
ax[1, 1].set(title="Win rate by lead source", xlabel="% of closed deals")
sh = stalled.groupby("stage").amount.sum().reindex(STAGES[:4]).fillna(0)
ax[1, 2].bar(sh.index, sh.values / 1e3, color=RED)
ax[1, 2].set(title="Stalled value by stage ($K)", ylabel="$K")
fig.tight_layout(rect=[0, 0, 1, .95])
fig.savefig(CHARTS / "pipeline_health_dashboard.png", dpi=125)
print("done")

# ---------- CRM as a factory: raw material in, how much was actually worked? ----------
# 4,000 synthetic records enter the CRM in a year. Nothing is "wasted" (no bad data); the loss is material that was never used.
rng2 = np.random.default_rng(1102)
N = 1600
lead_src = rng2.choice(list(SOURCES), size=N, p=list(SOURCES.values()))
touch_p = {"Inbound web": .80, "Trade show": .55, "Outbound sequence": .70, "Distributor referral": .85, "Existing customer": .95}
touched = np.array([rng2.random() < touch_p[s] for s in lead_src])
worked = touched & (rng2.random(N) < .55)            # more than one real attempt
qualified = worked & (rng2.random(N) < .30)
deal = qualified & (rng2.random(N) < .62)
won = deal & (rng2.random(N) < .29)
touches = np.where(~touched, 0, np.where(~worked, 1, 2 + rng2.poisson(.6, N)))
touches = touches + np.where(qualified, 4 + rng2.poisson(3, N), 0) + np.where(deal, 6, 0) + np.where(won, 15, 0)
lu = pd.DataFrame({"touches": touches, "source": lead_src, "touched": touched, "worked": worked, "qualified": qualified, "deal": deal, "won": won})
station = pd.DataFrame({"station": ["Records in CRM", "Touched at least once", "Worked (follow-up attempts)", "Qualified", "Deal created", "Won"],
                        "records": [N, int(touched.sum()), int(worked.sum()), int(qualified.sum()), int(deal.sum()), int(won.sum())]})
station["share_of_input"] = (station.records / N).round(3)
station.to_csv(DATA / "crm_factory_stations.csv", index=False)
idle = lu.groupby("source").apply(lambda g: pd.Series({"records": len(g), "never_touched": int((~g.touched).sum()),
                                                      "touched_not_worked": int((g.touched & ~g.worked).sum()),
                                                      "idle_share": ((~g.worked).mean()).round(2),
                                                      "won": int(g.won.sum())}), include_groups=False)
idle.to_csv(DATA / "crm_factory_idle_by_source.csv")
print(station.to_string(index=False)); print(idle)
fig2, a2 = plt.subplots(1, 3, figsize=(19, 5.4))
fig2.suptitle("CRM as a factory: the material was not wasted, it was not used (synthetic data)", fontsize=12, weight="bold")
a2[0].barh(station.station[::-1], station.records[::-1], color=[TEAL, GOLD, GOLD, BLUE, BLUE, BLUE][::-1][::-1] if False else BLUE)
for y, (n, s) in enumerate(zip(station.records[::-1], station.share_of_input[::-1])):
    a2[0].text(n + 40, y, f"{n:,}  ({s:.0%})", va="center", fontsize=8.5)
a2[0].set(title="Records reaching each station of the line", xlabel="records"); a2[0].set_xlim(0, N * 1.2)
bins = ["0", "1", "2", "3", "4", "5", "6+"]
cnt = [int((touches == k).sum()) for k in range(6)] + [int((touches >= 6).sum())]
cols_ = [RED, RED, GOLD, GOLD, GOLD, GOLD, TEAL]
a2[1].bar(bins, cnt, color=cols_)
for i_, v_ in enumerate(cnt):
    a2[1].text(i_, v_ + max(cnt) * .01, f"{v_} ({v_ / N:.0%})", ha="center", fontsize=8)
a2[1].set(title=f"Touches per record: average {touches.mean():.1f}, most records sit on the floor (red)", xlabel="number of touches (calls, emails, meetings)", ylabel="records")
pd.DataFrame({"touches": bins, "records": cnt}).to_csv(DATA / "crm_factory_touches.csv", index=False)
idle_avg = touches[~deal].mean()
deal_avg = touches[deal & ~won].mean()
won_avg = touches[won].mean()
a2[2].bar(["Idle record (no deal)", "Became a deal", "Closed won"], [idle_avg, deal_avg, won_avg], color=[RED, GOLD, TEAL])
for i_, v_ in enumerate([idle_avg, deal_avg, won_avg]):
    a2[2].text(i_, v_ + .5, f"{v_:.0f}", ha="center", weight="bold")
a2[2].set(title="Average touches by outcome: effort climbs with the result", ylabel="touches per record")
pd.DataFrame({"outcome": ["idle", "deal", "won"], "avg_touches": [idle_avg, deal_avg, won_avg]}).round(1).to_csv(DATA / "crm_factory_touches_by_outcome.csv", index=False)
print("touch share <=3:", round(float((touches <= 3).mean()), 3), "avg all", round(float(touches.mean()), 2), "idle/deal/won", round(idle_avg, 1), round(deal_avg, 1), round(won_avg, 1))
fig2.tight_layout(rect=[0, 0, 1, .93]); fig2.savefig(CHARTS / "crm_factory_utilization.png", dpi=125)
print("done factory")
