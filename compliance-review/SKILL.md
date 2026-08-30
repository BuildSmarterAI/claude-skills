---
name: compliance-review
description: Marketing-risk review of copy before it ships - unverifiable claims, fabricated statistics, unsupported guarantees, misleading comparisons, deceptive urgency, ad-platform policy exposure, prohibited claims, sensitive-attribute targeting - returning per-claim verdicts and the items that need a human reviewer. Use before publishing external marketing, and whenever copy makes a claim, comparison, guarantee, or price statement.
origin: BuildSmarter Copy OS
---

# Compliance Review

The last gate before copy goes outside. It asks one question of every assertion: **what would we show if someone demanded substantiation?**

This skill flags and explains risk. It is not legal advice and it does not clear anything for launch in a regulated category. Its output routes decisions to humans, and says so.

## When to Activate

- Before publishing any external marketing asset.
- Copy makes a performance claim, comparison, guarantee, price statement, or superlative.
- The category is regulated: health, finance, credit, insurance, legal, employment, housing, education, supplements, crypto, children.
- Copy will run as paid media on any ad platform.
- A claim was requested that nobody can point at a source for.
- `copychief` escalated an unsourced claim.

## When NOT to Activate

- Internal documents that will not be published.
- Code, technical documentation, changelogs.
- The concern is quality, not risk -> `copychief`.
- Repository skill-catalogue validation -> `skill-comply` (unrelated, similarly named).

## Inputs required

The copy, the proof inventory or Copy Brief, the target jurisdictions, the platforms it will run on, and the business's known restrictions. Missing inputs do not block the review - they become explicit `NEEDS-HUMAN` items.

## Review dimensions

### 1. Claim substantiation

Every assertion of fact gets a verdict:

| Verdict | Meaning |
|---|---|
| **SUBSTANTIATED** | A source exists and is cited |
| **UNSUBSTANTIATED** | Stated as fact, no source. Must be sourced, softened to opinion, or cut |
| **FABRICATED** | Traced to no origin at all. Hard stop - remove before anything else happens |
| **PUFFERY** | Subjective and non-falsifiable ("the best coffee in town"). Generally low risk; still flag in regulated categories |
| **NEEDS-HUMAN** | Cannot be judged without legal, regulatory, or business input |

Numbers get the strictest treatment. Any statistic without a named source is `UNSUBSTANTIATED` at minimum. A precise-looking number with no source is `FABRICATED`, not "close enough".

### 2. Guarantees and promises

- Is the guarantee one the business has actually agreed to offer?
- Are the terms stated where the guarantee is stated, or buried?
- Do the conditions make it practically unclaimable? That is a deceptive-practice exposure, not a clever hedge.
- Does the copy promise an outcome the business cannot control? Outcome promises in health, finance, employment, and immigration are high-exposure everywhere.

### 3. Comparisons

- Is the comparison against a real, current, correctly described alternative?
- Would the competitor recognise their own product in the description?
- Is the comparison basis stated (which plan, which configuration, which date)?
- "Better", "faster", "cheaper" without a basis is an unsubstantiated comparative claim, and comparative claims attract the most complaints of any category.

### 4. Urgency and scarcity

- Is the deadline real and enforced?
- Does the countdown reset per visitor?
- Is "limited" backed by an actual limit?
- Manufactured urgency is both a policy violation on major platforms and a consumer-protection exposure in most jurisdictions.

### 5. Testimonials, endorsements, reviews

- Did a real, identifiable person say it?
- Is it representative, or is it an atypical result presented as typical?
- Are material connections disclosed - paid, gifted, affiliated, employee?
- Are review counts and ratings real and current?
- An invented testimonial is a hard stop. There is no version of this that is acceptable.

### 6. Sensitive attributes

Flag any copy that targets, segments, or implies segmentation on: race, ethnicity, religion, national origin, immigration status, sexual orientation, gender identity, disability, health or medical condition, pregnancy, age, criminal history, financial distress, or union membership.

