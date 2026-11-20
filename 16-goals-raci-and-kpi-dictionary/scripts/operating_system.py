"""Commercial operating system for Aurelis Life Sciences (fictional): goal tracker, RACI matrix and KPI dictionary.

Builds a synthetic company-to-project goal tracker with status, a RACI matrix for commercial processes, a KPI dictionary
(definition, source of truth, owner, cadence) and the executive KPI pack layout, then charts goal delivery.
All data is invented. Run: python scripts/operating_system.py     Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(1601)

# ---------- 1. goal tracker: company goal -> department goal -> project ----------
G = [  # name, type, priority, lead, due, status
    ("Reach annual revenue goal", "Company goal", 1, "CEO", "Q4", "On track"),
    ("Generate 1,600 leads at 1% conversion", "Company goal", 1, "Commercial ops", "Q4", "On track"),
    ("Set up distributor network", "Company goal", 1, "Business development", "Q3", "Completed"),
    ("Launch product line A", "Company goal", 1, "Product", "Q2", "Completed"),
    ("Launch product line B", "Company goal", 1, "Product", "Q3", "Completed"),
    ("Launch product line C", "Company goal", 1, "Product", "Q3", "Under review"),
    ("Launch product line D", "Company goal", 2, "Product", "Q4", "Not started"),
    ("Relaunch two existing products", "Department goal", 1, "R&D", "Q4", "Not started"),
    ("Hire technical account manager", "Department goal", 1, "CEO", "Q4", "Completed"),
    ("Partnering financial model and forecast", "Department goal", 1, "Business development", "Q3", "Not started"),
    ("Weekly sales report", "Commercial system", 1, "Commercial ops", "Q3", "Completed"),
    ("Sales performance dashboard", "Commercial system", 1, "Commercial ops", "Q4", "Completed"),
    ("CRM and accounting integration", "Commercial system", 1, "Commercial ops", "Q3", "Completed"),
    ("Billing and BI integration", "Commercial system", 1, "Commercial ops", "Q3", "Cancelled"),
    ("Service Hub and ticketing", "Commercial system", 1, "Support lead", "Q3", "Completed"),
    ("Roles and responsibilities matrix", "Commercial system", 3, "Commercial ops", "Q3", "Under review"),
    ("Voice of customer organisation", "Commercial system", 3, "Commercial ops", "Q4", "Completed"),
    ("Shipping cost model, version 2", "Commercial system", 1, "Commercial ops", "Q3", "Completed"),
    ("Packaging redesign", "Operations project", 2, "Operations", "Q4", "Completed"),
    ("Quality management system", "Operations goal", 1, "Operations", "Q4", "On track"),
    ("Inventory management system", "Operations goal", 1, "Operations", "Q4", "On track"),
    ("Stage-gate framework", "Company goal", 1, "Product", "Q4", "On track"),
]
goals = pd.DataFrame(G, columns=["goal", "type", "priority", "lead", "due", "status"])
goals["year"] = 2026
goals.to_csv(DATA / "goal_tracker.csv", index=False)
status_counts = goals.status.value_counts()
by_type = goals.groupby("type").apply(lambda g: pd.Series({"goals": len(g), "completed": int((g.status == "Completed").sum()),
                                                           "on_track_or_done": int(g.status.isin(["Completed", "On track"]).sum())}), include_groups=False)
by_type["delivery_rate"] = (by_type.completed / by_type.goals).round(2)
by_type.to_csv(DATA / "goal_delivery_by_type.csv")

# ---------- 2. RACI matrix ----------
ROLES = ["Commercial ops", "Sales", "Marketing", "Support", "Finance", "Product", "Operations", "CEO"]
PROC = {
    "Lead capture and routing": "R,C,A,I,-,-,-,-", "Lead scoring and lifecycle rules": "A,C,R,-,-,-,-,I", "Quote to order": "A,R,-,C,C,-,C,-",
    "Order to cash and invoicing": "R,I,-,C,A,-,C,-", "Pricing and discount approval": "R,C,-,-,C,C,-,A", "Channel partner onboarding": "A,R,C,-,C,I,C,I",
    "Forecast and budget": "R,C,C,-,A,-,C,I", "KPI pack and weekly report": "A,C,C,C,C,-,C,I", "Support ticket handling": "C,I,-,A,-,C,C,-",
    "Voice of customer to product": "R,C,C,C,-,A,-,I", "Event planning and return": "C,C,A,-,C,-,R,I", "Territory and quota": "R,C,-,-,C,-,-,A",
}
raci = pd.DataFrame({p: v.split(",") for p, v in PROC.items()}, index=ROLES).T
raci.index.name = "process"
raci.to_csv(DATA / "raci_matrix.csv")
bad = [p for p, row in raci.iterrows() if (row == "A").sum() != 1]     # rule: exactly one accountable per process
assert not bad, bad

# ---------- 3. KPI dictionary ----------
K = [
    ("Revenue", "Invoiced revenue in the period, net of credits", "Accounting system", "Finance", "Monthly", "CRM deal amounts are not used; they differ from invoices"),
    ("Orders", "Count of orders created, including no-charge orders, across all three pipelines", "Order system", "Commercial ops", "Weekly", "Order count, not order value"),
    ("Opportunities", "Count of deals created; a deal is one opportunity", "CRM", "Sales", "Weekly", "Count, not value"),
    ("Opportunities by stage", "Deals open at each stage on the report date", "CRM", "Sales", "Weekly", "Stage definitions from project 11"),
    ("Win rate", "Closed won divided by closed won plus closed lost, by cohort created", "CRM", "Commercial ops", "Monthly", "Excludes open deals"),
    ("Pipeline coverage", "Open pipeline value divided by next-quarter quota", "CRM", "Sales", "Weekly", "Target 3x"),
    ("Revenue by customer, region, product", "Invoiced revenue, month, quarter and year to date, highest first", "Accounting system", "Finance", "Monthly", "Table, not chart"),
    ("Contacts in CRM", "Contacts with owner, valid email and segment", "CRM", "Commercial ops", "Monthly", "Data-quality gate"),
    ("Website visitors", "Unique visitors in the period", "Web analytics", "Marketing", "Monthly", "Trend line"),
    ("Social followers", "Followers at month end", "Social platform", "Marketing", "Monthly", "Trend line"),
    ("First-response SLA met", "Tickets answered within target divided by tickets", "Service Hub", "Support", "Weekly", "Target 90%"),
    ("Cost per qualified lead", "Programme cost divided by qualified leads", "Finance and CRM", "Marketing", "Quarterly", "Event and campaign level"),
]
kd = pd.DataFrame(K, columns=["kpi", "definition", "source_of_truth", "owner", "cadence", "note"])
kd.to_csv(DATA / "kpi_dictionary.csv", index=False)

# ---------- 4. executive KPI pack: layout and delivery ----------
pack = pd.DataFrame([["Cumulative revenue by month and quarter", "Line", "Accounting"], ["Revenue by month", "Column", "Accounting"],
                     ["Revenue by customer, region, product", "Table", "Accounting"], ["Orders by month", "Column", "Order system"],
                     ["Opportunities by month", "Column", "CRM"], ["Sales funnel by stage", "Funnel", "CRM"],
                     ["Contacts, website visitors, followers", "Trend", "CRM, web, social"]], columns=["page", "visual", "source"])
pack.to_csv(DATA / "kpi_pack_layout.csv", index=False)
print(goals.status.value_counts()); print(by_type); print(raci.head(3))

plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
SC = {"Completed": TEAL, "On track": BLUE, "Under review": GOLD, "Not started": GREY, "Cancelled": RED}
fig, ax = plt.subplots(1, 3, figsize=(18, 5.6), gridspec_kw={"width_ratios": [1, 1.3, 1.5]})
fig.suptitle("Aurelis Life Sciences | Commercial operating system: goals, ownership, KPIs (synthetic data)", fontsize=12.5, weight="bold")
sc = status_counts.reindex(list(SC)).fillna(0)
ax[0].bar(sc.index, sc.values, color=[SC[s] for s in sc.index])
for i, v in enumerate(sc.values):
    ax[0].text(i, v + .2, int(v), ha="center", weight="bold")
ax[0].tick_params(axis="x", rotation=30)
ax[0].set(title=f"Goal status ({len(goals)} goals)", ylabel="goals")
bt = by_type.sort_values("goals")
ax[1].barh(bt.index, bt.goals, color=GREY, label="Goals")
ax[1].barh(bt.index, bt.completed, color=TEAL, label="Completed")
ax[1].legend()
ax[1].set(title="Delivery by goal type", xlabel="goals")
cmap = {"R": TEAL, "A": BLUE, "C": GOLD, "I": GREY, "-": "white"}
ax[2].axis("off")
tbl = ax[2].table(cellText=raci.values, rowLabels=raci.index, colLabels=ROLES, loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(7.5)
tbl.scale(1, 1.25)
for (r, c), cell in tbl.get_celld().items():
    if r > 0 and c >= 0:
        v = raci.values[r - 1][c]
        cell.set_facecolor(cmap[v] if v != "-" else "white")
        if v in ("R", "A"):
            cell.get_text().set_color("white")
ax[2].set_title("RACI: one Accountable per process (R responsible, A accountable, C consulted, I informed)", fontsize=9)
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "operating_system_dashboard.png", dpi=125)
print("done")
