# Backup and restore

| Asset | Backup method and frequency | Location | Retention | Restore test |
|---|---|---|---|---|
| CRM objects (companies, contacts, deals, tickets) | Weekly full export plus daily change export | Cloud storage with versioning | 90 days daily, 3 years monthly | Quarterly restore test |
| Activity history (emails, calls, notes) | Monthly export | Cloud storage | 3 years | Annual sample check |
| Property definitions and workflows | On every change; monthly full copy | Version-controlled documentation | Indefinitely | Compared at each release |
| Reports and dashboards (BI model) | On every release | Version-controlled file store | Last 10 versions | Opened and refreshed quarterly |
| Integration settings and mappings | On every change | Documentation repository | Indefinitely | Reviewed each quarter |

## Rules
- Backups are stored outside the CRM and outside any one person's account.
- Access to backups is limited to two named people and the IT administrator.
- Credentials and secrets are never stored in backups or documentation; they live in the company password manager.
- Each restore test records the time to restore and any gaps; the target is a working CRM within one business day.
- A named backup owner and a named deputy are recorded so the routine survives staff changes.
