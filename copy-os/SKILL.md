---
name: copy-os
description: Route a marketing copy request through the right sequence of copy skills — strategy, persuasion, drafting, adversarial review, humanization, compliance — and enforce the shared Copy Brief and fact-provenance contract. Use when a copy task spans more than one skill, when a channel is named (landing page, ad, email, social, sales page), or when you need to decide how much process a copy request actually warrants.
origin: BuildSmarter Copy OS
---

# Copy OS

The router and the rulebook for the copy skill family. Methodology is global; **truth is local**. This skill decides which skills run, in what order, and it owns the two contracts every copy skill shares.

## When to Activate

- A copy request names a channel: landing page, sales page, Google/Meta/LinkedIn ad, cold or nurture email, social post, website page, sales collateral.
- A request needs more than one copy skill (draft *and* review, or strategy *and* draft).
- You are unsure how much process a request warrants.
- A repository has marketing context and you need to know how to read it before writing.
- Someone asks for "the copy workflow", "the full treatment", or "run this through review".

## When NOT to Activate

- Editing a single line the user already wrote and only wants tightened → go straight to `humanizer` or `direct-response-copy`.
- Auditing an existing paid-ads account's creative portfolio, budgets, or tracking → that is the `ads` / `ads-creative` family, not this one.
- Product documentation, changelogs, API docs, technical writing → not direct-response copy.
- Building a voice profile from existing published work → `brand-voice`.

## Routing table

Match the request, run only the stages listed. Do not force every task through every stage.

| Request | Route |
|---|---|
| Headline or subject-line rewrite | `direct-response-copy` → `copychief` |
| A few lines of body copy | `direct-response-copy` → `humanizer` |
| Single ad (one platform, one variant set) | `ad-copy` → `copychief` → `compliance-review` |
| Ad campaign across platforms | `copy-strategist` → `persuasion-engine` → `ad-copy` → `copychief` → `compliance-review` |
| Landing page / hero section | `copy-strategist` → `landing-page-copy` → `copychief` → `humanizer` |
| Full sales page or long-form promo | `copy-strategist` → `persuasion-engine` → `direct-response-copy` → `landing-page-copy` → `copychief` → `humanizer` → `compliance-review` |
| Cold email sequence | `copy-strategist` → `persuasion-engine` → `email-copy` → `copychief` → `compliance-review` |
| Nurture / lifecycle email | `email-copy` → `copychief` → `humanizer` |
| Organic social post | `social-copy` → `humanizer` |
| Social campaign tied to an offer | `copy-strategist` → `social-copy` → `copychief` → `humanizer` |
| Sales collateral, one-pager | `copy-strategist` → `direct-response-copy` → `copychief` → `compliance-review` |
| "Why isn't this converting?" | `copychief` → `copy-strategist` |
| Copy exists and reads like AI wrote it | `humanizer` → `copychief` |
| Copy makes claims nobody has verified | `compliance-review` |

**Escalate a route** when the copy carries money (a page that takes payment), carries risk (regulated category, health, finance, employment, housing, credit), or goes out at volume. **Shrink a route** when the deliverable is under ~50 words and reversible.

`compliance-review` is not optional for anything published externally that makes a claim, a comparison, a guarantee, or a price.

## The two contracts

Both live in full under `references/`. Read them before writing company-specific copy.

- **`references/copy-brief.md`** — the Copy Brief. The shared hand-off object every skill in this family reads and writes. One brief travels the whole route; each stage appends, none silently rewrites.
- **`references/fact-provenance.md`** — the contamination rules. What a global skill may assume about a repository (nothing), how to label facts, and what to do when context is missing.

## The provenance rule, in short

Every factual assertion in generated copy carries one of three labels:

- **`[FACT]`** — sourced from repository-local context, a file the user supplied, or something the user stated in this conversation. Cite where.
- **`[PROPOSED]`** — messaging you are recommending. True only if the business chooses to make it true. Positioning, angle, promise framing.
- **`[NEEDS-INPUT]`** — a slot the copy needs filled and you do not have. Name the input; never fill it yourself.

Never invent proof, customer quotes, performance numbers, competitor claims, pricing, guarantees, certifications, headcounts, founding dates, or awards. A plausible number is worse than a blank, because a blank gets filled and a plausible number ships.

If repository context is missing, produce the copy with `[NEEDS-INPUT]` slots and list them. Do not stall the whole deliverable on one missing input.

## Precedence

When sources conflict, the more local one wins:

```
TASK / CAMPAIGN INSTRUCTIONS   (highest - this conversation)
  > REPOSITORY MARKETING KNOWLEDGE  (docs/marketing/, brand guides, positioning docs)
  > REPOSITORY INSTRUCTIONS         (CLAUDE.md, AGENTS.md, repo rules)
  > GLOBAL METHODOLOGY              (this skill family - lowest)
```

A repo that says "we never use urgency" overrides every persuasion principle in `persuasion-engine`. A campaign brief that says "lead with price this time" overrides the repo's usual positioning. Say out loud which level you are following when you deviate from generic methodology.

## Reading repository context

Before generating anything company-specific, look for local truth in this order and stop when you have enough:

1. `CLAUDE.md`, `AGENTS.md`, `README.md` at the repo root.
2. `docs/marketing/`, `docs/brand/`, `docs/positioning/`, `marketing/`, `content/`.
3. Existing published copy in the repo — landing pages, email templates, site content.
4. `docs/` for product capability claims you are about to repeat.

Record what you found in the brief's `Sources` field. If you found nothing, say so; do not infer positioning from the code.

## Output contract

When this skill routes a request, emit before doing the work:

```
ROUTE: <stage> -> <stage> -> <stage>
WHY:   <one line: what made this route the right size>
BRIEF: <complete | partial | absent>
GAPS:  <the [NEEDS-INPUT] items, or "none">
```

Then execute the stages. Carry one brief through all of them.

## Quality gates

- The route is justified by the deliverable's size, risk, and reversibility — not by habit.
- Every stage in the route actually ran, or you said why it was skipped.
- No `[FACT]` label without a source.
- `compliance-review` ran on anything external that makes a claim.
- The final output separates the copy itself from the notes about the copy.

## Failure conditions

Stop and report rather than proceeding when:

- The request needs company facts, there is no repository context, and the user is not present to supply them.
- Repo-local instructions contradict each other and the conflict is material.
- The copy would require a claim you have no basis for and the user has declined to supply one.
- The category is regulated and no human reviewer is in the loop for a launch-bound asset.

## Handoffs

`copy-strategist` sets the brief · `persuasion-engine` picks angles · `direct-response-copy` supplies craft · `landing-page-copy` / `ad-copy` / `email-copy` / `social-copy` are the channel executions · `copychief` reviews · `humanizer` edits · `compliance-review` clears. `brand-voice` supplies the voice profile if one exists. `market-research` supplies competitive and market inputs the brief asks for.
