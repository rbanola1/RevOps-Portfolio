# The CRM as a factory

The problem was not bad material. The CRM held plenty of good records, but most of them were lying on the floor: never touched, or touched once, and then left. Few ever reached the conveyor.

## Before: material on the floor
```mermaid
flowchart LR
    IN["1,600 records in"] --> FL["On the floor<br>60% have 0 or 1 touch<br>85% have 3 or fewer; average 2.8"]
    IN --> W["Worked<br>40%"]
    W --> Q["Qualified 11%"] --> D["Deals 6%"] --> X["Won 2%"]
    FL -.->|"no owner, no alert, no touch target"| LOST["Bought, never used"]
    classDef a fill:#DCE8F7,stroke:#2B5C9E,color:#222
    classDef g fill:#CFE9E3,stroke:#2A9D8F,color:#222
    classDef r fill:#F4C7CE,stroke:#D1495B,color:#222
    class IN,W,Q,D a
    class X g
    class FL,LOST r
```

## After: nothing stays on the floor
```mermaid
flowchart LR
    A["Record in with an owner"] --> R["Routed by fit and intent"] --> W["Touch plan: 6 or more touches in a set time"] --> D["Deal with next step"] --> X["Won"]
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
