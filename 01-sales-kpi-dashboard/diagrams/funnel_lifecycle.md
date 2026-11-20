# Funnel and lead lifecycle

```mermaid
flowchart LR
    L[Lead<br/>contact added] -->|combined score at MQL cut-off| M[MQL<br/>good fit, some interest]
    M -->|score at SQL cut-off or fit-checked hand-raise| S[SQL<br/>high fit and intent]
    S -->|deal created| O[Opportunity]
    O -->|closed won| C[Customer]
    O -->|closed lost| X[Lost]
    L -.->|score decays 20% per quarter| L
    X -.->|nurture| L
```

## Deal stages and forecast mapping

```mermaid
flowchart LR
    A[Discovery and Scoping<br/>PIPELINE 15%] --> B[Proposal / Quote Sent<br/>BEST CASE 30%]
    B --> C[Verbal Commit<br/>COMMIT 60%]
    C --> D[Closed Won<br/>100%]
    A --> E[Closed Lost]
    B --> E
    C --> E
```
