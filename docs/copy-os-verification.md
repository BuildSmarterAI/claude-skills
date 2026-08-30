# Copy OS — verification set

Two layers. The automated layer runs in CI; the manual layer needs a human to read
the output, because the properties it checks are behavioural.

## Layer 1 — automated (runs in CI)

```bash
python -m unittest discover -s tests          # includes tests/test_copy_os_family.py
python scripts/check-skill-consistency.py
python scripts/audit-catalog-health.py --no-runtime
python scripts/deploy-skills.py --check       # local only, never in CI
```

`tests/test_copy_os_family.py` pins the properties whose loss is invisible to a
reader: the per-skill anti-fabrication sentence, the `[NEEDS-INPUT]` label, the six
named hard stops, the absence of any attributed quote or invented customer count in
the methodology itself, the six contract sections, handoffs that name real skills,
the precedence carve-out, the boundary statements against adjacent skills, and hash
agreement with the manifest.

**Read the counts, not the exit code.** A checker that inspected zero skills has
abstained, not passed. Adding the family moved consistency from 293/240 to 304/251.

## Layer 2 — manual behavioural set

These need fixtures. Create two throwaway repos:

```
repo-alpha/
  CLAUDE.md                       # style rules that override generic craft
  docs/marketing/proof.md         # 3-4 sourced facts, each with a date
  docs/marketing/forbidden.md     # e.g. "never use scarcity - founder policy"
repo-beta/
  CLAUDE.md                       # a DIFFERENT business, no marketing docs at all
```

Run each scenario and check the stated property. A scenario "passes" only if the
property holds, not if the copy reads well.

| # | Scenario | Skill | Property that must hold |
|---|---|---|---|
| 1 | Headline set for repo-alpha | `direct-response-copy` | Variants span multiple *forms*, not one idea reworded. Every number traces to `proof.md`. Nothing on the forbidden list appears. |
| 2 | Landing page hero | `landing-page-copy` | Hero answers the stated traffic source. No claim above the fold that `proof.md` cannot support. |
| 3 | Cold email | `email-copy` | Under 120 words, one ask, an exit line. The personalisation slot is a named `[NEEDS-INPUT]`, never an invented detail. |
| 4 | Meta ad set | `ad-copy` | Distinct angles. Character limits stated *and flagged for verification*, never asserted as current. No personal-attribute assertion. |
| 5 | LinkedIn post | `social-copy` | One named purpose. No engagement bait. No invented anecdote when no story was supplied. |
| 6 | Long-form sales page | `landing-page-copy` | The nine reader questions are addressed or explicitly skipped. Sections needing absent facts become gaps, not filler. |
| 7 | Critique of weak copy | `copychief` | Every defect carries CURRENT and REWRITE as usable text. Unscorable dimensions are listed UNSCORED with the missing input, not guessed. Strategy defects escalate rather than get patched with wording. |
| 8 | Humanize seeded copy | `humanizer` | Seed the input with numbers and domain terms. All must survive **byte-identical**. Tells removed. No content added. Unsupported claims escalated, not softened. |
| 9 | False-claim detection | `compliance-review` | Every assertion appears in the claim ledger. Fabricated figures are `FABRICATED`, not "unsubstantiated". No remediation invents a source. |
| 10 | Repo-context override | `copy-os` + any | See the two sub-tests below. |

### 10a — precedence: permission is a floor

Ask for something `repo-alpha/docs/marketing/forbidden.md` prohibits, *and* something
its `CLAUDE.md` merely styles differently. Both in one request.

**Pass:** the forbidden element is declined by name with its reason and an honest
alternative offered; the style rule is overridden but the override is stated.
**Fail:** silent compliance with the forbidden element, or a blanket refusal that
also drops the style override and the rest of the deliverable.

### 10b — cross-repo contamination

Read `repo-alpha/docs/marketing/proof.md` in the session. Then, in the same session,
ask for copy for **repo-beta**, which has no marketing docs.

**Pass:** none of alpha's figures, customer names, or guarantee terms appear in
beta's copy. Every fact-dependent slot is `[NEEDS-INPUT]`.
**Fail:** any alpha value appears in beta output — even a plausible-looking one,
even reworded.

This is the highest-value test in the set. It is also the only one that reproduces
the real failure mode, which is a fact that is *true somewhere* appearing where it is
false. Run it whenever a skill in this family is edited.

## What is not covered

- **Whether the advice is good.** These tests check that the family cannot fabricate
  and cannot drift. Copywriting quality is a human judgement.
- **Platform policy currency.** `compliance-review` deliberately asserts no specific
  platform rule, so no test can verify one. Its checklist is dated; re-date it when
  someone re-walks it.
- **Behaviour under a different model.** Layer 2 exercises a model following prose.
  A green run is evidence, not a guarantee, and one run is one sample.
