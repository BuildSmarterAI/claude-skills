---
name: persuasion-engine
description: Select and apply behavioral-science persuasion principles - anchoring, social proof, loss aversion, authority, scarcity, framing, contrast, commitment, reciprocity, defaults, risk reversal - matched to audience temperature and awareness, with hard guardrails against fabricated scarcity, authority, statistics, and testimonials. Use when deciding which persuasion angles a piece of copy should use, or when auditing copy for manipulative technique.
origin: BuildSmarter Copy OS
---

# Persuasion Engine

A menu of strategic tools, not a mandate. The job is to choose the two or three principles that fit this reader at this moment, apply them honestly, and name the ones you deliberately rejected.

Copy that stacks every principle reads as manipulation and converts worse than copy that picks two and earns them.

## When to Activate

- Choosing the persuasive angle for a page, sequence, ad, or offer.
- Copy is accurate and clear but does not move anyone.
- Auditing existing copy for manipulative or fabricated technique.
- Deciding how to present price, comparison, guarantee, or urgency.
- A campaign needs different angles for cold, warm, and hot audiences.

## When NOT to Activate

- The problem is wording, rhythm, or AI tells -> `humanizer` or `direct-response-copy`.
- The problem is the offer itself -> `copy-strategist`.
- The problem is whether a claim is legal or substantiated -> `compliance-review`.
- The reader is most-aware and waiting on terms. Say the terms.

## Inputs required

Audience temperature, awareness stage, what the reader already believes, the verified proof inventory, the offer terms, and the brand's forbidden techniques. Absent these, propose angles as `[PROPOSED]` and name what would confirm them.

## Selecting by temperature

Wrong-temperature persuasion actively repels. This table is the first filter.

| Temperature | Leads well with | Also works | Actively backfires |
|---|---|---|---|
| **Cold** - never heard of you | Specific concrete story, naming the problem | Framing, contrast, authority if genuinely earned | Social proof (no context), scarcity, commitment |
| **Warm** - comparing options | Social proof, anchoring, contrast | Authority, mechanism, framing | Scarcity (premature), fear (already aware) |
| **Hot** - deciding now | Loss aversion, risk reversal, real deadline | Social proof, defaults, cognitive ease | Long stories, re-establishing authority |
| **Lapsed** - bought before | Continuity, familiarity, reciprocity | Endowment, loss aversion, defaults | Fear, hard scarcity |
| **Skeptical** - thinks the category is hype | Verifiable specifics, peer proof, steelmanning the objection | Authority with credentials that check out | Confirmation pressure, scarcity, superlatives |

## The principles

Each entry: what it is, the honest form, the failure mode.

**Anchoring** - the first number sets the scale. Honest: a real reference price, a real cost of the status quo, a real alternative. Fails when the anchor is invented or is a price nobody has ever paid.

**Social proof** - people follow people like them. Honest: a specific number, a named person, a role, a measurable result - at least two of those. Fails as "thousands of happy customers", which the reader discounts to zero.

**Loss aversion** - losses weigh roughly twice gains. Honest: name a cost the reader is already paying. Fails when the loss is invented, or when fear is raised with no exit in the same breath. Every fear must be closed by a concrete, low-effort next step immediately.

**Authority** - credentials, track record, demonstrated competence. Honest: verifiable and relevant. Fails as borrowed authority, vague "industry-leading", or expertise in an adjacent field implied to cover this one.

**Scarcity and urgency** - real limits change behaviour. Honest: a genuine cap, a real deadline, a real capacity constraint - and it must be stated with its reason. Fails as a resetting countdown, permanent "only 3 left", or a deadline nothing enforces. This is the single most abused principle in marketing and the fastest way to lose a warm audience.

**Framing** - the same fact reads differently in different frames. Honest: choosing which true frame to lead with. Fails when the frame implies something the fact does not support.

**Contrast** - meaning comes from comparison. Honest: comparing against the real alternative, including doing nothing. Fails when the comparison misrepresents what the alternative actually offers.

**Commitment and consistency** - small yes leads to larger yes. Honest: a genuinely small first step with real value. Fails as a bait step whose only purpose is obligation.

**Reciprocity** - give first. Honest: something useful whether or not they buy. Fails when the gift is a gate.

