# System map: lead to cash in seven boxes

```mermaid
flowchart LR
    L["Find leads"] --> C["CRM: customers and deals"]
    P["Product data: one master"] --> C
    C --> CH["Channels: store, marketplaces, distributors"]
    CH --> E["ERP: orders and shipping"]
    E --> A["Accounting: invoices"]
    A -->|"invoice status"| C
    C -->|"read only"| B["Dashboards"]
    classDef a fill:#DCE8F7,stroke:#2B5C9E,color:#222
    classDef g fill:#CFE9E3,stroke:#2A9D8F,color:#222
    classDef y fill:#FBE5B6,stroke:#E9A23B,color:#222
    class L,P a
    class C,CH,E,A g
    class B y
```

How to read it: customer and product data meet in the CRM, orders flow to the ERP and accounting, and invoice status flows back to the CRM so one reporting layer shows everything. Each arrow has one owner and one direction.

Full detail with every connection: [system_map_full_detail.md](system_map_full_detail.md).
