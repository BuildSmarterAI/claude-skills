---
name: landing-page-copy
description: Write and structure landing page, sales page, and website page copy - hero, subhead, proof blocks, mechanism, objection handling, offer, and CTA - with section-by-section message match to the traffic source. Use when building or rewriting a page whose job is conversion, not when auditing an existing page for speed, forms, or UX.
origin: BuildSmarter Copy OS
---

# Landing Page Copy

Page copy is an argument arranged in space. Each section answers one question and earns the scroll to the next.

## When to Activate

- Writing or rewriting a landing page, sales page, home page, product page, or pricing page.
- Building a hero section, or fixing one that does not hold.
- Structuring a long-form sales page.
- A page needs to match a specific ad, email, or campaign it receives traffic from.

## When NOT to Activate

- Auditing an existing page for load speed, mobile experience, form mechanics, or trust-signal placement -> `ads-landing`.
- Technical implementation of the page -> the frontend skills.
- SEO structure and keyword mapping -> `seo`.
- The ad that drives the traffic -> `ad-copy`.

## Inputs required

The Copy Brief, the traffic source and the exact promise it made, the offer, the proof inventory, the primary action, and any fixed page structure. Without the traffic source you cannot check message match - ask for it, and if it is not available, write the page for a single named entry point and say which.

## Message match

The first rule of page copy: **the hero must answer the promise the reader arrived with.** A page that restates the brand rather than continuing the ad breaks the chain at the most expensive point.

- Ad promised a specific outcome -> the hero names that outcome, in words close to the ad's.
- Email promised a resource -> the hero delivers the resource, immediately.
- Organic search on a problem -> the hero names the problem.
- Direct or brand traffic -> the hero states the category and the differentiator.

Mismatch is also a platform-policy exposure, not only a conversion problem.

## Page architecture

Sections in the order a reader needs them. Cut any that this page does not need; do not reorder to a pattern that ignores the reader.

```
1  HERO              headline + subhead + primary CTA + one proof element
2  PROBLEM           the situation, named more precisely than the reader can
3  MECHANISM         why this works - required at sophistication 3+
4  OUTCOME           what changes, concretely
5  PROOF             numbers, named customers, demonstrations, third-party validation
6  HOW IT WORKS      three to five steps, so the reader can picture using it
7  OBJECTIONS        the dominant one first, named in the reader's own words
8  OFFER             what is included, terms, price posture
9  RISK REVERSAL     guarantee, trial, pilot - adjacent to the action
10 FINAL CTA         restated value + the single action
```

**Hero.** Headline states the outcome or the mechanism. Subhead does the qualifying work - who it is for and what it is. CTA is an instruction. One proof element sits above the fold: a number, a name, a logo the reader recognises. Nothing above the fold may be a claim the proof inventory cannot support.

**Short pages** (lead capture, single offer): sections 1, 4, 5, 8, 10.
**Long-form sales pages**: all ten, sometimes 3 and 5 repeated at increasing depth.
**Pricing pages**: 1, 8, 7, 9, 10 - objections belong beside the price, not after it.

## Section rules

- **One idea per section.** If a section needs two subheads to explain itself, it is two sections.
- **Subheads carry the argument.** A reader who scrolls and reads only subheads should get the full case. Test this by reading the subheads alone.
- **Proof sits next to the claim it supports**, not gathered in a testimonial ghetto at the bottom.
- **Objections in the reader's words.** "This will take months to set up" beats "Implementation".
- **One primary action per page.** Secondary actions are text links, not buttons.
- **The CTA repeats** at natural decision points, always with the same wording and same destination.
- **Nothing decorative.** A section that does not answer a reader question is deleted.

## Scroll depth

Each section owes the next one a reason to continue. After drafting, read only the last sentence of each section and ask whether it makes the next section inevitable. Where it does not, the page will leak there.

## Output contract

```
PAGE: <name>  |  TRAFFIC SOURCE: <what promise the reader arrived with>

MESSAGE MATCH
  Source promised: <...>
  Hero answers:    <...>

SECTIONS
  <n>. <SECTION NAME>
     Purpose:  <the reader question it answers>
     Headline: <text>
     Body:     <text>
     Proof:    <[FACT] source | [NEEDS-INPUT]>
     CTA:      <text, if any>

NOTES
  Sections omitted: <which, and why>
  Claims:           <[FACT] | [PROPOSED] | [NEEDS-INPUT]>
  Subhead-only read: <does the page argue with subheads alone? yes/no>
```

## Quality gates

- The hero answers the traffic source's promise in the source's own terms.
- The page argues successfully when only subheads are read.
- One primary action, one destination, repeated wording.
- Every proof element has a source or is a `[NEEDS-INPUT]` slot.
- The dominant objection is named, in the reader's language, before the offer.
- Risk reversal sits adjacent to the action, not in a footer.
- No section exists without a reader question attached to it.

## Failure conditions

- The traffic source is unknown and unobtainable: write for one named entry point, state the assumption, and mark the message-match check as unperformed.
- The offer is not viable on a page - the decision needs a conversation. Say so; recommend a lead-capture structure rather than pretending a page can close it.
- Proof inventory is empty and the market is sophisticated: the page cannot carry section 5. Report that the page will underperform for a reason no wording fixes.

## Handoffs

`copy-strategist` upstream · `direct-response-copy` for headline and body craft · `ad-copy` and `email-copy` must match this page's promise · `copychief` to review · `humanizer` before ship · `compliance-review` for claims · `ads-landing` for post-click technical and UX audit.

## Provenance rule

Never invent proof, customer names, results, pricing, or guarantees. Facts come from repo-local context, supplied files, or the user. Label every assertion `[FACT]`, `[PROPOSED]`, or `[NEEDS-INPUT]`. Full contract: `copy-os/references/fact-provenance.md`.
