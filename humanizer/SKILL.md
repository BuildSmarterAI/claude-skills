---
name: humanizer
description: Final editorial pass that strips AI tells from copy - cliché vocabulary, uniform sentence rhythm, em-dash overuse, hollow transitions, inflated adjectives, formulaic triads, empty superlatives, robotic sectioning - while preserving meaning, persuasion, brand voice, technical terms, and deliberate formatting. Use when text is accurate but reads machine-written, or as the last stage before copy ships.
origin: BuildSmarter Copy OS
---

# Humanizer

The last editorial pass. It removes the signature of machine writing without weakening the argument.

**The line that governs this skill: do not make strong copy casual.** A confident, specific, well-argued sentence is not an AI tell. Flattening it into chattiness is a worse failure than the tells being removed.

## When to Activate

- Copy is accurate and structurally sound but reads as machine-written.
- Final pass before anything ships externally.
- A draft is full of "leverage", "seamless", "robust", "unlock", "delve".
- Every sentence is the same length and every section the same shape.
- Someone says the writing "sounds like AI" or "sounds like everyone else".

## When NOT to Activate

- The copy is wrong, unclear, or unpersuasive - fix that first with `copychief` or `direct-response-copy`. This skill does not repair arguments.
- Technical documentation where uniformity is a feature.
- Legal or compliance text where the wording is load-bearing.
- Building a voice profile from published work -> `brand-voice`.

## Inputs required

The text, and where available: the brand voice profile, the register the copy is meant to hold, and the list of terms that must not be changed. Absent a voice profile, default to plain, specific, and direct - never to breezy.

## Vocabulary tells

Replace on sight. The right substitute depends on the sentence; these are starting points.

| Tell | Reach for |
|---|---|
| leverage | use, put to work |
| utilize | use |
| optimize | fix, tune, speed up |
| empower | let, give |
| unlock | open, get, reach |
| delve into | dig into, look at |
| seamless | easy, no setup, one step |
| robust | solid, tested, holds up |
| revolutionary, game-changing | new, first, different |
| transformative | changes how you work |
| holistic | complete, end to end |
| streamline | cut steps, speed up |
| harness | use, tap |
| synergy | working together |
| actionable insights | what to do next |
| deep dive | the detail |
| move the needle | change the number |
| navigate the complexities of | handle, deal with |
| in today's fast-paced world | (cut the clause entirely) |
| it's not just X, it's Y | (cut - say the thing) |
| whether you're X or Y | (cut - pick one reader) |
| when it comes to | (cut - start with the noun) |

Also remove: "elevate", "curated", "bespoke", "cutting-edge", "best-in-class", "world-class", "industry-leading", "supercharge", "unparalleled", "meticulously", "testament to", "landscape" (figurative), "realm", "tapestry", "embark".

## Structural tells

Vocabulary is the easy half. These shapes read as machine-written even when every word is clean.

**Uniform rhythm.** Three sentences of similar length in a row is the strongest single tell. Break it. Short one. Then a longer sentence that carries the argument and gives the reader room. Then short.

**The rule of three, everywhere.** "Fast, reliable, and scalable." Machine writing reaches for triads reflexively. Use two, or four, or one. Keep a triad only where the third item earns its place.

**Em-dash overuse.** One per paragraph at most, and only where a comma or a full stop would genuinely be worse. Machine drafts use them as an all-purpose connective.

**Hollow transitions.** "Moreover", "Furthermore", "Additionally", "That said", "It's worth noting that", "Importantly". Cut them. If the connection is real, the sentences carry it themselves.

**Symmetrical sectioning.** Every section the same length with the same intro-body-summary shape. Real writing is lumpy. Let sections be the length their content needs.

**Hedge stacking.** "May potentially help improve." One qualifier maximum, and only where the uncertainty is real.

**Restating the question.** "When it comes to choosing a vendor, choosing a vendor requires..." Start with the answer.

**Summary paragraphs nobody asked for.** "In conclusion, we've explored..." Cut. The reader was there.

**Adjective stacks.** "Innovative, reliable, scalable solution." One adjective, or replace all of them with a fact.

**Perfectly parallel bullets.** Every bullet the same length and grammatical shape. Vary them; let one be a fragment.

**Fake conversational inserts.** "Here's the thing." "Let's be honest." "Sound familiar?" These simulate a voice rather than having one. Cut unless the brand genuinely writes that way.

## What must survive

Removing tells must not remove:

- **Factual accuracy.** Never change a number, name, date, term, or claim while editing prose.
- **Persuasive force.** A specific promise stays specific. Do not soften a claim to make it sound more human.
- **Brand voice.** If the profile says formal, stay formal. Human does not mean casual.
- **Technical terminology.** Domain terms are precision, not jargon. "Change order", "RLS policy", "vertical dispersion" stay.
- **Deliberate formatting.** Intentional repetition, a one-word paragraph, an anaphoric run - these are craft. Recognise them before cutting them.
- **Structure that serves comprehension.** Tables, numbered steps, and headings in reference material are correct.

## Never add

- Fabricated anecdotes, personal stories, or "I remember when" openers.
- Invented statistics, sources, or attributions.
- Casual filler to sound human ("honestly", "look,", "at the end of the day").
- Contractions in a brand voice that does not use them.
- Slang or idiom that the audience may not share.

Humanizing is **subtraction and rewriting**, never invention. If the draft is thin, that is a `copychief` finding, not something to fill.

## Reasoning workflow

1. Read aloud. Mark every stumble.
2. Vocabulary pass - the table above.
3. Rhythm pass - read sentence lengths as a sequence; break any run of three similar.
4. Transition pass - delete hollow connectives, check the prose still flows without them.
5. Structure pass - triads, symmetry, em-dashes, summary paragraphs.
6. Preservation check - diff against the original for facts, terms, and claims. Anything that changed meaning gets reverted.
7. Read aloud again.

## Output contract

```
EDITED COPY
  <the full edited text, ready to use>

CHANGES
  <tell removed> -> <what replaced it>   x n
  Rhythm: <where and how it was broken up>
  Structure: <what was cut>

PRESERVED DELIBERATELY
  <thing that looks like a tell but is craft or a required term, and why>

MEANING CHECK
  Facts unchanged: <yes | what changed and why>
  Claims unchanged: <yes | ...>
  Register held:    <yes | ...>
```

## Quality gates

- No word from the vocabulary table survives unless the brand voice requires it.
- No three consecutive sentences of similar length.
- Every fact, number, name, and technical term is byte-identical to the input unless the change was flagged.
- No content was added.
- The edited version is not more casual than the brand voice allows.
- Persuasive claims are as strong as they were, or stronger.

## Failure conditions

- The copy is weak rather than robotic. Say so and route to `copychief`. Humanizing a bad argument produces a readable bad argument.
- Removing the tells would require weakening a claim. Keep the claim, flag the tension.
- No voice profile exists and the register is genuinely ambiguous. Edit for plainness and specificity only, and say the register call is unmade.

## Handoffs

Runs after `copychief` and the channel skills · takes its register from `brand-voice` when a profile exists · hands off to `compliance-review` for anything shipping externally.

## Provenance rule

Editing never introduces facts. Never add a statistic, anecdote, quote, or attribution that was not in the input. Full contract: `copy-os/references/fact-provenance.md`.
