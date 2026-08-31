# Changelog

Catalog releases of `BuildSmarterAI/claude-skills`. Versioning policy:
[`docs/consolidation/RELEASING.md`](docs/consolidation/RELEASING.md).

The version in [`catalog-version.json`](catalog-version.json) names the **catalog**, not any
individual skill. Skills are not versioned independently.

## [1.1.0] — 2026-08-31

Adds the **Copy OS**: a reusable global copywriting and marketing-intelligence layer, and the
first skill *family* in this catalogue — eleven skills that share contracts and route to each
other rather than one skill doing everything.

### Eleven composable skills

`copy-os` routes · `copy-strategist` decides what the copy must argue · `direct-response-copy`
supplies craft · `persuasion-engine` selects angles · `landing-page-copy`, `ad-copy`,
`email-copy` and `social-copy` execute per channel · `copychief` reviews adversarially ·
`humanizer` edits · `compliance-review` gates publication.

Route length scales with the deliverable. A headline rewrite runs two stages; a full sales page
runs seven. Nothing is forced through every stage.

### Methodology global, truth local

The layer carries **no company facts** — no positioning, ICPs, offers, pricing, proof, customers,
or performance claims. Those belong to the repository the copy is written for. Two shared
contracts under `copy-os/references/` enforce it: the Copy Brief schema, and the fact-provenance
rules. Every factual assertion is labelled `[FACT]` with a source, `[PROPOSED]`, or
`[NEEDS-INPUT]`. Nothing is invented to fill a gap.

Precedence orders **judgment** — angle, positioning, tone, structure — as task > repo marketing
knowledge > repo instructions > global methodology. It does **not** order **permission**: a
repository's forbidden-claims list and substantiation are floors that nothing above them lifts, a
task prompt included.

### Deliberate boundaries

`ad-copy` writes where `ads-creative` audits; `landing-page-copy` writes where `ads-landing`
audits; `email-copy` is marketing email where `email-ops` operates a mailbox; `social-copy` writes
posts where `content-engine` builds calendars. `direct-response-copy` carries **copy-that-sells**
as a body alias rather than a folder name, so it cannot collide with the upstream plugin skill of
that name.

Deployed `CLAUDE_ONLY` by scope rather than mechanism. The skills are plain markdown and would run
in Codex unchanged; parity is a manifest change with no content change.

### Enforcement

`tests/test_copy_os_family.py` pins the properties whose loss is invisible to a reader: the
per-skill anti-fabrication sentence, the three provenance labels on generative skills, the named
hard stops, the refusal to state platform policy as settled, handoffs that name real skills, and
hash agreement with the manifest. `docs/copy-os-verification.md` records the behavioural set that
a checker cannot cover — including the cross-repo contamination test, which is the one that
reproduces the real failure mode.

### Documentation corrected

`README.md` described a deployment model retired by the 1.0.0 consolidation — cloning this
repository directly into `~/.claude/skills`. It now documents canonical source → manifest →
deployer → runtime output, with the deploy and change runbooks. `CLAUDE.md` carried the same
claim, plus seven "team aggregator" skills absent from both disk and manifest since `cb87b03`;
both corrected, with the retirement recorded so the pattern is not reintroduced.

## [1.0.0] — 2026-08-21

First versioned release. Establishes this repository as the single canonical source for every
AI-engineering skill on the machine, with deterministic deployment and enforced integrity.

### One canonical source

Four divergent skill stores were consolidated into one. Two of them were orphan git repositories
pinned to a commit that exists on no remote. The manifest at `manifests/skills.json` now governs
**288 skills**: what each one is, which runtimes receive it, who owns it, and the SHA-256 its
canonical bytes must have.

### Deterministic deployment

`scripts/deploy-skills.py` deploys canonical bytes to `~/.claude/skills` and `~/.agents/skills`.
It is hash-based rather than timestamp-based, idempotent, and **copy/update only — it never
deletes**. Runtime-only skills are reported as EXTRA for review, never removed silently.

### Claude / Codex parity model

Runtime stores are deployment *outputs*, not sources. Divergence must be declared: `IDENTICAL`,
`CLAUDE_ONLY`, `CODEX_ONLY`, or `ADAPTER` — and the divergent modes must carry a written reason.
Runtime divergence found during consolidation was overwhelmingly *corruption*, not customization:
a blind `Claude`→`Codex` substitution had produced 72 broken paths, 4 mangled `name:` fields, and
6 skills with no frontmatter, which meant they could never register at all.

### Risk-Based TDD doctrine

`risk-based-tdd` is now the single source of truth for **when** tests must come first. It replaced
contradictory guidance, including an unconditional "Always TDD" mandate. Responsibilities are
separated and no skill redefines testing order:

| Skill | Owns |
|---|---|
| `risk-based-tdd` | WHEN tests must come first |
| `superpowers:test-driven-development` | the strict RED → GREEN → REFACTOR loop |
| `tdd-workflow` | TypeScript / Vitest / Playwright HOW patterns |

### Capability splits and merges

Two same-named skills turned out to be two different capabilities and were split rather than
collapsed — recovering a dual-axis code reviewer that existed only in the Codex store:

- `code-review` (dual-axis Standards + Spec reviewer) · `code-review-patterns` (quality checklist)
- `git-workflow` (BuildSmarter conventions) · `git-workflow-patterns` (branching encyclopedia)

`python-patterns`, `python-testing` and `deep-research` were genuinely merged, preserving material
from both sides.

### Skill ownership model

Every skill now has a truthful owner. `REPO_LOCAL` requires a named `owner_repo` **and**
`owner_path`; the generic placeholder "belongs to a product repo" is rejected by CI. Classes are
defined in [`docs/consolidation/skill-ownership-policy.md`](docs/consolidation/skill-ownership-policy.md).

### Runtime description-budget reduction

Skill descriptions consume context on every turn. Codex was **over** its budget:

| Runtime | Before | After |
|---|---|---|
| Claude | 133 live · 98% | 88 live · ~68% |
| Codex | 223 live · **139%** | 91 live · ~70% |

Codex has no native disable switch, so non-active skills were **moved** to
`~/.agents/skills-disabled/`, outside the scanned root — never deleted. All 223 remain accounted
for.

### Canonical consistency CI

`scripts/check-skill-consistency.py` runs on every PR and every push to `main`. It reads only the
repository — no runtime stores, no network, no secrets — and enforces manifest validity, hash
integrity over raw bytes, frontmatter validity, ownership, state contradictions, documented
divergence, and undeclared skills. It ships with 38 tests and was verified by killing 11
deliberate mutants.

`deploy-skills.py --check` deliberately does **not** run in CI: it compares against live runtime
stores a runner does not have, and would report 246 false CREATEs.

### Preservation and rollback

Nothing was deleted at any point in the consolidation.

- `chore/pre-consolidation-skill-snapshot-2026-08-20` — 1,214-file byte-exact archive (`8a756b95`)
- `archive/runtime-pinned-f175f20` — the orphan runtime commit (`f175f208`), preserved before the
  runtime `.git` directories were retired
- `.gitattributes` pins `* -text` so line endings cannot silently invalidate the recorded hashes

### Release traceability

`catalog-version.json` names the catalog release. `deploy-skills.py` now writes
`.deployment-state.json` into each runtime root recording catalog version, canonical commit,
manifest SHA-256, timestamp and runtime — because a commit alone does not identify the bytes that
were deployed.
