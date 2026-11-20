# Ticket rules and phone setup details

## Ticket fields and closing rules
- **Required before a ticket leaves New:** ticket owner, inquiry category, ticket category, refund or replacement (or N/A), product group and item.
- **Required to close:** product performance issue (yes or no).
- **Inquiry category vs ticket category:** the inquiry category is the main category (it sets the ticket tag and who is alerted); the ticket category is the internal reporting category.
- **Closing a ticket that needs no action** (automated notices, bounces, spam): inquiry category General (or Spam), ticket category N/A (or Spam), product group N/A, refund or replacement N/A, product performance issue No.
- **Marking spam, every time:** set ticket category to Spam, inquiry category to Spam and owner to the spam mailbox. Filtering on those lets the team compute total inbound enquiries against spam, so lead volume is reported cleanly.
- **Use notes, not comments,** for each interaction so the timeline stays clean.
- **Do not bulk-close tickets.** Delete junk tickets instead, because closing sends the survey email.
- **Conference feedback** goes to the voice-of-customer owner for entry in the VOC pipeline, not into the support pipeline.
- **Status flips automatically:** "Waiting on Contact" after we reply, "Waiting on Us" when they reply. If we replied but still owe a follow-up, switch back to "Waiting on Us" by hand.

## Phone setup per user
| Step | Detail |
|---|---|
| Call hours and ringing | Weekday 8 to 4 call hours; ring on the mobile app when on the go, or in the browser with the call window open at a desk |
| Calendar sync | Calendar and out-of-office sync on, so availability updates automatically and calls go to voicemail or another user |
| Notifications | Enable tickets, calling, chat and email conversations, and workflow notifications; do not enable the "unassigned" variants; mirror the settings in the mobile app; never disable required call, voicemail or assignment notifications |
| Availability | Sales and reception set availability in the inbox; customer service and technical support set it in the help desk. Only available users get routed calls, and tickets are not assigned to a user marked unavailable |

## Call log views
Each team has a saved "[Team] Call Log" view in the calls object, filtered by the team's number, by "activity assigned to" the user, or by department, with these columns: call title, department, activity assigned to, voicemail available, call result, call notes, activity date. Desktop is recommended; mobile is for quick checks only.

## Known limitation and how it is handled
The CRM assigns a call only when it is answered, and a menu key press cannot be used as a filter, so missed menu calls may show only under the main line.
1. The person who gets the call notification reviews the call.
2. Check the "all calls" view for unassigned calls or calls with no department.
3. Voicemail left: assign the correct department and team member.
4. No voicemail: return the call to confirm the reason, then assign.
5. Everyone checks "all calls" regularly; one person has primary responsibility and one a backup.

Assigning department and person is what makes call reporting and follow-up work.

## Call results, outbound calls and misrouted calls
- Use the call notes column (notes sync to the contact; notes are preferred over comments) and record the call result as completed or follow-up.
- Only seat holders can call from the CRM: from the browser dialer, choosing the line to call from; on the mobile app, calls start from a contact, company or pending call task. Outbound calls use the company's general number so caller ID stays consistent.
- Accounts-receivable and HR calls that reach the sales line are redirected to the accounting or HR mailbox instead of being handled there.
