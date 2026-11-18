# Ownership model

```mermaid
flowchart TD
    P[Parent account<br/>owner set] --> C1[Child account: division A<br/>owner set]
    P --> C2[Child account: division B<br/>owner set]
    C1 --> K1[Contact: decision maker]
    C1 --> K2[Contact: end user]
    C2 --> K3[Contact: procurement]
    K1 --> D1[Deal<br/>owner set]
    K2 --> D1
    K3 --> D2[Deal<br/>owner set]
    C1 --> D1
    C2 --> D2
```

Every deal is linked to both its company and a relevant contact. Every record has an owner. Child accounts roll up to the parent, so a new division of an existing customer is visible to the parent owner immediately.
