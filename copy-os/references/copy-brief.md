# The Copy Brief

The hand-off object every skill in the copy family reads and writes. One brief travels the whole route. Each stage **appends**; no stage silently rewrites an earlier stage's field. If a stage disagrees with an earlier field, it adds a `Revision:` note saying what changed and why.

A brief is not paperwork. It is the only thing preventing ten skills from each inventing their own version of the company.

## Schema

```markdown
# Copy Brief: <deliverable>

## 1. Deliverable
- Channel:            <landing page | sales page | google ad | meta ad | linkedin | cold email | nurture | social | collateral | web page>
- Format + limits:    <word count, character caps, asset slots>
- Primary action:     <the one thing the reader should do>
- Success measure:    <what would prove this worked>

## 2. Audience
- Who:                <role, situation, trigger event>          [FACT | PROPOSED | NEEDS-INPUT]
- Awareness stage:    <unaware | problem | solution | product | most aware>
- Market sophistication: <1-5, see direct-response-copy>
- Temperature:        <cold | warm | hot | lapsed | skeptical>
- What they already believe: <the belief the copy must work with or against>
- What they have already been told: <competing claims saturating this market>

## 3. Offer
- What they get:      <deliverable, access, outcome>            [FACT | NEEDS-INPUT]
- Price / terms:      <...>                                     [FACT | NEEDS-INPUT]
- Risk reversal:      <guarantee, trial, pilot, or NONE>        [FACT | NEEDS-INPUT]
- Friction:           <what the reader must do, give up, or risk>

## 4. Proof
Only verified items belong here. Each line carries its source.
- <claim>  ->  <source: file path, URL, conversation, dataset>  [FACT]
- <claim>  ->  UNVERIFIED                                        [NEEDS-INPUT]

## 5. Positioning
- Category:           <the frame the reader files you under>
- Differentiator:     <the thing only this can say>             [FACT | PROPOSED]
- Against:            <the alternative, including "do nothing">
- Forbidden claims:   <what this business may not say, and why>

## 6. Voice
- Register:           <plain | technical | warm | blunt | formal>
- Source of voice:    <brand-voice profile | supplied samples | NEEDS-INPUT>
- Never say:          <words, claims, tones this brand rejects>

## 7. Constraints
- Legal / regulatory: <regulated category? claims substantiation regime?>
- Platform policy:    <the platforms this will run on>
- Repo overrides:     <local rules that beat generic methodology, with file path>

## 8. Sources
- <file path or URL>  -> <what it established>
- Context searched but not found: <list>

## 9. Gaps
- [NEEDS-INPUT] <the exact input needed, and who can supply it>

## 10. Stage log
- copy-strategist:    <what it decided>
- persuasion-engine:  <angles selected, angles rejected and why>
- <channel skill>:    <variants produced>
- copychief:          <score, top defects>
- humanizer:          <what it changed>
- compliance-review:  <verdict, flags>
```

## Minimum viable brief

Not every route needs all ten sections. A one-line headline rewrite needs sections 1, 2, and 4. Anything that will be published externally needs 1, 2, 3, 4, 5, 7.

A brief with an empty **section 4 (Proof)** is a warning, not a blocker: it means the copy cannot yet carry a specificity claim, and `copychief` will score it down for exactly that. Say so rather than filling section 4 with invention.

## Completeness levels

- **complete** — every field is `[FACT]` or deliberately `PROPOSED`; no `[NEEDS-INPUT]` in sections 1-3.
- **partial** — the copy can be drafted, with named gaps. This is the normal state. Draft anyway, mark the slots.
- **absent** — no local context at all. Produce structure and `[PROPOSED]` messaging only. Do not attach the business name to invented facts.
