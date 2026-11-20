# 02 | CRM Cleanup, Segmentation and Lead Scoring

**Fictional company:** RB Tech · **All data is synthetic**

![Cleanup overview](charts/cleanup_overview.png)

## At a glance
```mermaid
flowchart LR
    A["Full marketing tier, messy industry field, engagement-only score"] --> B["Audit, demote, promote and one clean segment field"] --> C["Tier 94% to 58%, classified contacts 55% to 88%"]
    classDef p fill:#EEF0F3,stroke:#9AA5B1,color:#222
    classDef b fill:#DCE8F7,stroke:#2B5C9E,color:#222
    classDef r fill:#CFE9E3,stroke:#2A9D8F,color:#222
    class A p
    class B b
    class C r
```

## The problem
The CRM had grown through bulk list imports. The marketing-contact tier was close to its paid limit, three out of four contacts had never opened a marketing email, nearly half had no industry, and the industry field held many overlapping values with no way to report by market. Lead score measured engagement only, so it could not tell a real buyer from a curious bystander. There was no room to nurture good leads because the tier was full of dead weight.

## What I built
Four connected pieces, each with written rules so the work is repeatable and explainable.

| Piece | What it does |
|---|---|
| **Marketing-tier audit and cleanup** | Finds contacts that cost money but never engage and moves them to non-marketing, without deleting anything |
| **Promotion list** | Finds non-marketing contacts who engaged with sales email and promotes them, holding EU/UK/CH contacts for a consent check |
| **Segment field** | Replaces a messy industry picklist with one clean Segment field using 10 market segments, filled from a mapping table and then job-title rules |
| **Engagement score with decay** | The starting point: scores replies, sales clicks and opens, decaying 20% per quarter so old activity stops counting. Its limits, and the replacement that adds fit and intent, are covered in [GTM-Strategy 02](https://github.com/rbanola1/GTM-Strategy/tree/main/02-lead-scoring-redesign) |

## Results on the synthetic CRM (60,000 contacts)
| Metric | Before | After |
|---|---|---|
| Marketing-contact tier (limit 50,000) | 47,190 (94%) | 28,913 (58%) |
| Contacts demoted to non-marketing | | 18,337 |
| Engaged contacts promoted | | 60 (plus 21 held for EU/UK/CH consent check) |
| Duplicates merged | | 77 |
| Contacts with a usable industry or segment | 55% | 88% |
| Distinct industry values | 18 | 10 segments |

The numbers are simulated. The design is the point: rules first, a reversible change log second, and nothing deleted.

## Principles
1. **Rules before action.** Every demotion and promotion follows a written rule that a colleague can audit.
2. **Reversible.** Contacts move between marketing and non-marketing; nothing is deleted. The change log lists every record touched.
3. **Protect what matters.** Customers, open deals, target personas, recent contacts and anyone added by a person on purpose are never demoted.
4. **Consent first.** EU, UK and Swiss contacts are never promoted automatically.
5. **Fix the cause.** Entry rules decide who may become a marketing contact in future, so the tier does not refill with imports.

## Documents and diagrams
- [docs/cleanup_rules.md](docs/cleanup_rules.md): demote, promote, protect and entry rules
- [docs/segmentation_model.md](docs/segmentation_model.md): the 10 segments, mapping table and title fallbacks
- [docs/lifecycle_and_scoring.md](docs/lifecycle_and_scoring.md): lifecycle stages, score weights and decay
- [diagrams/cleanup_process.md](diagrams/cleanup_process.md): audit to change log
- [diagrams/segmentation_flow.md](diagrams/segmentation_flow.md): messy industry to clean segment
- [diagrams/governance.md](diagrams/governance.md): who may enter and leave the marketing tier

## Reproduce
```bash
pip install pandas numpy matplotlib
python scripts/crm_cleanup.py     # writes data/*.csv and charts/cleanup_overview.png
```

| File | What it is |
|---|---|
| `data/contacts_sample.csv` | 1,000-contact sample with action, segment, segment source, score (the script writes the full 60,000 to `contacts_cleaned.csv`) |
| `data/change_log_sample.csv` | 500-row sample of the change log (the full log is `change_log.csv`) |
| `data/industry_to_segment_map.csv` | The mapping table |
| `data/kpi_summary.csv` | Headline numbers above |

## Skills shown
CRM data governance · database audit and hygiene · segmentation design · lead scoring and lifecycle design · consent-aware marketing operations · change control · Python data work
