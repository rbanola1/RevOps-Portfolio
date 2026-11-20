# Workflow

## Who does what

```mermaid
sequenceDiagram
    actor Analyst
    participant AI as AI assistant (Claude)
    participant DB as Lead database (over MCP)
    participant PY as Python scripts
    participant CRM as CRM
    Analyst->>AI: Persona, product fit, signals wanted
    AI->>DB: Search, filter fields, refine
    DB-->>AI: Researchers with grants, papers, trials, posters
    AI->>PY: Candidate file
    PY->>PY: Suppression check against the CRM export
    AI->>DB: Researcher intel for net-new leads
    AI-->>PY: Why-now note per lead
    PY->>PY: Fit score and tiers A / B / C
    PY->>DB: Upload of leads missing an email (stable Lead ID)
    DB-->>PY: Emails returned
    PY->>PY: Merge by Lead ID, verify, list what is still missing
    AI-->>Analyst: Draft first emails for tier A / B
    Analyst->>CRM: Reviewed import with lead-source tag
    CRM-->>Analyst: Replies and meetings for measurement
```

## Email gap-fill and bulk update

```mermaid
flowchart TB
    M[(Master lead files)] --> U[Upload file: every lead with no email<br>or an email to verify, keyed by Lead ID]
    U --> D[Lead database lookup]
    D --> R[Results file]
    R --> MAP{Match on Lead ID?}
    MAP -->|yes| CHK{Row unchanged<br>since upload?}
    MAP -->|no: unique name match| CHK
    MAP -->|no match| X[Report as unmatched]
    CHK -->|yes| W[Write email in place<br>status = Ready, keep manual edits]
    CHK -->|no| STOP[Stop and review]
    W --> V[Verification]
    M --> MISS[Missing-email list:<br>every lead still without an email]
```

No lead is removed by the merge. An old unverified email that the database cannot confirm is cleared, and the lead moves to the missing list.