**Decoy effect** - a third option makes a target option look right. Honest: three genuinely purchasable tiers. Fails when the decoy is unbuyable by design and the reader can tell.

**Default effect** - the pre-selected option wins. Honest: default to what most readers actually want. Fails as pre-ticked upsells, opt-out billing, dark patterns.

**Cognitive ease** - fluent copy feels truer. Honest: plain words, short sentences, clean layout. Fails when ease is bought by removing material terms.

**Specificity** - precise beats round. "Forty minutes" beats "faster". Honest: the real number. Fails, and fails badly, when precision is manufactured - a fake decimal reads as credible right up until someone checks.

**Risk reversal** - move the risk to the seller. Honest: a guarantee the business will actually honour, stated with its terms. Fails when conditions quietly make it unclaimable.

## Anti-patterns - hard stops

These are not stylistic preferences. Do not produce them, even when asked, even labelled as an example, even as a placeholder.

- **Fabricated scarcity** - countdowns that reset, invented inventory limits, deadlines nothing enforces.
- **Fabricated authority** - invented credentials, awards, certifications, press mentions, client logos.
- **Fabricated statistics** - any number without a source. Including plausible ones. Especially plausible ones.
- **Invented testimonials** - any quote attributed to a person who did not say it, including a composite or a "representative" customer.
- **False guarantees** - promising terms the business has not agreed to.
- **Deceptive urgency** - implying a consequence for delay that does not exist.
- **Manufactured precision** - decimals, percentages, or timeframes chosen because they sound researched.
- **Fear without an exit** - raising a threat with no concrete step in the same passage.
- **Comparative claims about competitors** without a verifiable, current source.
- **Sensitive-attribute targeting** - copy that segments or implies segmentation on race, religion, health, sexual orientation, immigration status, financial distress, or similar. Beyond the ethics, this is a policy violation on every major ad platform.

When a request asks for one of these, do not silently substitute a softer version. Say which principle was requested, why it is a hard stop, and offer the honest form: a real deadline instead of a fake one, a customer-quote slot instead of an invented quote, a mechanism instead of a statistic you do not have.

## Reasoning workflow

1. Read temperature and awareness from the brief.
2. Filter the menu by the temperature table. Discard the backfire column outright.
3. Pick **two or three** primary principles. More than three is stacking.
4. For each: check it against the proof inventory. A principle you cannot substantiate is not available to you.
5. Write the honest form of each into the copy at a named position.
6. Run the anti-pattern list against the draft.
7. Record the principles you rejected and why - that record is what stops the next pass from silently adding them back.

## Output contract

```
ANGLES
  Primary:    <principle> at <position> - honest form: <how>
  Primary:    <principle> at <position> - honest form: <how>
  Supporting: <principle> - <how>
REJECTED
  <principle> - <why: wrong temperature | unsubstantiated | brand forbids>
SUBSTANTIATION
  <principle> -> <[FACT] source | [NEEDS-INPUT] what is needed>
ANTI-PATTERN SCAN
  <clean | flagged: what and where>
```

## Quality gates

- Three principles or fewer are doing primary work.
- Every applied principle is substantiated or explicitly `[PROPOSED]`.
- The rejected list is non-empty. If nothing was rejected, the selection was not a selection.
- No item on the anti-pattern list appears anywhere in the draft.
- Every fear or loss framing has a concrete exit within the same passage.
- Urgency, if present, names the real reason for the deadline.

## Failure conditions

- The only persuasive angle available requires a fact nobody can substantiate. Report it as `[NEEDS-INPUT]`; do not manufacture the fact.
- The user insists on a fabricated scarcity, authority, statistic, or testimonial. Decline that element specifically, state why in one sentence, deliver the rest, and offer the honest alternative.
- The category is regulated and the angle depends on an outcome claim. Route to `compliance-review` before drafting.

## Handoffs

`copy-strategist` supplies temperature and proof · `direct-response-copy` and the channel skills apply the angles · `copychief` scores whether they landed · `compliance-review` clears substantiation.

## Provenance rule

Never invent proof, customers, results, pricing, guarantees, competitor claims, or credentials. Facts come from repo-local context, supplied files, or the user. Label every assertion `[FACT]`, `[PROPOSED]`, or `[NEEDS-INPUT]`. Full contract: `copy-os/references/fact-provenance.md`.
