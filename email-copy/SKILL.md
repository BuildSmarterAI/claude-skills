---
name: email-copy
description: Write cold outreach, nurture, lifecycle, and broadcast email copy - subject lines, preview text, openers, body, and single-action CTAs - with sequence architecture and per-send purpose. Use when drafting or rewriting marketing or sales email, not when triaging a mailbox or operating a send.
origin: BuildSmarter Copy OS
---

# Email Copy

Email lands in a space the reader controls, and they can end the relationship in one click. Where they opted in, every send spends a little of that permission. Where they did not - cold outreach - there is no permission to spend, only a lawful basis to establish and attention you have not been granted. Either way the copy has to be worth it.

## When to Activate

- Writing cold outreach, a nurture sequence, lifecycle email, or a broadcast.
- Subject lines and preview text.
- Designing a sequence: how many sends, what each one does, when to stop.
- Rewriting email that gets opened and not answered.

## When NOT to Activate

- Mailbox triage, drafting a personal reply, verifying what landed in Sent -> `email-ops`.
- List operations, deliverability infrastructure, DNS, warm-up.
- The wider outbound motion including targeting and data -> `cold-outreach-pipeline`.
- The landing page the email points at -> `landing-page-copy`.

## Inputs required

The Copy Brief, the relationship (cold, opted-in, customer, lapsed), the trigger for this send, the single action wanted, the sender identity, and the proof inventory. For cold email, also: how the recipient was identified, and the lawful basis for contacting them.

## Subject lines

The subject earns the open; nothing else in the email matters until it does.

- **Specific over clever.** A subject that says what is inside beats a subject that teases it, in every audience that has been burned by teasing - which is all of them.
- **Short, because of mobile.** Assume heavy truncation; front-load.
- **No fake reply prefixes.** No "RE:" or "FWD:" on a first contact. This is deceptive and destroys the relationship on open.
- **No manufactured urgency** in the subject. It is the fastest route to an unsubscribe.
- **Preview text is a second line, not a repeat.** Most senders waste it; use it to extend the subject.
- Write eight. Keep three. They should differ in angle: what-is-inside, the question, the outcome.

## Cold email

Cold email is a request from a stranger. The structure follows from that.

```
1  RELEVANCE      why this person, specifically - one line, verifiable
2  OBSERVATION    something true about their situation, not flattery
3  RELEVANCE-TO-THEM  what that means for them
4  ASK            one small, low-cost, specific ask
5  EXIT           a graceful way to say no
```

- **Under 120 words.** Length reads as presumption.
- **The personalisation must be real.** A merge field is not personalisation, and a wrong one is worse than none.
- **One ask.** Not "let me know your thoughts, or grab a time, or I can send more info."
- **The ask should be small.** A reply is smaller than a meeting. A question is smaller than a reply.
- **No fake familiarity.** No "circling back" on a first email, no "as discussed", no invented prior contact. This is both dishonest and instantly recognisable.
- **Give an exit.** "If this is not your area, I will leave it there" outperforms pressure and preserves the relationship.

## Nurture and lifecycle

Every send has one job. Name it before writing.

| Purpose | The send does | The CTA |
|---|---|---|
| Deliver | Gives the thing promised | Use it |
| Teach | One idea, useful whether or not they buy | Read or apply |
| Prove | One story or result, concretely | See the detail |
| Handle | Names one objection and answers it | Reconsider |
| Offer | Makes the ask directly | Buy or book |
| Reactivate | Acknowledges the silence honestly | Small re-entry step |

A sequence that is six offers is a sequence with a rising unsubscribe rate. A sequence that never asks is a newsletter.

**Sequence design:** state each send's purpose, its trigger, its delay, and its exit condition. Every sequence needs a stop - a rule that removes someone who has replied, converted, or gone cold.

## Body

- **First line does the work.** Preview text and the first line are often all that is seen. Never open with "I hope this email finds you well" or a paragraph about yourself.
- **Short paragraphs.** One to three lines. Email is read on phones, fast, in a queue.
- **One idea.** Two ideas means two emails.
- **Plain formatting.** Heavy design lowers the felt authenticity of a one-to-one message.
- **One CTA**, repeated at most twice, same wording both times.
- **Sign as a person.** A named human outperforms a brand for anything that wants a reply.

## Compliance essentials

Email is directly regulated, and the rules differ by jurisdiction. Verify the current regime for each market; treat these as items to check, not as settled law:

- The lawful basis for contacting this person (consent, legitimate interest, existing relationship) and whether it holds in their jurisdiction.
- Accurate sender identification and a real postal address where required.
- A working, honoured, one-step unsubscribe - including in cold outreach.
- Subject lines that are not deceptive.
- Suppression list honoured before every send.

Route anything uncertain to `compliance-review` and, for regulated categories, to a human.

## Output contract

```
SEQUENCE: <name>   RELATIONSHIP: <cold | opted-in | customer | lapsed>

SEND <n>  PURPOSE: <deliver | teach | prove | handle | offer | reactivate>
  Trigger:      <event or delay>
  Subject:      <3 variants, differing in angle>
  Preview:      <text>
  Body:         <text>
  CTA:          <one action>
  Claims:       <[FACT] source | [PROPOSED] | [NEEDS-INPUT]>
  Exit rule:    <what removes someone from the sequence here>

NOTES
  Word counts:  <per send>
  Compliance:   <lawful basis, unsubscribe, sender ID - verified | NEEDS-HUMAN>
  Stop rule:    <how the sequence ends>
```

## Quality gates

- Each send has one named purpose and one CTA.
- Cold emails are under 120 words with a real, verifiable relevance line.
- No fake reply prefix, no invented prior contact, no manufactured urgency.
- Subject variants differ in angle, not wording.
- Every claim traces to the proof inventory or is a `[NEEDS-INPUT]` slot.
- The sequence has a stop rule and an unsubscribe path.
- Personalisation slots are named inputs, never invented values.

## Failure conditions

- Cold outreach with no verifiable relevance available: say the personalisation cannot be written truthfully, and that a generic version will underperform and may harm the sender's domain.
- No lawful basis established for cold contact in the target jurisdiction: mark `NEEDS-HUMAN` before send.
- The offer needs a page that does not exist: write the sends and flag the destination gap.
- A request for a deceptive subject line or a fabricated prior conversation: decline that element, state why in a sentence, and deliver the rest.

## Handoffs

`copy-strategist` sets the argument · `persuasion-engine` picks the angle per send · `landing-page-copy` owns the destination · `copychief` reviews · `humanizer` before send · `compliance-review` for claims and regime · `email-ops` operates the actual send and verifies it landed.

## Provenance rule

Never invent a prior conversation, a mutual connection, a customer result, a company detail, or a statistic in order to personalise. Unverifiable personalisation is a `[NEEDS-INPUT]` slot. Full contract: `copy-os/references/fact-provenance.md`.
