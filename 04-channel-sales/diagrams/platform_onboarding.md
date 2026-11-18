# Platform onboarding and data QA

```mermaid
flowchart LR
    M[(Product master)] --> T1[Apply Marketplace A format]
    M --> T2[Apply Procurement B format]
    M --> T3[Apply Government C format]
    M --> T4[Apply Exchange D format]
    T1 --> F1[Feed A]
    T2 --> F2[Feed B]
    T3 --> F3[Feed C]
    T4 --> F4[Feed D]
    F1 --> Q{Discrepancy check against master}
    F2 --> Q
    F3 --> Q
    F4 --> Q
    Q -->|clean| S[Submit and log version]
    Q -->|issues| R[Report: platform, SKU, issue]
    R --> X[Fix master or ask the field owner]
    X --> M
```
