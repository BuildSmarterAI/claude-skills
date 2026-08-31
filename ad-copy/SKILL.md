---
name: ad-copy
description: Write paid-ad copy for Google, Meta, LinkedIn, TikTok, Microsoft, and display - headlines, descriptions, primary text, hooks, and CTAs - built around platform intent, format limits, and the landing page it must match. Use when generating or rewriting ad creative copy, not when auditing an existing ad account's performance, budgets, or creative fatigue.
origin: BuildSmarter Copy OS
---

# Ad Copy

Paid copy has three constraints ordinary copy does not: a hard character budget, a platform whose reader is in a specific mental state, and a landing page it must not contradict.

## When to Activate

- Writing or rewriting ad text for any paid platform.
- Producing headline and description variant sets for testing.
- Building hooks for paid social, or responsive search ad asset sets.
- Adapting one message across several platforms without flattening it.

## When NOT to Activate

- Auditing an existing account's creative portfolio, fatigue signals, format diversity, or spend -> `ads-creative` and the `ads` audit family. That family diagnoses accounts; this one writes copy.
- Budget, bidding, or targeting strategy -> `ads-budget`, `ads-plan`.
- The destination page -> `landing-page-copy`.
- Organic social posts -> `social-copy`.

## Inputs required

The Copy Brief, the platform and placement, the exact landing page promise, the offer, the proof inventory, character limits for the format, and any brand-forbidden claims. If the landing page does not exist yet, write the ad and flag that message match is unverified.

## Platform intent

The same offer needs a different opening on each platform, because the reader is doing something different.

| Platform | Reader is | Copy leads with | Avoid |
|---|---|---|---|
| **Google Search** | Actively looking, has typed the problem | The exact thing they searched, plus the differentiator | Story openers, curiosity gaps |
| **Google Display / Demand Gen** | Not looking at all | A recognisable situation or a strong visual claim | Anything requiring context to parse |
| **Meta** | Scrolling for entertainment | A pattern interrupt in the first line - a specific situation, not a question | Corporate register, feature lists |
| **LinkedIn** | In professional mode, guarded | A role-specific problem, credibly stated | Hype, consumer urgency, exclamation |
| **TikTok** | Watching, fast, native-first | The hook in the first two seconds, in platform-native voice | Repurposed TV script, formal tone |
| **Microsoft** | Searching, often older and higher-intent B2B | Same as Google Search, register slightly more formal | Slang |
| **Retargeting** | Already met you | The specific objection that stopped them, or the offer | Reintroducing the brand |

## Format discipline

Character limits are part of the craft, not an afterthought. Confirm current limits from the platform before finalising - they change - and write to the limit, not to the average.

- **Front-load.** Truncation happens at the end. The claim goes first.
- **One idea per headline.** Ad headlines cannot carry a subordinate clause.
- **Write variant sets, not variants.** For responsive formats, every headline must make sense against every description. Test the combinations.
- **Vary the angle, not the wording.** Ten headlines that say the same thing differently is one test, not ten.
- **Match the destination.** The ad's promise and the page's hero must be recognisably the same promise, in similar words.

## Variant design

Build a test set that isolates a variable:

```
ANGLE A  <problem-led>      x2 headlines
ANGLE B  <outcome-led>      x2 headlines
ANGLE C  <mechanism-led>    x2 headlines
ANGLE D  <proof-led>        x2 headlines   (only if proof exists)
```

Four angles beat ten rewordings, because a losing angle tells you something and a losing synonym does not.

## Hard limits

Ad platforms enforce more aggressively than any other channel, and rejections are often silent. Never write:

- Personal-attribute assertions - copy that claims to know something about the viewer ("struggling with debt?", "as a diabetic").
- Targeting or implied targeting on protected classes. In housing, employment, and credit, assume a special regime applies.
- Unrealistic outcome claims - income, health, guaranteed results.
- Countdown or scarcity language that is not backed by a real limit.
- Comparative claims about a named competitor without a verifiable current source.
- Before-and-after framing.
- Any statistic without a source.

`compliance-review` owns the full treatment. These are the ones that most often stop an ad before it serves.

## Output contract

```
PLATFORM: <...>   FORMAT: <...>   LIMITS: <verified from platform docs on YYYY-MM-DD>

DESTINATION MATCH
  Page hero says:  <...>
  Ads promise:     <...>
  Match:           <yes | flagged: how they differ>

VARIANTS
  ANGLE <A-D>: <angle name>
    Headline:      <text>  (<n>/<limit> chars)
    Description:   <text>  (<n>/<limit>)
    Primary text:  <text>  (<n>/<limit>)
    CTA:           <...>
    Persuasion:    <principle applied>
    Claims:        <[FACT] source | [PROPOSED] | [NEEDS-INPUT]>

TEST DESIGN
  Variable isolated: <...>
  What each result would tell you: <...>

POLICY FLAGS
  <item> -> route to compliance-review
```

## Quality gates

- Character counts are stated and within the platform's current published limits.
- Angles are distinct; no two test cells differ only in wording.
- Every claim traces to the proof inventory or is a `[NEEDS-INPUT]` slot.
- The ad's promise and the landing page hero match, or the mismatch is flagged.
- Nothing on the hard-limits list appears.
- Responsive formats: every headline works against every description.

## Failure conditions

- The landing page does not exist or is unknown: produce the ads, mark message match unverified, and say the set is not launch-ready.
- Current character limits cannot be verified: state the limits you assumed and the date, and mark them for verification.
- The strongest available angle needs a statistic nobody has: write the other angles, and record the proof-led angle as blocked on a named input.
- The offer is not distinct enough to sustain four angles. That is a `copy-strategist` finding, not a writing problem.

## Handoffs

`copy-strategist` and `persuasion-engine` upstream · `landing-page-copy` owns the destination and must agree with these ads · `copychief` reviews · `compliance-review` is mandatory before launch · the `ads` audit family owns account-level diagnosis after the ads are running.

## Provenance rule

Never invent proof, results, review counts, customer names, competitor claims, or pricing. Facts come from repo-local context, supplied files, or the user. Label every assertion `[FACT]`, `[PROPOSED]`, or `[NEEDS-INPUT]`. Full contract: `copy-os/references/fact-provenance.md`.
