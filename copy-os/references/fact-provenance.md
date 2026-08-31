# Fact Provenance and Contamination Rules

Global copy skills carry methodology. They carry **no facts about any business**. This file is the enforcement.

## The failure this prevents

A global skill used in repo A learns, or appears to learn, that "the guarantee is 30 days." Used later in repo B, it writes "30-day guarantee" into copy for a different company that has no guarantee at all. The copy reads well, ships, and is false. Nothing in the output looked wrong.

The defence is not memory hygiene. It is that **no skill in this family may state a business fact it cannot point at a source for**.

## Three labels, applied to every assertion

| Label | Means | Requires |
|---|---|---|
| `[FACT]` | Sourced from repo-local context, a file the user supplied, or a statement the user made in this conversation | A citation: file path, URL, or "user stated" |
| `[PROPOSED]` | Messaging under recommendation. True only if the business decides to make it true | Nothing, but it must be visibly labelled |
| `[NEEDS-INPUT]` | The copy needs this and you do not have it | A named input and, where possible, who holds it |

In final deliverables, keep the labels in the notes block, not inside the copy itself. The copy ships clean; the provenance ships beside it.

## Never invent

Not as a placeholder, not as an example, not to show the shape, not with a disclaimer:

- Customer names, quotes, testimonials, case studies, logos
- Performance results, conversion rates, ROI figures, growth numbers, time savings
- Headcounts, revenue, funding, founding dates, locations, years in business
- Certifications, licences, insurance, bonding, awards, memberships, rankings
- Pricing, discounts, terms, guarantees, trial lengths, refund windows
- Competitor claims, competitor pricing, competitor weaknesses
- Review counts, star ratings, "trusted by N teams"
- Regulatory status, compliance attainments, security attestations
- Anything attributed to a named third party

If a template genuinely needs to show shape, write the slot, not a value. Correct: `[NEEDS-INPUT: customer quote - named, with role and measurable result]`. Wrong: a realistic-looking quote from an invented person. A fabricated example survives copy-paste; a bracketed slot does not.

## Never assume

- **Positioning.** A repo's code tells you what the product does, not what the business claims to be. Read the marketing docs or ask.
- **Pricing model.** Seat-based, usage-based, project-based - do not infer it from a database schema.
- **Legal permission.** You cannot know what a business is allowed to claim. Where a claim is regulated, route it to a human.
- **Audience.** A construction product is not automatically sold to contractors; it may be sold to owners, lenders, or municipalities.
- **Tone.** Absent a voice profile, default to plain and specific, not to enthusiasm.
- **Territory.** Claims legal in one jurisdiction are not legal in all of them.

## Cross-repository hygiene

- Facts learned in one repository do not travel to another. If you know something about a business and cannot point at a source *in the current context*, treat it as `[NEEDS-INPUT]`.
- Never carry a proof point, customer name, or number from an earlier task into a new one.
- Never treat an example in a global skill's own documentation as a fact about the current business. Every example in this family is illustrative.
- When the same phrase would fit two different clients equally well, that is a signal the copy is generic, not that it is reusable.

## When context is missing

Missing context is a normal state, not an error. The correct response:

1. Produce the deliverable's **structure** and its `[PROPOSED]` messaging.
2. Mark every fact-dependent slot `[NEEDS-INPUT]` with a precise description of the input.
3. List the gaps at the end, grouped by who can answer them.
4. State plainly that the draft is not publishable until the slots are filled.

Do not stall the entire deliverable on one missing input, and do not quietly downgrade the copy to something vague enough to avoid needing facts. Vague copy is the failure mode that missing proof produces; naming the gap is the fix.

## Distinguishing known facts from proposed messaging

The single most useful sentence in a copy hand-off:

> Everything in the Proof section is sourced. Everything in the Positioning section is a recommendation you have not yet committed to.

Say it. Reviewers who cannot tell the two apart approve fabrications by accident.
