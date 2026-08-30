# Copy OS

A reusable global copywriting and marketing-intelligence layer for Claude Code. Eleven composable
skills covering strategy, craft, persuasion, channel execution, adversarial review, humanization,
and marketing-risk review.

**Design principle: methodology is global, truth is local.** These skills contain no company
facts, no client information, no offers, no ICPs, no proof points, and no performance claims.
Those live in the repository the copy is being written for.

## Installed skills

| Skill | Role | Size |
|---|---|---|
| `copy-os` | Router. Owns the routing table and the two shared contracts | 7.8 KB + 2 refs |
| `copy-strategist` | Decides what the copy must argue, before anyone writes | 7.6 KB |
| `direct-response-copy` | Craft: headlines, leads, body architecture, offers, CTAs | 8.0 KB |
| `persuasion-engine` | Selects persuasion principles; blocks the manipulative forms | 9.7 KB |
| `copychief` | Adversarial reviewer, 15 dimensions, rewrite per defect | 7.8 KB |
| `humanizer` | Removes AI tells without weakening the copy | 8.1 KB |
| `compliance-review` | Marketing-risk gate before publication | 8.6 KB + 1 ref |
| `landing-page-copy` | Page structure and section copy | 6.5 KB |
| `ad-copy` | Paid ad copy per platform | 6.8 KB |
| `email-copy` | Cold, nurture, lifecycle email and sequences | 7.4 KB |
| `social-copy` | Organic social and short-video scripts | 7.2 KB |

## Paths

| What | Where |
|---|---|
| Canonical source | `<repo>/<skill-name>/SKILL.md` in `BuildSmarterAI/claude-skills` |
| Governance | `manifests/skills.json` — mode `CLAUDE_ONLY`, targets `["claude"]`, family `copy-os` |
| Claude runtime | `~/.claude/skills/<skill-name>/` |
| Codex runtime | **not deployed** — see "Adding Codex parity" below |
| Shared contracts | `copy-os/references/copy-brief.md`, `copy-os/references/fact-provenance.md` |
| Policy checklist | `compliance-review/references/platform-policy-checkpoints.md` |

The runtime store is a **deployment output**. Never hand-edit `~/.claude/skills`; edit the
canonical source and redeploy.

## Orchestration

The full workflow, when a deliverable warrants it:

```
RESEARCH -> STRATEGY -> PERSUASION ANGLES -> COPY GENERATION
         -> COPYCHIEF REVIEW -> HUMANIZATION -> COMPLIANCE REVIEW -> FINAL
```

Most tasks do not warrant it. `copy-os` holds the routing table; the principle is that route
length scales with the deliverable's size, risk, and reversibility.

```
Headline rewrite      direct-response-copy -> copychief
Single ad             ad-copy -> copychief -> compliance-review
Landing page          copy-strategist -> landing-page-copy -> copychief -> humanizer
Full sales page       copy-strategist -> persuasion-engine -> direct-response-copy
                      -> landing-page-copy -> copychief -> humanizer -> compliance-review
Cold email sequence   copy-strategist -> persuasion-engine -> email-copy -> copychief
                      -> compliance-review
Social post           social-copy -> humanizer
```

`compliance-review` is not optional for anything published externally that makes a claim, a
comparison, a guarantee, or a price.

## Precedence

Lower levels override higher ones when they conflict:

```
TASK / CAMPAIGN INSTRUCTIONS        (this conversation)
  > REPOSITORY MARKETING KNOWLEDGE  (docs/marketing/, brand guides, positioning docs)
  > REPOSITORY INSTRUCTIONS         (CLAUDE.md, AGENTS.md, repo rules)
  > GLOBAL METHODOLOGY              (these skills)
```

A repo rule saying "we never use urgency" beats every principle in `persuasion-engine`. A campaign
brief saying "lead with price this time" beats the repo's usual positioning.

## Structuring repo-local context

Give the global layer somewhere to read local truth. A minimal, effective structure:

```
docs/marketing/
  positioning.md      category, differentiator, the alternative (including doing nothing)
  audience.md         who buys, who signs, trigger events, what they have already tried
  offers.md           what is sold, terms, guarantees, price posture
  proof.md            verified claims ONLY, each with a source and a date
  voice.md            register, words to use, words this brand rejects
  forbidden.md        claims this business may not make, and why
```

Rules that make this work:

- **`proof.md` is the load-bearing file.** Every line carries a source and a date. Anything
  without one does not belong in it. The global layer will not write a number that is not here.
- **`forbidden.md` is honoured absolutely.** It beats every methodology in this family.
- Put these in the repo, not in a global file. A global proof file is exactly the cross-brand
  contamination this design exists to prevent.
