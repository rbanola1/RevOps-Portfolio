# Decision log

| # | Idea | Decision | Reason |
|---|---|---|---|
| 1 | Four separate pipelines (non-revenue, outside, inside, therapeutics and distributor) | Rejected | Easier handling of deals but more training, and one account could have deals in several pipelines. Kept a simpler structure with an owner field and a deal category |
| 2 | Make contact, deal and company owner mandatory | Adopted | Every record needs a clear owner |
| 3 | Link every deal to both company and contact | Adopted | Enables reporting and prevents orphan deals |
| 4 | Parent and child accounts | Adopted selectively | Prevents clashes across divisions, but harder to maintain, so used where needed |
| 5 | Association labels for contacts | Adopted | Clarifies roles; reduced to a short consistent set |
| 6 | Workflow alert when a deal is created in another rep's company | Adopted | Early overlap warning |
| 7 | Conference leads default to outside sales manager | Adopted | Avoids trade-show ownership disputes |
| 8 | Inside nurtures, then hands off to outside | Adopted | Matches sales-cycle and deal-size criteria |
| 9 | Separate dashboards for inside, outside, BD and distributor sales | Under review | Needs a deal-level category rather than contact-level fields |
