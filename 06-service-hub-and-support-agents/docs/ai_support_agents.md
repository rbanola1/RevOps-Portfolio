# AI support agents

## Roles
| Agent | Job | Human control |
|---|---|---|
| **Triage agent** | Reads each new ticket, assigns the inquiry category and product group, flags spam | Confident results are routed automatically; low confidence goes to a review queue |
| **Reply-drafting agent** | Drafts a first response from approved scripts and product documents | A person reviews and sends |
| **Spam agent** | Closes obvious spam and adds the sender to a suppression list | Weekly sample check |
| **Weekly monitoring agent** | Reviews ticket activity for loops, spikes and unanswered tickets | Report to the team lead, dry run first |

## Triage design
- Classify into the same categories used for human routing.
- Return a confidence score; set a threshold (here 70%).
- Above the threshold: route to the category owner and apply tags. Below: human review queue.
- Always log the agent's decision and confidence so accuracy can be audited.

## Synthetic results (2,400 tickets)
| Metric | Value |
|---|---|
| Share routed automatically | 92% |
| Accuracy of automatically routed tickets | 99% |
| Accuracy on the review queue before a human | 35% (which is why it goes to a human) |
| Spam caught | 96% |

## Guardrails
1. Agents never send external replies without a human, except fixed acknowledgements protected by loop rules.
2. No refund, replacement or pricing decisions by an agent.
3. Run any new agent as a dry run that reports what it would do.
4. Keep cost under control: scheduled weekly checks rather than constant polling.
5. Review misrouted tickets monthly and update the keyword and example set.
6. Keep personal and sensitive data out of prompts.
