# D2 — Canonical Skill Source Consolidation

> **This repository is the single source of truth for skills.**
> `~/.claude/skills` and `~/.agents/skills` are **deployment outputs**. Do not hand-edit them —
> edit here and run `scripts/deploy-skills.py --deploy`.

## Architecture

```
        C:\Users\harri\Documents\GitHub\claude-skills          <- authoritative Git source
                              │
                     manifests/skills.json                     <- declares deployment intent
                              │
                  scripts/deploy-skills.py                     <- deterministic, hash-based
                     --check / --dry-run / --deploy
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        ~/.claude/skills             ~/.agents/skills
         Claude Code                  Codex CLI (root `r0`)
```

`pre-consolidation/` on branch `chore/pre-consolidation-skill-snapshot-2026-08-20`
(commit `8a756b95…`) is the byte-exact preservation archive. **Never mutate it, never deploy it.**

## Why this was needed

Both runtime stores were single-commit **orphan git repositories** pinned to `f175f208` — a commit
that does not exist on the remote they both declare (`upload-pack: not our ref`) and which shares
**zero history** with it. Neither could be reconciled by git. Between them, 89 skills were untracked
and 50 modified against that unreachable commit, and **65 identically named skills differed**
between the two runtimes.

The divergence turned out not to be customization but **corruption**: a blind `Claude` → `Codex`
string substitution that produced 100 broken paths, 4 mangled frontmatter names, and 6 skills with
no frontmatter at all. See `divergence-adjudication.md`.

## Manifest

`manifests/skills.json` — one entry per skill:

| Field | Meaning |
|---|---|
| `skill`, `source` | name, and source directory in this repo |
| `targets` | `["claude"]`, `["codex"]`, or both |
| `mode` | `IDENTICAL` · `CLAUDE_ONLY` · `CODEX_ONLY` · `ADAPTER` · `DISABLED` · `REPO_LOCAL` · `VENDORED` · `HOLD` |
| `status` | `active` · `on-demand` · `repo-local` · `hold` |

`status` controls what a runtime **loads**; `mode` and `targets` control what it
**receives**. They are independent: `on-demand` is installed but not auto-loaded,
never withheld from the runtime. So a deployable entry targeting a present runtime
must exist on disk whatever its status, and `audit-catalog-health.py` reports its
absence as a violation. Settled 2026-08-24 — before that, two documents disagreed
and the catalog held exactly one on-demand entry, too few to break the tie.
| `classification` | A–J ownership class (see `skill-inventory.md`) |
| `canonical_owner`, `origin` | provenance, including vendored upstream |
| `expected_sha256` | canonical content hash |
| `divergence_decision` | which variant won, and why |

**Source retention and runtime exposure are separate decisions.** A skill can be `DISABLED` at
runtime and still fully retained here. Reducing runtime noise must never reduce source richness.

## Deployment

```bash
python scripts/deploy-skills.py --check      # report drift; exit 1 if any
python scripts/audit-catalog-health.py       # drift WITH the side attributed
python scripts/deploy-skills.py --dry-run    # describe exactly what --deploy would do
python scripts/deploy-skills.py --deploy     # copy/update runtimes
```

Safety properties: idempotent · hash-based (never mtime or size) · **copy/update only — it never
deletes a runtime skill** · runtime-only skills reported as `EXTRA` for review · refuses to run on a
missing manifest or a missing declared source · never touches `pre-consolidation/`, `scripts/`,
`docs/`, `manifests/` · byte-exact, preserving line endings · `--json` machine-readable report ·
non-zero exit on unexpected drift.

## Claude / Codex parity

**Identical by default** for tool-neutral methodology. Divergence is permitted only where the tool
surface genuinely differs — invocation syntax, Codex's lack of Agent dispatch, Claude-specific
hooks, path conventions — and **every intentional divergence is declared in the manifest** via
`mode` (`CLAUDE_ONLY` / `CODEX_ONLY` / `ADAPTER`).

Target after D2: **undocumented divergence = 0.**

## Third-party source policy

