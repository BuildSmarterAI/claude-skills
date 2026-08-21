# Releasing the catalog

Operational runbook. For the architecture, see [`README.md`](README.md); for ownership classes,
[`skill-ownership-policy.md`](skill-ownership-policy.md).

## Three versions — do not conflate them

`catalog-version.json` declares all three:

| Field | Describes | Bumps when |
|---|---|---|
| `catalog_version` | this **release of the catalog** (semver) | per the policy below |
| `manifest_schema_version` | the **shape** of `manifests/skills.json` | its structure changes incompatibly |
| `deployment_state_schema_version` | the shape of runtime `.deployment-state.json` | that record's structure changes |

`manifest_schema_version` must equal the `schema` field inside `manifests/skills.json`.
`check-skill-consistency.py` enforces that agreement, so the version file cannot drift into being a
second, unverified place to write a number.

**Skills are not versioned individually.** One catalog version covers all of them.

## Version policy

**MAJOR** — an existing consumer must change something:
- incompatible `manifests/skills.json` schema change
- breaking change to the ownership model or its required fields
- breaking change to deployment semantics (e.g. if the deployer ever gained delete behaviour)
- removal or rename of a widely consumed capability with no compatibility path

**MINOR** — new capability, nothing breaks:
- new canonical skills
- a substantial new shared capability
- a new runtime target or adapter
- meaningful non-breaking merges/splits (a split that keeps both names reachable)

**PATCH** — no change to the public capability contract:
- wording, description and typo corrections
- provenance and metadata corrections
- classification corrections that do not change what a runtime can reach
- checker/deployer bug fixes that do not alter deployment semantics

### What does *not* bump the catalog

- editing a skill's body without changing what it can do
- manifest bookkeeping: `expected_sha256` recomputation, notes, reasons
- documentation, CI, or test changes
- exposure changes (`active` ↔ `on-demand`) — those change what is *loaded*, not what the catalog
  *contains*, and are recorded in the deployment state instead

When a change spans levels, take the highest.

## Routine: change a skill

```bash
git switch main && git pull --ff-only          # always start from main, never an old branch
git switch -c chore/<what-you-are-doing>

# edit the skill, then update its recorded hash in manifests/skills.json

python scripts/check-skill-consistency.py      # repository correctness
python -m unittest discover -s tests           # the checker's own tests
python scripts/deploy-skills.py --check        # this machine's runtime parity
```

Open a PR. The `Skill consistency` check must pass before merge.

## Routine: deploy locally

```bash
python scripts/deploy-skills.py --check        # what differs
python scripts/deploy-skills.py --dry-run      # what --deploy would do
python scripts/deploy-skills.py --deploy       # copy/update only; never deletes
python scripts/deploy-skills.py --check        # must end CLEAN
```

`--deploy` writes `.deployment-state.json` into each runtime root. `--check` and `--dry-run` never
write anything.

## Routine: cut a release

1. Merge the substantive PR first.
2. From `main`, bump `catalog_version` in `catalog-version.json` per the policy above.
3. Add a `CHANGELOG.md` section describing **durable outcomes**, not intermediate debugging.
4. Run the three commands above; all must pass.
5. Open a PR for the bump; let CI pass; merge.
6. Tag `main` only after the bump is merged:

```bash
git switch main && git pull --ff-only
git tag -a v1.0.0 -m "Catalog v1.0.0"
git push origin v1.0.0
```

Never tag a commit that CI has not passed, and never tag a dirty tree.

## Routine: inspect what a runtime is running

```bash
cat ~/.claude/skills/.deployment-state.json
cat ~/.agents/skills/.deployment-state.json
```

Attribution is `catalog_version` + `canonical_commit` + `manifest_sha256`. **A commit alone is not
sufficient** — a dirty tree, an export, or a hand-edit all share a commit while shipping different
bytes. `canonical_tree_dirty: true` means the deploy came from uncommitted work and is not
reproducible from the commit alone.

## Routine: roll back

Rollback is a deploy from an older catalog state; there is no separate mechanism.

```bash
git switch --detach v0.9.0                     # or any known-good commit
python scripts/check-skill-consistency.py      # verify that state is self-consistent
python scripts/deploy-skills.py --check        # see what would change
python scripts/deploy-skills.py --deploy
```

Because the deployer never deletes, rolling back **restores older bytes but does not remove skills
added since**. Remove those deliberately if that is what you want.

The ultimate backstop is the preservation snapshot, which predates the whole consolidation:

```bash
git show 8a756b95:pre-consolidation/claude-runtime/skills/<skill>/SKILL.md
```

Never delete `chore/pre-consolidation-skill-snapshot-2026-08-20` or
`archive/runtime-pinned-f175f20`.

## Two checks, two questions

| | `check-skill-consistency.py` | `deploy-skills.py --check` |
|---|---|---|
| Asks | is the repository internally correct? | is **this machine** in parity? |
| Reads | repo only | repo **and** runtime stores |
| Runs in CI | yes | **no** — a runner has no runtime stores |

Never wire `deploy-skills.py --check` into CI. On an empty runner it reports every declared skill
as a CREATE (measured: 246), and faking the directories to get a green tick would make the check
assert nothing.
