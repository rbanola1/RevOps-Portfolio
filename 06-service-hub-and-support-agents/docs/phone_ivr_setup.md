# Phone system and menu (IVR) setup

Fictional numbers shown. Teams using the phone system: sales, customer service, technical support, main reception.

## Menu design
One public main line with an automated menu:

| Key | Destination | Direct number (fictional) | Who answers |
|---|---|---|---|
| Main line | Menu | +1 555 0100 | - |
| 1 | Main reception | +1 555 0101 | Receptionist |
| 2 | Sales | +1 555 0102 | Sales lead (reassigns to the territory owner) |
| 3 | Customer service | +1 555 0103 | Commercial operations |
| 4 | Technical support | +1 555 0104 | Technical specialist |

Only the main line is public. Other numbers are internal, except where used on marketing material.

## Seats and ringing
- Seats are assigned to the people who answer each line; only seat holders can place outbound calls from the company numbers.
- Working hours for ringing: Monday to Friday, 8 am to 4 pm (after-hours optional, mainly sales).
- Each user chooses how calls ring: mobile app or the browser call window (calls ring only while the window is open).

## Availability
- Sales and reception set availability in the inbox; customer service and technical support set it in the help desk.
- Only available users receive routed calls.
- Calendar sync marks users unavailable for meetings and time off, so calls go to voicemail or another user.
- If someone turns availability off by hand, they turn it back on, or it stays off.

## Notifications
Enable: tickets (not "unassigned" tickets), calling, chat and email conversations (not "new unassigned"), and custom workflow notifications. Mobile app notifications on for the same items.

## Call routing and ownership
- Calls are assigned to whoever answers.
- Unassigned calls are reviewed daily and assigned to a person and a department; this is essential for reporting and follow-up.
- Sales calls go to the sales lead until the team grows, then by territory.
- Customer service and technical support calls create a ticket automatically, assigned round-robin.
- Menu key presses cannot be used as filters in the call log, and missed menu calls may appear only under the main line. Mitigation: a recipient reviews call details, assigns department and team member, listens to voicemails, and returns calls with no voicemail; a named owner and a back-up check "all calls" for unassigned items.

## Call log views
Create a team view with filters: "to number" is the team number, or "assigned to" is me, or "department" is mine. Columns: call title, department, assigned to, voicemail available, call result, notes, activity date. Use notes rather than comments so they appear on the contact.
Call result: completed or follow-up.

## Outbound calls
From the browser call window: search a contact or enter a number, choose the line to call from (for example technical support), and confirm the browser as the calling method. Mobile has no dialer; call from the contact record.

## Daily routine
Review and reassign unassigned calls, keep availability current, clear voicemails, add notes and a result to each call.
