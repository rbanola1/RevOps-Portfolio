# Ticket-based routing

Inbound requests from shared inboxes and forms become tickets in a service system, which assigns an owner automatically.

| Request category | Primary owner | Secondary | Last resort | Ticket created |
|---|---|---|---|---|
| Product sales inquiries | Outside sales rep | Inside sales | Manager | Yes |
| Customer service and orders | Inside sales | Outside sales rep | Manager | Yes |
| Technical support and applications | Technical specialist | Outside sales rep | Inside sales | Yes |
| Custom development | Business development | Technical specialist | Outside sales rep | Yes |
| Therapeutics collaborations | Business development | Executive | Manager | Yes |
| General | Inside sales | Operations | Manager | Yes |
| Careers and investor inquiries | HR or finance leader | Executive | | No ticket, routed by email |

## Rules
- Each category has a primary, secondary and last-resort owner so nothing sits unowned.
- Tickets get a colour by category for quick triage.
- A catch-all inbox is checked by all reps periodically.
- Auto-assignment follows the lane criteria: inbound goes to inside sales, event and field leads to outside sales, specialised inquiries to business development.
- Loop and spam guardrails prevent auto-replies from creating runaway tickets.