| Source | Policy | Rationale |
|---|---|---|
| **Superpowers** | **(D) reference the plugin-owned version** — never copy or fork | Actively maintained upstream, loaded as a plugin. D1's `risk-based-tdd` dispatches to it rather than rewriting it. |
| **Matt Pocock skills** (40 tracked) | **(B) track upstream + local adapter** | Installed via `.skill-lock.json` with source URLs. Keep origin metadata; add adapters rather than editing in place. |
| **everything-claude-code** | **(C) keep only selected imported skills** | Vendored third-party; we consume a subset. Never govern it. |
| **Other vendored** (`gemini-api-dev`, `find-skills`, `archify`, deep-research) | **(B) track upstream** | Each carries a `source` + `sourceUrl` in `.skill-lock.json`. |

Every vendored skill carries origin metadata in the manifest. **Do not maintain forked copies
without a real, documented customization.**

## Preservation guarantees

- Preservation snapshot `8a756b95…` untouched, 1,214 files, byte-exact.
- D1 doctrine commit `d63e893…` is the parent of this work.
- **Unaccounted-for skills = 0**: every skill in either runtime is represented in canonical source,
  declared third-party, deliberately repo-local, deliberately on-demand, or explicitly pending human
  adjudication.
- No runtime skill was deleted or disabled in D2.

## Two checks, two different questions

Both are necessary. Neither substitutes for the other.

| | `check-skill-consistency.py` | `deploy-skills.py --check` | `audit-catalog-health.py` |
|---|---|---|---|
| Question | Is the canonical repository internally correct? | Is **this machine's** runtime in parity with canonical? | Does the record still describe the world? |
| Reads | repo files only | repo **and** `~/.claude/skills`, `~/.agents/skills` | repo, runtime stores, and `origin` refs |
| Runs in CI | **yes** — the PR gate | **no** | yes, but `--no-runtime` |
| Runs locally | yes | yes — before and after every deploy | yes — this is the only place its drift section runs |

### Why the third one matters

`deploy-skills.py --check` reports *that* a runtime file differs. `audit-catalog-health.py`
reports **which side changed**, and that distinction is the whole point. On 2026-08-21 a
third-party installer overwrote `~/.claude/skills/code-review/SKILL.md`, and `--check`
reported an UPDATE that no session had caused. Without attribution the reflex is to
redeploy, which fixes the symptom until the installer runs again — so the identical
finding reappears and looks new every time.

```bash
python scripts/audit-catalog-health.py              # drift + retention vs reality
python scripts/audit-catalog-health.py --json       # machine-readable
python scripts/audit-catalog-health.py --no-runtime # what CI runs
```

It reports and never repairs. Exit 0 healthy (advisory notices allowed), 1 violations,
2 refused.

**Known limitation.** CI runs it with `--no-runtime` because a runner has no runtime
stores, and that section reports itself as `SKIPPED` rather than passing silently. So the
drift check only ever runs when a human runs it here. Until something on this machine
invokes it on a schedule, drift detection still depends on someone remembering — which by
this repository's own standard is not yet an invariant.

`deploy-skills.py --check` must never run in GitHub Actions. A clean runner has no
runtime stores, so it reports every declared skill as a CREATE — measured at **246**
on an empty runner — and the failure looks like catastrophic drift rather than a
missing precondition. Faking those directories to make CI green would make the
check assert nothing at all.

Conversely `check-skill-consistency.py` can never tell you whether your machine is
deployed correctly. It does not look at a runtime store.

### What CI enforces

Manifest validity (unique ids, required fields, mode/status/target enums) · canonical
hash integrity over raw bytes · frontmatter validity and name/directory agreement ·
`REPO_LOCAL` ownership (a named `owner_repo` **and** `owner_path`, placeholder phrasing
rejected) · state contradictions (`active` + `DISABLED`) · holds carrying a
`hold_reason` · documented `intentional_divergence` for `CLAUDE_ONLY` / `CODEX_ONLY` /
`ADAPTER` · skills present on disk but undeclared.

The 1,214-file `pre-consolidation/` archive is rollback evidence, not deploy input, and
is deliberately excluded from validation and hashing.

> **If correctness depends on someone remembering to run a local command, it is not yet
> an invariant.** That is why these moved into CI.
