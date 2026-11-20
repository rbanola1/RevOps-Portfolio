# Migration plan

| Step | Work | Done when |
|---|---|---|
| 1. Inventory | List objects, fields, workflows, integrations, reports and users in the legacy CRM | Inventory signed off by sales, marketing and finance |
| 2. Design | Decide match keys, picklists, required fields, owners and the property map from old to new | Mapping sheet approved |
| 3. Clean in staging | Dedupe, standardise, fill owners, remove junk, archive stale records | Quality score at target in staging |
| 4. Trial load | Load a copy into a sandbox; reconcile counts by object | Counts match; errors fixed |
| 5. Freeze and final load | Stop edits in the legacy system; load; reconcile | Counts match; missing records reloaded |
| 6. Verify | Sample-check 200 records across objects; test workflows, reports and integrations | No critical defects |
| 7. Cut over | Switch users and integrations; keep legacy read-only for 90 days | Users working; no data entered in legacy |
| 8. Stabilise | Monthly quality check; quarterly restore test; retire legacy | Legacy archived and access removed |

## Reconciliation checks
- Record counts by object: source minus duplicates minus junk equals loaded.
- Totals: deal value by owner and by stage, and number of contacts per company, compared old versus new.
- Associations: sample of contacts still linked to the right company and deals.
- History: sample of activities still on the right record with correct dates.

## Risks
| Risk | Control |
|---|---|
| Users keep editing the legacy system | Freeze date announced two weeks ahead; legacy set read-only |
| Associations break | Association checks and a sample review before cut-over |
| Reports differ from before | Side-by-side report comparison for two reporting cycles |
| Integrations push duplicate data | Integrations paused during load and restarted one at a time |
