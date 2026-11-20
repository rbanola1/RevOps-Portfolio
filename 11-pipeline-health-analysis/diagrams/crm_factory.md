# The CRM as a factory

The problem was not bad material. Records were accurate and plentiful, but most were never worked, so the plant looked busy and shipped little.

## Before: material piles up unused
```mermaid
flowchart LR
    A["4,000 records in"] --> B["74% touched once"] --> C["40% worked"] --> D["7% became deals"] --> E["2% won"]
    A -.-> W["Idle inventory: no owner, no alert"]
    classDef a fill:#DCE8F7,stroke:#2B5C9E,color:#222
    classDef g fill:#CFE9E3,stroke:#2A9D8F,color:#222
    classDef y fill:#FBE5B6,stroke:#E9A23B,color:#222
    class A,B,C,D a
    class E g
    class W y
```

## After: every station has an owner and a clock
```mermaid
flowchart LR
    A["Record in with an owner"] --> R["Routed by fit and intent"] --> W["Worked within a set time"] --> D["Deal with next step"] --> X["Won"]
    W -.->|"idle too long"| AL["Alert to owner"]
    AL -.-> W
    classDef a fill:#DCE8F7,stroke:#2B5C9E,color:#222
    classDef g fill:#CFE9E3,stroke:#2A9D8F,color:#222
    classDef y fill:#FBE5B6,stroke:#E9A23B,color:#222
    class A,R,W,D a
    class X g
    class AL y
```

Full detail with every connection: [crm_factory_full_detail.md](crm_factory_full_detail.md).

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
