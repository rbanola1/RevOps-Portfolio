# Marketplace onboarding

## Single source of truth
One **product master** holds every field for every SKU: name, size, price, lead time, classification codes, hazard data, packaging, storage. Platform feeds are generated from it.

## Per-platform steps
1. **Read the platform's own guidelines first**: unit-of-measure codes, text-length limits, classification-code length, image rules, hazard formats.
2. **Map master fields to platform fields**, applying the platform's format at export only. The master keeps the full detail.
3. **Generate the feed**, then run the **discrepancy check** against the master.
4. **Fix at the source**: correct the master, regenerate, never hand-edit a feed.
5. **Submit, then record** the file version and submission date.
6. **Re-sync** every platform when the master changes.

## Discrepancy check
For each SKU on each platform, compare against the master:
| Check | Flag when |
|---|---|
| SKU | Platform uses a different identifier for the same product |
| Price | Differs from the master list price |
| Classification code | Differs after applying the platform's code length |
| Lead time | Differs from the master |
| Size and unit | Same quantity expressed inconsistently |

The output is a report listing platform, SKU, issue, platform value and master value.

## Rules
- Fields owned by another team (customs and classification codes) are never changed here; discrepancies go to the owner.
- Use the newest file per platform only; archive older ones.
- Work platform by platform to keep changes traceable.
- Keep hazard and shipping flags consistent with safety documents.
- Status per platform: Outreach done, Ongoing onboarding, Live.
