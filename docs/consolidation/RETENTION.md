# Branch retention policy

> **A merged branch is disposable only when its content is preserved. A preservation branch is
> valuable precisely because it is not.** Never use branch age or ancestry alone as a deletion
> criterion.

Companion inventory: [`branch-retention-inventory.md`](branch-retention-inventory.md).
Machine-readable: [`../../manifests/retention.json`](../../manifests/retention.json).

## Why ancestry is not evidence

Every PR in this repository is **squash-merged**. A squash preserves the tree and discards the
commits, so `git branch --merged` and `git merge-base --is-ancestor` both report a fully-merged
branch as *unmerged*. Measured here: 4 of 5 non-main branches are not ancestors of `main`, yet two
of them are entirely represented on it.

Diffing a branch against `main` is equally misleading in the other direction — an old branch always
differs, because `main` moved on.

**The correct test is blob containment:** does every blob the branch introduced exist somewhere in
`main`'s history?

```bash
# every blob reachable from a ref, across all its commits
git rev-list <ref> | while read c; do git ls-tree -r "$c"; done | awk '{print $3}' | sort -u
```

A blob present in `main`'s history cannot be lost by deleting the branch. A blob absent from it can.

Distinguish two kinds of "missing" blob:

- **absent, and on no live path** — an intermediate commit state superseded before merge. Not
  content loss; the file's final state is on `main`.
- **absent, and carried by a path in the branch's tip tree** — real content that exists nowhere
  else. **Not disposable.**

## Branch classes

### 1. PERMANENT-PRESERVATION

Snapshots, runtime-pinned archives, disaster-recovery and forensic rollback refs — content that
exists nowhere else and predates or falls outside the canonical lineage.

**Retention: indefinite.** Deletion requires explicit human approval *and* proof that an equivalent
preservation artifact exists elsewhere. These are not cleaned up, not "tidied", and not merged.

### 2. RELEASE-CRITICAL

Refs needed to reconstruct a released catalog. Retain at least until a durable tag or release
supersedes them. Once release lineage is carried by annotated tags, prefer the tag and reclassify
the branch.

### 3. MERGED-IMPLEMENTATION

Ordinary feature/chore branches fully represented on `main`.

**Retention: 30 days after merge**, so a rollback window outlives the merge. Deletable only when
every item in the checklist below passes.

### 4. TEMPORARY-ROLLBACK

Short-lived refs created during a risky migration. **Retention: 30–90 days by risk**, and each one
must carry an explicit expiry date at creation. A rollback ref with no expiry becomes an
accidental permanent ref.

### 5. ACTIVE

In-flight work, or any branch checked out in a worktree. **Never deleted automatically.**

### 6. UNCERTAIN

Anything whose purpose or containment cannot be established. **Never deleted automatically** —
escalate for human review. Uncertainty is a reason to keep, never a reason to delete.

## Retirement checklist

Every deletion must pass **all** of these:

- [ ] remote `main` healthy; checker PASS
- [ ] the release/tag containing the work is healthy
- [ ] PR merged, or equivalent documented evidence
- [ ] branch is not ACTIVE
- [ ] no worktree has the branch checked out
- [ ] no open PR targets it
- [ ] no unique unpreserved commits
- [ ] **squash-aware blob containment established** — no tip-tree path holds a blob absent from
      `main` history
- [ ] no preservation role
- [ ] no `.deployment-state.json`, manifest, or doc depends on the branch name
- [ ] rollback window expired
- [ ] deletion recorded in the inventory

**If any check fails, do not delete.** A failed check is a finding, not an obstacle to route
around.

## Deleting safely

Record the tip SHA first — a deleted branch is recoverable only if its SHA is known:

```bash
git rev-parse origin/<branch>          # record this in the inventory
git push origin --delete <branch>
git branch -D <branch>                 # local copy, only after the remote is gone
```

Never use wildcard or bulk deletion. One branch, one verification, one record.

## What this policy does not cover

Tags are not branches. `v1.0.0` and any future release tag are immutable release identity: never
retag, never move, never delete. See [`RELEASING.md`](RELEASING.md).
