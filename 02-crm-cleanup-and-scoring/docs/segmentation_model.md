# Segmentation model

## Why
The industry picklist had overlapping values (for example Biotechnology, Biotech Research and Life Sciences) and a large blank share, so reporting by market was unreliable. A single **Segment** field gives every report and every campaign one shared vocabulary.

## The 10 segments
Pharma · Biotech · Academia · CRO · CGT Developer · Hospital · Core Facility · Nonprofit Foundation · Government · Distributor

## Fill order
1. **Map from industry.** A mapping table converts each raw industry value to one segment (see `data/industry_to_segment_map.csv`).
2. **Infer from job title** when industry is blank, using keyword rules such as professor or postdoc to Academia, cell therapy to CGT Developer, procurement to the company's segment.
3. **Leave Unclassified** rather than guess when neither works. These go to a review list.

## Rules
- Segment is set per company and inherited by contacts, so the same company never carries two segments.
- Every segment value records its source (mapped, inferred, manual) so confidence is visible.
- Changes need sign-off from the teams who use the field (sales, marketing).
- Do the enrichment as one import, then keep it current through form fields and entry rules.