- Reference them from the repo's `CLAUDE.md` so they are discovered without being asked for.

## The provenance contract

Every factual assertion carries a label:

- `[FACT]` — sourced from repo-local context, a supplied file, or a user statement. Cite where.
- `[PROPOSED]` — recommended messaging. True only if the business decides to make it true.
- `[NEEDS-INPUT]` — the copy needs it and you do not have it. Name the input.

Never invented, under any framing: customer names or quotes, results, conversion rates, pricing,
guarantees, certifications, awards, review counts, competitor claims, headcounts, or dates.

If context is missing, the correct output is the structure plus `[NEEDS-INPUT]` slots — not a
vaguer claim that avoids needing a fact. Vagueness is the symptom; the named gap is the fix.

## Naming, and what these do not replace

Deliberate boundaries against skills already in this catalogue:

| New skill | Adjacent existing skill | Boundary |
|---|---|---|
| `ad-copy` | `ads-creative`, `ads` family | Those **audit an account's** creative, fatigue, and spend. `ad-copy` **writes** copy. |
| `landing-page-copy` | `ads-landing` | `ads-landing` audits an existing page for speed, forms, and UX. This writes the copy. |
| `email-copy` | `email-ops` | `email-ops` triages a mailbox and operates sends. This writes marketing email. |
| `social-copy` | `content-engine` | `content-engine` builds multi-platform content *systems*. This writes individual posts. |
| `humanizer` | `brand-voice` | `brand-voice` derives a voice profile from published work. `humanizer` edits against one. |
| `compliance-review` | `skill-comply` | Unrelated despite the name — `skill-comply` validates this repo's skill catalogue. |
| `direct-response-copy` | `article-writing` | `article-writing` is editorial long-form. This is response-driven copy. |

`direct-response-copy` is aliased as **copy-that-sells** in its body. The folder is deliberately
*not* named `copy-that-sells`, so it cannot collide with the upstream
`avectats7/copy-that-sells` plugin skill if that is ever installed alongside it.

## Provenance of the methodology

Concepts were extracted and rewritten, not vendored:

- **Awareness stages and market sophistication** — Eugene Schwartz, *Breakthrough Advertising*.
  Long-standing public direct-response theory.
- **Anti-AI editorial rules** — informed by the approach in `avectats7/copy-that-sells` (MIT).
- **Persuasion selection by audience temperature and the anti-pattern framing** — informed by
  `MADEVAL/MindFluence` (MIT).

Neither repository was vendored. Both ship a single very large `SKILL.md` (25 KB and 92 KB), which
conflicts with this catalogue's 5–15 KB norm and with the composable-skills design. All prose here
is original.

## Updating

```bash
git switch main && git pull --ff-only
git switch -c chore/<what-you-are-doing>

# edit the SKILL.md, then update its expected_sha256 in manifests/skills.json
python -c "import hashlib;print(hashlib.sha256(open('<skill>/SKILL.md','rb').read()).hexdigest())"

python -m unittest discover -s tests
python scripts/check-skill-consistency.py
python scripts/audit-catalog-health.py --no-runtime
python scripts/deploy-skills.py --check
```

Two things bite here:

- `expected_sha256` is over **raw bytes**. `.gitattributes` pins `* -text` — write LF, never CRLF.
- `manifests/skills.json` is **CRLF with no trailing newline**. A naive `json.dump` rewrites all
  226 KB. Preserve the format or the diff is unreviewable.

Adding a skill to this family is a **MINOR** catalog bump per `docs/consolidation/RELEASING.md`.

## Adding Codex parity

These are `CLAUDE_ONLY` by scope, not by mechanism — they are plain markdown and would run in
Codex unchanged. To grant parity, set `"mode": "IDENTICAL"` and `"targets": ["claude","codex"]`
on the eleven entries and redeploy. No content change is needed.

## Rolling back

The deployer is copy/update-only and **never deletes**, so rollback restores older bytes but does
not remove skills. To remove the family entirely:

```bash
# 1. revert the source change
git revert <commit>            # or: git switch main

# 2. remove the runtime copies by hand - the deployer will not do it
rm -rf ~/.claude/skills/{copy-os,copy-strategist,direct-response-copy,persuasion-engine}
rm -rf ~/.claude/skills/{copychief,humanizer,compliance-review,landing-page-copy}
rm -rf ~/.claude/skills/{ad-copy,email-copy,social-copy}

# 3. confirm
python scripts/deploy-skills.py --check
```

To disable without removing, add each name to `skillOverrides` in `~/.claude/settings.json` with
value `"off"`. That hides them from the harness while leaving the files in place.
