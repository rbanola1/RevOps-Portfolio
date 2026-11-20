# Ticket intake and routing in seven boxes

```mermaid
flowchart LR
    I["Request arrives: email, web form, phone"] --> T["Ticket created"]
    T --> AI["AI triage"]
    AI -->|"confident"| R["Routed to the right owner"]
    AI -->|"unsure"| H["Human review"]
    H --> R
    AI -->|"spam"| S["Closed and suppressed"]
    R --> X["Reply in 24 hours, close in 72"]
    X --> Q["Satisfaction survey"]
    classDef a fill:#DCE8F7,stroke:#2B5C9E,color:#222
    classDef g fill:#CFE9E3,stroke:#2A9D8F,color:#222
    classDef y fill:#FBE5B6,stroke:#E9A23B,color:#222
    class I,T a
    class AI,H y
    class R,X,Q g
```

How to read it: every request becomes one ticket, the AI sorts it, a person reviews anything it is unsure about, and each ticket reaches one owner with a reply deadline.

Full detail with every connection: [ticket_intake_full_detail.md](ticket_intake_full_detail.md).
