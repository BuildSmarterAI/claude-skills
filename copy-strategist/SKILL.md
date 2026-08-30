---
name: copy-strategist
description: Turn a vague copy request into a decided strategy before anyone writes a word - audience, awareness stage, market sophistication, offer architecture, message hierarchy, and the proof inventory. Use when a copy task needs direction, when a page is not converting and nobody knows why, or when a Copy Brief does not exist yet.
origin: BuildSmarter Copy OS
---

# Copy Strategist

Copy fails upstream of the sentence. This skill decides what the copy must argue before any craft skill decides how to say it. It produces the Copy Brief the rest of the family consumes.

## When to Activate

- A copy request arrives with no brief, or with a brief that has no audience or offer.
- A sales page, landing page, campaign, or sequence is being built from scratch.
- Existing copy underperforms and the diagnosis is unclear.
- The same message has to work across several channels and needs one spine.
- Someone asks "what should we say?" rather than "how should we say it?"

## When NOT to Activate

- The message is already decided and only the wording is in question -> `direct-response-copy`.
- The task is a single headline variant or a subject-line test.
- The request is market or competitor research, not messaging -> `market-research`.
- The request is a voice/tone question -> `brand-voice`.

## Inputs required

Ask for what is missing rather than assuming it. The strategy can be drafted on partial input; mark gaps.

| Input | Why it decides something |
|---|---|
| Who buys, and who signs | Changes the argument, not just the vocabulary |
| The trigger event | The moment the reader becomes reachable |
| What they have already tried | Sets sophistication level |
| The offer and its terms | Determines whether the page can close or only capture |
| Verified proof available | Determines whether specificity is possible |
| What the business may not claim | Bounds everything downstream |
| Where it runs | Sets length, format, and policy constraints |

Missing inputs become `[NEEDS-INPUT]` lines. Never fill them from imagination.

## Reasoning workflow

### 1. Locate the reader on the awareness ladder

Schwartz's five stages. The stage decides where the copy must start, and it is the single highest-leverage strategic call.

| Stage | The reader knows | Copy must open with |
|---|---|---|
| **Unaware** | Nothing - no problem recognised | A story, an observation, a fact about their world |
| **Problem-aware** | The pain, not that solutions exist | The problem, named more precisely than they can name it |
| **Solution-aware** | Solutions exist, not yours | The mechanism - why this category of solution works |
| **Product-aware** | Yours, but not convinced | The differentiator and the proof |
| **Most aware** | Everything; they need a reason now | The offer and the deadline |

Getting this wrong is the most common cause of a page that "reads fine" and converts badly. Product-aware copy shown to an unaware reader reads as noise. Unaware copy shown to a most-aware reader reads as stalling.

### 2. Read market sophistication

How many times has this market heard this claim? Sophistication is about the *market*, not the reader.

1. **First to market** - state the claim plainly. It is new; that is enough.
2. **Claim is familiar** - amplify it. Bigger, faster, more specific than the incumbent said it.
3. **Claims are exhausted** - lead with a *mechanism*. Not what it does; how it does it.
4. **Mechanisms are exhausted** - elaborate the mechanism, or make it more believable.
5. **Everything is exhausted** - shift to identity, experience, or a new frame entirely.

A level-1 promise in a level-4 market reads as a lie. A level-4 mechanism essay in a level-1 market reads as evasion.

### 3. Inventory the proof before promising anything

List what can actually be substantiated. Three columns: claim, evidence, source. Anything without a source is `[NEEDS-INPUT]`, not a softer claim.

The proof inventory constrains the promise. A business with no numbers cannot lead with numbers, and the honest move is a demonstration, a specific mechanism, or a risk reversal - not a vaguer version of the number it does not have.

### 4. Architect the offer

The offer is usually a bigger lever than the copy. Assess and, where you can, recommend changes:

- **Value stack** - what is included, in the order the reader values it
- **Risk reversal** - who carries the risk of being wrong, and for how long
- **Friction** - every field, call, commitment, and unknown between reading and acting
- **Reason to act now** - a real one; see the anti-patterns in `persuasion-engine`
- **The alternative** - including doing nothing, which is the real competitor

If the offer is weak, say so. Copy cannot rescue an offer nobody wants.

### 5. Set the message hierarchy

One primary claim. Two or three supports. Everything else is subordinate or cut.

```
PRIMARY:   <the one thing they must believe>
SUPPORT 1: <the proof that makes it credible>
SUPPORT 2: <the objection it pre-empts>
SUPPORT 3: <the reason it matters now>
CUT:       <everything the business wants to say that the reader does not need>
```

If you cannot name what gets cut, the hierarchy is not finished.

### 6. Name the dominant objection

Every reader has one thing that stops them. Name it explicitly and decide where the copy handles it. Copy that never names the objection is arguing with a reader who has already left.

## Output contract

A Copy Brief per `copy-os/references/copy-brief.md`, plus a short strategy note:

```
STRATEGY
  Reader:          <who, at what moment>
  Awareness:       <stage> - therefore copy opens with <...>
  Sophistication:  <1-5> - therefore the claim takes the form <...>
  Primary claim:   <one sentence>
  Proof status:    <strong | thin | absent> - <what that forces>
  Dominant objection: <...> handled at <position>
  Offer verdict:   <sound | needs work: what>
  Gaps:            [NEEDS-INPUT] ...
```

## Quality gates

- The awareness stage is stated and justified from evidence, not guessed.
- The sophistication level is justified by what competitors are already saying.
- Every proof point has a source or is marked `[NEEDS-INPUT]`.
- The primary claim is one sentence a skeptical reader could dispute - if nobody could disagree with it, it says nothing.
- Something was cut.
- The strategy would produce different copy from a competitor's strategy. If it would not, it is a category description, not a position.

## Failure conditions

- The offer is not viable and no amount of copy fixes it. Say this rather than writing around it.
- Two audiences with incompatible arguments are being served by one asset. Split the asset or pick one.
- Positioning cannot be established because no local marketing context exists and the user cannot supply it. Produce structure with `[PROPOSED]` positioning and stop short of asserting it as fact.
- The claim the business wants is one it cannot substantiate. Escalate to `compliance-review` rather than softening the wording until it passes unnoticed.

## Handoffs

-> `persuasion-engine` for angle selection · `direct-response-copy` for craft · the channel skills for execution · `market-research` when the sophistication read needs competitive evidence · `compliance-review` early when the category is regulated.

## Provenance rule

Never invent proof, customers, results, pricing, positioning, or permissions. Facts come from repo-local context, supplied files, or the user. Label every assertion `[FACT]`, `[PROPOSED]`, or `[NEEDS-INPUT]`. Full contract: `copy-os/references/fact-provenance.md`.
