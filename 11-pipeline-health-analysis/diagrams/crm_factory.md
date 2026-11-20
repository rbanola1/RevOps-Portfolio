# The CRM as a factory

The problem was not bad material. Records were accurate and plentiful. The line simply did not use them: most sat unworked at the first stations, so the plant looked busy and shipped little.

## Before: material piles up unused

```mermaid
flowchart LR
    subgraph IN[Raw material in]
        S1[Trade shows]
        S2[Web forms]
        S3[Outbound lists]
        S4[Distributor referrals]
    end
    IN --> A[CRM intake: 4,000 records]
    A --> B[Touched once: 74%]
    B --> C[Worked with follow-up: 40%]
    C --> D[Qualified: 11%]
    D --> E[Deal created: 7%]
    E --> F[Won: 2%]
    A -.-> W1[(Never touched: 26%)]
    B -.-> W2[(Touched once, then idle: 34%)]
    W1 --- Z[Idle inventory: nobody owns it, nobody sees it]
    W2 --- Z
```

## After: every station has an owner, a clock and a report

```mermaid
flowchart LR
    A[Intake with source, fit score and owner] --> R{Route by fit and intent}
    R -->|High| H[Rep: contact in 1 day]
    R -->|Medium| N[Nurture sequence with a stop rule]
    R -->|Low| X[Hold and suppress]
    H --> Q[Qualified]
    N --> Q
    Q --> D[Deal with next step and date]
    D --> WON[Won]
    H -.->|no activity in 7 days| ALERT[Idle-inventory alert]
    D -.->|past stage benchmark| ALERT
    ALERT --> OWN[Owner acts or closes the record]
    OWN --> A
    WON --> REP[Weekly throughput and utilisation report]
```

## Factory measures used in the weekly report
| Factory term | CRM measure | Why it matters |
|---|---|---|
| Raw material | Records created by source | Shows where input comes from |
| Utilisation | Share of records touched and worked | The gap between input and use |
| Work in progress | Open deals by stage | Too much at one station means a bottleneck |
| Idle inventory | Records or deals with no activity past the benchmark | Material paid for and not used |
| Yield per station | Conversion from one stage to the next | Finds the weakest station |
| Cycle time | Days in each stage versus benchmark | Finds slow stations |
| Throughput | Deals won per month | The output that counts |