This is simultaneously an ethics problem, an ad-platform policy violation, and in housing, employment, and credit, a legal one in many jurisdictions. Flag it; do not work around it.

### 7. Platform policy exposure

Ad platforms maintain their own rules and **change them frequently**. Treat every specific rule as something to verify, never as settled fact.

Structural risks that have been stable across platforms and are worth checking first: before-and-after imagery, personal-attribute assertions ("as a diabetic, you..."), unrealistic outcome claims, countdown pressure, misleading landing-page mismatch, restricted categories, and claims about protected classes.

**`references/platform-policy-checkpoints.md`** lists what to check per platform. It is a dated checklist of *where to look*, not a copy of any platform's rules. Read the current policy before launch.

### 8. Jurisdiction

Advertising rules differ by country and often by state or province. Where the copy will run outside the reviewer's jurisdiction, mark the claim `NEEDS-HUMAN` rather than assuming the local rule travels.

## Reasoning workflow

1. Extract every assertion into a list - claims, numbers, comparisons, guarantees, urgency, endorsements.
2. Assign each a verdict against the substantiation table.
3. Run dimensions 2-8 across the whole asset.
4. Separate **hard stops** from **flags** from **notes**.
5. For every hard stop and flag, give the remediation: the sourced version, the softened version, or the cut.
6. List what a human must decide, and who.

## Output contract

```
COMPLIANCE REVIEW - <asset>

VERDICT  <CLEAR | CLEAR WITH CHANGES | BLOCKED | NEEDS HUMAN REVIEW>

HARD STOPS  (must change before use)
  - <claim as written>
    ISSUE:  <fabricated | invented testimonial | sensitive-attribute targeting | false guarantee>
    FIX:    <the exact replacement, or [NEEDS-INPUT: the source required]>

FLAGS  (change or accept with a documented reason)
  - <claim>  ISSUE: <...>  FIX: <...>

CLAIM LEDGER
  <claim>  ->  <SUBSTANTIATED (source) | UNSUBSTANTIATED | FABRICATED | PUFFERY | NEEDS-HUMAN>

PLATFORM EXPOSURE
  <platform>: <risk> - verify against current policy before launch

NEEDS HUMAN REVIEW
  <item>  ->  <who: legal, compliance, the claim owner>

NOT ASSESSED
  <jurisdiction, regime, or platform outside what was supplied>
```

## Quality gates

- Every assertion appears in the claim ledger. A claim not in the ledger was not reviewed.
- Every number is traced or marked.
- Hard stops are separated from flags - a fabricated statistic and an over-strong adjective are not the same finding.
- Every finding carries a remediation.
- No remediation invents a source to resolve an unsubstantiated claim.
- Platform findings say "verify current policy", and no specific rule is asserted as permanently true.
- The review states what it did not assess.

## Failure conditions

- A regulated-category outcome claim with no human reviewer in the loop: verdict is `NEEDS HUMAN REVIEW`, not `CLEAR`.
- The user wants a fabricated statistic, testimonial, or guarantee retained. Decline that element, state why in a sentence, deliver the rest of the review, and offer the sourced or slot-based alternative.
- Jurisdiction unknown and the claim is jurisdiction-sensitive: mark `NEEDS-HUMAN`; do not default to the most permissive reading.
- Substantiation exists but was not supplied: `UNSUBSTANTIATED (source not provided)` - distinct from "no source exists", and say which.

## Limits of this review

This is a marketing-risk review by a non-lawyer. It does not establish legal compliance, does not clear regulated claims, and does not substitute for platform pre-approval. Anything it marks `NEEDS-HUMAN` needs a human before launch.

## Handoffs

Receives from every channel skill and `copychief` · returns hard stops to the drafting skill · escalates substantiation gaps to `copy-strategist` (proof inventory) · `persuasion-engine` owns the honest forms of urgency, authority, and social proof.

## Provenance rule

Never invent a source to resolve an unsubstantiated claim. The remediation for a missing source is a `[NEEDS-INPUT]` slot naming the evidence required. Full contract: `copy-os/references/fact-provenance.md`.
