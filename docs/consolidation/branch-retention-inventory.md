# Branch retention inventory

Generated against `origin/main` `6470d65f` (catalog **v1.0.0**). Policy: [`RETENTION.md`](RETENTION.md).

**No branch was deleted in the session that produced this inventory.** Classification first, retirement second.

## Summary

| Class | Count |
|---|---:|
| MERGED-IMPLEMENTATION | 3 |
| PERMANENT-PRESERVATION | 2 |

6 remote branches exist including `main`. Two branches named as candidates in the original plan — `chore/catalog-versioning` and `chore/normalize-21st-skills` — **no longer exist remotely**: the repository has `delete_branch_on_merge` enabled, so GitHub retired them automatically at merge. Stale local tracking refs remain and are pruned with `git fetch --prune` plus a local `git branch -D`.

## Inventory

| Branch | Class | PR | Content on main? | Unique tip content | Preservation role | Expiry | Recommendation |
|---|---|---|---|---:|---|---|---|
| `chore/canonical-risk-based-tdd` | MERGED-IMPLEMENTATION | (none — content landed via #3) | **no** | 1 | no | 2026-09-20 (30 days after the merge that carried it) | Retire on or after **2026-09-20** |
| `chore/canonical-skill-source-consolidation` | MERGED-IMPLEMENTATION | #3 MERGED (squash `de06054`) | yes (superseded states only) | 0 | no | 2026-09-20 (30 days after merge) | Retire on or after **2026-09-20** |
| `claude/add-claude-documentation-IaLZN` | MERGED-IMPLEMENTATION | #1 MERGED | yes | 0 | no | expired | **RETIRED 2026-08-24** — tip `9fc33a67` |
| `archive/runtime-pinned-f175f20` | PERMANENT-PRESERVATION | (none) | **no** | 57 | yes | indefinite | **KEEP INDEFINITELY** |
| `chore/pre-consolidation-skill-snapshot-2026-08-20` | PERMANENT-PRESERVATION | (none) | **no** | 913 | yes | indefinite | **KEEP INDEFINITELY** |

## Evidence per branch

### `chore/canonical-risk-based-tdd`

- **Class:** MERGED-IMPLEMENTATION · **tip:** `d63e8937` · **last commit:** 2026-08-20 · **files:** 225
- **Purpose:** D1: created the canonical risk-based TDD doctrine (`d63e893`).
- **Protects against:** Nothing not already on main.
- **Containment evidence:** `risk-based-tdd/SKILL.md` is **blob-identical** on branch and main (`1619d428aaf3`) — the deliverable is preserved verbatim. Its single main-absent blob is the pre-D3.6 `tdd-workflow/SKILL.md` (7,271 b), superseded by main's merged 10,220 b version.
- **Retention:** 2026-09-20 (30 days after the merge that carried it) — Retire on or after **2026-09-20**

### `chore/canonical-skill-source-consolidation`

- **Class:** MERGED-IMPLEMENTATION · **tip:** `0e297f56` · **last commit:** 2026-08-21 · **files:** 396
- **Purpose:** D1–D4.3: the whole consolidation — canonical import, manifest, deploy tooling, ownership model, consistency CI.
- **Protects against:** Nothing not already on main.
- **Containment evidence:** 16 blobs absent from main history but **0 tip-tree paths** carry them — all are intermediate commit states superseded before merge. Content shipped in v1.0.0.
- **Retention:** 2026-09-20 (30 days after merge) — Retire on or after **2026-09-20**

### `claude/add-claude-documentation-IaLZN`

- **Class:** MERGED-IMPLEMENTATION · **tip:** `9fc33a67` · **last commit:** 2026-04-28 · **files:** 289
- **Purpose:** Added the top-level CLAUDE.md repo guide.
- **Protects against:** Nothing.
- **Containment evidence:** **0 blobs absent from main history** — the only branch that is also a true ancestor of main. Fully contained by every measure.
- **Retention:** expired — **RETIRED 2026-08-24**
- **Deleted tip:** `9fc33a672688ccc308461cabc00dc3261282a023`
- **Recovery:** `git push origin 9fc33a672688ccc308461cabc00dc3261282a023:refs/heads/claude/add-claude-documentation-IaLZN` recreates it verbatim while the object
  survives on the remote. Containment was re-verified immediately before deletion:
  0 blobs absent from `main` history, 0 orphaned and 0 divergent tip paths.

### `archive/runtime-pinned-f175f20`

- **Class:** PERMANENT-PRESERVATION · **tip:** `f175f208` · **last commit:** 2026-03-30 · **files:** 183
- **Purpose:** The commit both runtime `.git` directories were pinned to (`f175f208`), captured before those directories were retired in D4.
- **Protects against:** Loss of the runtime-side history. `f175f208` exists on no upstream remote (`upload-pack: not our ref`); this branch is the only place it survives.
- **Containment evidence:** 57 blobs on 57 tip-tree paths absent from main history — genuinely unique content, not superseded states. Reachable remotely.
- **Retention:** indefinite — **KEEP INDEFINITELY**

### `chore/pre-consolidation-skill-snapshot-2026-08-20`

- **Class:** PERMANENT-PRESERVATION · **tip:** `8a756b95` · **last commit:** 2026-08-20 · **files:** 1438
- **Purpose:** Byte-exact archive of all four skill stores as they existed before D2 touched anything: 1,214 files under `pre-consolidation/`, plus canonical-repo tree and history listings.
- **Protects against:** Total loss of the pre-consolidation state. This is the only copy of the four original stores, including the two orphan runtime repos that were pinned to a commit existing on no remote.
- **Containment evidence:** 501 blobs, on 913 tip-tree paths, exist nowhere in main history. Snapshot commit `8a756b95` reachable remotely. Cited by 8 documents including CHANGELOG.md and RELEASING.md.
- **Retention:** indefinite — **KEEP INDEFINITELY**

## Method

Containment was established by **blob**, not by ancestry or diff. Every blob reachable from each branch (across all its commits) was tested for membership in the set of blobs reachable from `main` (18 commits, 530 distinct blobs). Ancestry would have been wrong for 4 of 5 branches, because every PR here is squash-merged.

A branch-only blob matters **only if a path in the branch tip tree still carries it**. Otherwise it is an intermediate state that was superseded before merge, and deleting the branch loses nothing.

Also verified: no `.deployment-state.json`, manifest entry, or document depends on a retirement candidate by name, and no worktree has one checked out.
