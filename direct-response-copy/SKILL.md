---
name: direct-response-copy
description: Write direct-response copy that asks for an action - headlines, leads, body architecture, offers, and CTAs - using awareness-stage and sophistication-aware frameworks rather than generic marketing prose. Use for sales copy, promos, long-form pages, headline sets, taglines, and any writing whose job is a measurable response. Also known as copy-that-sells.
origin: BuildSmarter Copy OS
---

# Direct-Response Copy

The craft layer. Strategy decides what to argue; this decides how it is said so a reader acts.

Aliases: **copy-that-sells**, **direct-response copywriting**, **sales copy**.

## When to Activate

- Writing or rewriting copy whose success is a measurable action.
- Headlines, subheads, leads, taglines, bullets, offers, CTAs, guarantees.
- Long-form: sales pages, promos, VSL scripts, advertorials, letters.
- Someone asks for copy that "converts", "sells", or "gets a response".
- Rewriting brand copy that describes instead of persuades.

## When NOT to Activate

- Editorial articles, tutorials, docs, thought-leadership essays -> `article-writing`.
- The only problem is that finished copy sounds machine-written -> `humanizer`.
- Copy needs judging, not writing -> `copychief`.
- Channel-specific structure is the whole question -> `landing-page-copy`, `ad-copy`, `email-copy`, `social-copy`.

## Inputs required

Awareness stage, market sophistication, the offer, the proof inventory, and the forbidden-claims list. Get these from a Copy Brief (`copy-os`) or from `copy-strategist`. Without them, write the structure and mark `[NEEDS-INPUT]`; do not guess the offer.

## Headlines

The headline does one job: earn the next line. Judge every candidate on whether a *specific* reader would keep reading, not on whether it sounds good.

**Working forms** - pick by awareness stage, not by taste:

| Form | Shape | Best for |
|---|---|---|
| Benefit-specific | The measurable outcome, named | Problem- and solution-aware |
| Mechanism | The how, made interesting | Sophistication 3-4 |
| Problem-agitation | The pain, said better than they say it | Problem-aware |
| News | What changed, and when | Unaware, product-aware |
| Curiosity gap | A question only the body answers | Unaware - use sparingly, never as a trick |
| Direct offer | The deal, plainly | Most aware |
| Proof-led | The number, first | Product-aware with strong proof |
| Contrarian | The received wisdom, denied | Sophistication 4-5 |

**Rules that hold across forms:**

- Specific beats clever. A number, a name, a timeframe, a place.
- One idea. A headline carrying two ideas carries none.
- Say the thing. If the headline could sit on a competitor page unchanged, it is a category label.
- No headline may make a claim the proof inventory cannot support.
- Write more than you need. Ten is a working set; three is a preference.

## Leads

The lead is the first 50-150 words and it does the heaviest lifting on the page. Match it to awareness:

- **Story** - unaware. A specific scene, a specific person, a specific moment.
- **Problem** - problem-aware. Name the pain with more precision than they can.
- **Secret / mechanism** - solution-aware. There is a reason this works, and here it is.
- **Proclamation** - product-aware. A bold claim, immediately substantiated.
- **Offer** - most aware. The deal, the terms, the deadline.

A lead fails when it warms up. Delete the first paragraph and check whether anything was lost; usually the copy improves.

## Body architecture

Long copy is not padded short copy. It earns its length by answering, in order, the questions a buying reader actually asks:

```
1. Is this for me?          <- reader recognition
2. What is the problem?     <- named precisely
3. Why has nothing worked?  <- validates their history, defuses "tried that"
4. What is different here?  <- the mechanism
5. Does it work?            <- proof, specific and sourced
6. What exactly do I get?   <- the offer, itemised
7. What if I am wrong?      <- risk reversal
8. Why now?                 <- a real reason, not a manufactured one
9. What do I do?            <- one action, unambiguous
```

Cut any section that does not move a reader toward the next question. Order can flex; the questions do not.

**Rhythm.** Vary sentence length deliberately. Short sentences land. Longer sentences carry an argument and give the reader somewhere to breathe before the next hit. Then short again.

**Subheads** must carry the argument alone. A reader who reads only subheads should get the whole case.

## Bullets

Bullets sell curiosity, not features. Each one implies a payoff without delivering it. Keep them concrete, keep them parallel, and never let a bullet promise something the body does not deliver.

## Offer and CTA

- State exactly what happens next. "Get started" is not an instruction.
- One primary action per asset. Competing CTAs halve both.
- Restate the value at the point of action, not just at the top.
- Put the risk reversal adjacent to the button, where the hesitation lives.
- Remove a field. Then remove another. Friction is measured in fields.

## Editing rules

Run these in order on every draft:

1. **Cut the first paragraph.** Check what was lost. Usually nothing.
2. **Replace every abstraction with a thing.** "Improve efficiency" becomes "cut the Friday close from six hours to forty minutes".
3. **Kill adjective stacks.** One strong adjective, or a fact instead.
4. **Passive to active.** Name who does what.
5. **Hedges out.** "May help potentially" is an admission the claim is unsupported. Either support it or drop it.
6. **Read aloud.** Stumble means cut. Sounds like a press release means rewrite.
7. **So-what, three times.** Push each benefit down to the human consequence.
8. **The competitor test.** Paste a competitor name over yours. If it still reads true, the copy says nothing.

## Anti-generic principles

- Write to one person, not a segment.
- Facts persuade; adjectives decorate. Prefer the fact.
- Every claim earns its keep with proof, a mechanism, or a demonstration.
- Concrete nouns and strong verbs; the modifier is usually the weakest word in the sentence.
- Do not sell the product. Sell the situation the reader is in afterwards.
- If a sentence could open any page in the category, it is filler.

## Output contract

```
HEADLINES        <n variants, each tagged with form + awareness stage>
LEAD             <the chosen opening, 50-150 words>
BODY             <structured to the nine questions>
CTA              <action + risk reversal>
NOTES
  Claims:        <each mapped to [FACT] source | [PROPOSED] | [NEEDS-INPUT]>
  Cut:           <what was removed and why>
  Recommend:     <offer or proof changes that would beat any wording change>
```

## Quality gates

- Every claim traces to the proof inventory or is labelled.
- The headline set covers more than one form, not ten variants of one.
- The copy would fail the competitor test if the brand name were swapped.
- Sentence rhythm varies; no three consecutive sentences share a shape.
- One CTA, one action, stated as an instruction.
- Nothing in the copy required inventing a fact.

## Failure conditions

- The offer cannot carry the promise the copy needs. Escalate to `copy-strategist`.
- The proof inventory is empty and the market is at sophistication 3+. Say that specificity is impossible without inputs rather than writing vaguer claims.
- The requested claim is unsubstantiated. Route to `compliance-review`; do not soften it into deniability.

## Handoffs

`copy-strategist` upstream · `persuasion-engine` for angle selection · `copychief` to review · `humanizer` for the final editorial pass · `compliance-review` before anything ships.

## Provenance rule

Never invent proof, customers, results, pricing, guarantees, or competitor claims. Facts come from repo-local context, supplied files, or the user. Label every assertion `[FACT]`, `[PROPOSED]`, or `[NEEDS-INPUT]`. Full contract: `copy-os/references/fact-provenance.md`.
