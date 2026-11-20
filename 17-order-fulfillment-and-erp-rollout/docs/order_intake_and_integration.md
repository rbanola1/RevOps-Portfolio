# Order intake and web-store integration

## Intake channels
| Channel | How it enters the ERP | Owner |
|---|---|---|
| Customer PO by email | Shared order mailbox, then manual sales-order entry by the SOP | Commercial operations |
| Web store | Automatic sales-order creation through the integration | Commercial operations |
| Distributor and marketplace orders | Entered from the partner's order file or portal export | Commercial operations |

## Email intake rules
- One shared mailbox for all orders, with a rule that assigns each message an owner.
- Standard subject line: customer, PO number, and "order".
- Auto-reply tells the customer what happens next and when to expect the acknowledgement.
- A message is complete only when an acknowledgement has been sent and a sales order exists.

## Web store and ERP integration
| Item | Rule |
|---|---|
| Orders | Store order creates a sales order with the same item numbers and prices |
| Customers | Matched by email; new customers created with a customer ID |
| Stock | ERP stock level updates the store at set intervals |
| Shipment | ERP shipment and tracking update the store order |
| Errors | Failed orders go to an exceptions list reviewed twice a day |

## Checks
- Daily count of store orders equals the count of ERP sales orders created from the store.
- Weekly review of the exceptions list and of orders with no shipment after the expected date.
- Item numbers and prices are maintained in one place (the ERP item master) and pushed to the store.
