# Purchase-order processing SOP

**Purpose:** turn a customer purchase order into a correct sales order and a confirmed shipment.
**Owner:** commercial operations. **Backup:** named deputy.

| Step | Action | Check |
|---|---|---|
| 1 | Open the order mailbox; assign each new message to yourself | One owner per message |
| 2 | Read the PO: customer, items, quantities, price, ship-to, bill-to, payment terms, tax status | All fields present; if not, reply with a short request |
| 3 | Find the customer in the ERP; create a new record only if none exists | No duplicates; customer ID matches the CRM |
| 4 | Create the sales order; attach the PO | Item numbers and prices match the price list |
| 5 | Check stock and lead time for each line | Backorders are flagged and agreed with the customer |
| 6 | Confirm tax status and shipping method | Exempt documents are on file; shipping per the shipping policy |
| 7 | Send the order acknowledgement | Includes expected ship date |
| 8 | Release to the warehouse; confirm pick, pack and ship | Tracking number recorded |
| 9 | Send the shipping notice | Tracking and invoice reference included |
| 10 | Close the email thread and mark the order complete | Mailbox shows no open item |

## Exceptions
| Case | Action |
|---|---|
| Price differs from the price list | Hold; ask the sales owner to approve or correct |
| New customer | Run the new-customer check before creating the record |
| Partial shipment | Ship available lines; confirm the rest with a new date |
| Cold-chain item | Check the shipping window before releasing |

## Records
Every order has the PO, the acknowledgement, the shipping notice and the invoice stored against the sales order.
