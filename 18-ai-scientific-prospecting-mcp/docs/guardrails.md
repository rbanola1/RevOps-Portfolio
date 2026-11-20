# Guardrails for AI-assisted prospecting

| Rule | Why |
|---|---|
| The assistant reads the lead database; it never writes to the CRM or sends email | People stay accountable for every record and every message |
| Suppression check before any paid lookup | Credits go only to people nobody has contacted |
| Credit estimate and a 10-row test before any bulk run | Cost is known before it is spent |
| One stable Lead ID per person | Results from any tool map back to the right row |
| Scripts stop if a row changed since the upload | Manual edits are never overwritten |
| No lead is deleted by a merge; misses go to a separate list | Nothing disappears without a decision |
| Every email verified before import | Protects the sending domain |
| Every import tagged by lead source | Results can be compared by method and tool |
| One decision-maker per organisation, plus at most one escalation contact | Targeted outreach, not staff lists |
| Drafts are reviewed by a person before any send | Accuracy and tone stay human-checked |

## Signals and how they score
| Signal | Weight | Reason |
|---|---|---|
| New grant (last 12 months) | Highest | Funded work starting now |
| Clinical trial | High | Active programme with budget |
| Recent paper (last 6 months) | Medium-high | Active method user; corresponding author is reachable |
| New lab or new role | Medium | New setups buy tools |
| Conference poster | Medium | Early-stage work; warm topic for a first email |

Recency adds points: the newer the signal, the higher the score.
