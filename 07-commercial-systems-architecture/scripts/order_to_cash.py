"""Synthetic order-to-cash integration model for Aurelis Life Sciences (fictional).

Simulates 1,500 orders flowing CRM -> online store -> ERP -> accounting -> BI, with integration
exceptions injected, so the effect of automation and the reconciliation method can be shown.
All data invented. Run: python scripts/order_to_cash.py
Needs: pandas, numpy, matplotlib
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
rng = np.random.default_rng(99)

N = 1500
start = pd.Timestamp("2026-01-05")
orders = pd.DataFrame({
    "order_id": [f"SO-{20000 + i}" for i in range(N)],
    "created": start + pd.to_timedelta(rng.integers(0, 330, N), unit="D"),
    "channel": rng.choice(["Web store", "Rep quote"], N, p=[.62, .38]),
    "customer_type": rng.choice(["Academic", "Commercial", "Tax-exempt institution"], N, p=[.45, .35, .20]),
    "amount": rng.choice([100, 199, 270, 600, 750, 1200, 2400], N, p=[.2, .2, .1, .2, .15, .1, .05]).astype(float),
})
# phase: before integration (manual re-keying) vs after (automated syncs) at a go-live date
GO_LIVE = pd.Timestamp("2026-06-15")
orders["phase"] = np.where(orders.created < GO_LIVE, "Manual", "Integrated")
manual = orders.phase == "Manual"

# lead times in days between stages; automation removes re-keying delay
def lag(mean_manual, mean_auto, sd):
    return np.clip(np.where(manual, rng.normal(mean_manual, sd, N), rng.normal(mean_auto, sd * .5, N)), 0.1, None)
orders["days_won_to_erp"] = lag(1.8, 0.3, 0.8)
orders["days_erp_to_ship"] = lag(3.0, 2.6, 1.0)
orders["days_ship_to_invoice"] = lag(3.0, 1.5, 1.2)
orders["days_won_to_invoice"] = orders[["days_won_to_erp", "days_erp_to_ship", "days_ship_to_invoice"]].sum(axis=1)

# integration exceptions: what goes wrong, by phase
EX = {"Product ID missing or mismatched": (.060, .012),
      "Tax-exempt flag not carried over": (.045, .008),
      "Duplicate customer record": (.050, .015),
      "Amount differs between systems": (.035, .006),
      "Order stuck in sync queue": (.020, .010)}
rows = []
for name, (p_manual, p_auto) in EX.items():
    p = np.where(manual, p_manual, p_auto)
    hit = rng.random(N) < p
    rows.append(pd.DataFrame({"order_id": orders.order_id[hit], "exception": name,
                              "phase": orders.phase[hit]}))
exc = pd.concat(rows, ignore_index=True)
exc.to_csv(DATA / "exceptions.csv", index=False)
orders["has_exception"] = orders.order_id.isin(exc.order_id)

# three-way reconciliation: CRM won amount vs ERP order vs accounting invoice, by month
orders["month"] = orders.created.dt.to_period("M").astype(str)
orders["crm_amount"] = orders.amount
amt_bad = orders.order_id.isin(exc[exc.exception == "Amount differs between systems"].order_id)
orders["invoice_amount"] = np.where(amt_bad, (orders.amount * rng.uniform(.9, 1.1, N)).round(2), orders.amount)
rec = orders.groupby("month").agg(crm=("crm_amount", "sum"), invoiced=("invoice_amount", "sum"),
                                  orders=("order_id", "count"),
                                  exception_rate=("has_exception", "mean")).reset_index()
rec["gap"] = (rec.invoiced - rec.crm).round(2)
rec["gap_pct"] = (rec.gap / rec.crm).round(4)
rec.round(3).to_csv(DATA / "monthly_reconciliation.csv", index=False)
orders.to_csv(DATA / "orders.csv", index=False)

# integration inventory (the architecture as data)
inv = pd.DataFrame([
    ("Lead sources and verifier", "CRM", "Verified contacts with lead source tag", "Reviewed import", "Email and name after suppression check", "Live"),
    ("CRM", "BI dashboards", "All objects, read only", "CRM to BI", "Object IDs", "Live"),
    ("Product data hub", "CRM", "Products", "Hub to CRM, about 1 minute", "Product ID", "Live"),
    ("Product data hub", "CRM", "Tax-exempt documents (backup)", "Hub to CRM", "Company ID", "Live"),
    ("Product data hub", "Online store", "Product data", "Hub to store, about 5 minutes", "Product ID", "Live"),
    ("Online store", "ERP", "Web orders", "Store to ERP", "Order ID with field mapping", "Live"),
    ("Order desk (templates)", "ERP", "Marketplace purchase orders and distributor orders", "Manual entry from approved template", "PO number", "Live"),
    ("ERP", "Accounting", "Orders for invoice generation", "ERP to accounting", "Order number", "Live"),
    ("Accounting", "CRM", "Invoice status and paid date", "Accounting to CRM", "Order number", "Live"),
    ("CRM", "Accounting", "Product sync", "Off", "SKU", "Off by design"),
    ("Accounting", "CRM", "Contact sync", "Off", "Email", "Off by design"),
    ("Online store", "CRM", "Product sync", "Off", "Product ID", "Off by design"),
], columns=["from_system", "to_system", "data", "direction", "match_key", "status"])
inv.to_csv(DATA / "integration_inventory.csv", index=False)

kpi = {
    "orders": N,
    "avg_days_won_to_invoice_manual": round(orders[manual].days_won_to_invoice.mean(), 1),
    "avg_days_won_to_invoice_integrated": round(orders[~manual].days_won_to_invoice.mean(), 1),
    "cycle_reduction_pct": round(1 - orders[~manual].days_won_to_invoice.mean()
                                 / orders[manual].days_won_to_invoice.mean(), 3),
    "orders_with_exception_manual": round(orders[manual].has_exception.mean(), 3),
    "orders_with_exception_integrated": round(orders[~manual].has_exception.mean(), 3),
}
pd.Series(kpi).to_csv(DATA / "kpi_summary.csv", header=["value"])
print(pd.Series(kpi).to_string())
print(exc.groupby(["exception", "phase"]).size().unstack(fill_value=0).to_string())

# ---------------- charts ----------------
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, TEAL, GOLD, RED, GREY = "#2B5C9E", "#2A9D8F", "#E9A23B", "#D1495B", "#9AA5B1"
fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
fig.suptitle("Aurelis Life Sciences | Order-to-cash integration (synthetic data)", fontsize=13, weight="bold")
st = inv.status.value_counts()
ax[0].barh(st.index[::-1], st.values[::-1], color=[GREY, TEAL][: len(st)][::-1])
ax[0].set(title="Integration inventory by status", xlabel="connections")
stages = ["days_won_to_erp", "days_erp_to_ship", "days_ship_to_invoice"]
lab = ["Won to ERP", "ERP to ship", "Ship to invoice"]
m = orders.groupby("phase")[stages].mean().loc[["Manual", "Integrated"]]
bottom = np.zeros(2)
for s, l, c in zip(stages, lab, [BLUE, TEAL, GOLD]):
    ax[1].bar(m.index, m[s], bottom=bottom, label=l, color=c)
    bottom += m[s].values
ax[1].legend(fontsize=8)
ax[1].set(title=f"Days from deal won to invoice (-{kpi['cycle_reduction_pct']:.0%})", ylabel="days")
e = exc.groupby(["exception", "phase"]).size().unstack(fill_value=0)
e = e.reindex(columns=["Manual", "Integrated"]).fillna(0)
y = np.arange(len(e))
ax[2].barh(y + .2, e.Manual, .4, color=RED, label="Manual")
ax[2].barh(y - .2, e.Integrated, .4, color=TEAL, label="Integrated")
ax[2].set_yticks(y, [t.replace(" or ", "/") for t in e.index])
ax[2].legend(fontsize=8)
ax[2].set(title="Exceptions by type", xlabel="orders")
ax[3].bar(rec.month.str[-2:], rec.exception_rate * 100, color=np.where(rec.month < "2026-06", RED, TEAL))
ax[3].axvline(4.5, color="k", ls="--", lw=.7)
ax[3].text(4.6, ax[3].get_ylim()[1] * .9, "go-live", fontsize=8)
ax[3].set(title="Exception rate by month (%)", ylabel="%")
fig.tight_layout(rect=[0, 0, 1, .93])
fig.savefig(CHARTS / "architecture_overview.png", dpi=130)
print("done")
