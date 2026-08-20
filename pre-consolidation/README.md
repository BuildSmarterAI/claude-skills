# pre-consolidation — read-only archive

> **This directory is not a skill and contains no skills to install.**
> It is a frozen snapshot of every skill store on the authoring machine as it
> existed on **2026-08-20**, taken immediately before consolidation work began.
> Nothing here is deployed. Nothing here should be edited.

The repository's normal layout is one kebab-case folder per skill at the root
(see `CLAUDE.md`). This directory is the one deliberate exception: an archival
artifact, committed so that no unique skill, customization, or provenance can be
lost when the four competing stores are merged into one canonical source.

## Why this exists

An infrastructure audit established that:

- Four skill stores existed in parallel, holding **648 skill directories** across
  **272 distinct skill names**.
- Two of them — `~/.claude/skills` and `~/.agents/skills` — are **single-commit
  orphan git repositories** sitting on commit `f175f208`, which **does not exist
  on the remote they both declare** (`upload-pack: not our ref`) and shares
  **zero history** with it. Neither can be reconciled by git.
- Between them, **89 skills were untracked** and **50 were modified** relative to
  that unreachable commit — meaning a large body of work, including an entire
  third-party skill pack, existed in **no recoverable version control anywhere**.
- Claude and Codex read **different stores**, and **65 identically named skills
  differed in content** between them.

Consolidating without first freezing this state risked silently destroying work
that had no other copy.

## Layout

```
pre-consolidation/
├── manifest.json               provenance + per-skill content hashes
├── claude-runtime/skills/      snapshot of ~/.claude/skills      (Claude Code reads this)
├── codex-runtime/skills/       snapshot of ~/.agents/skills      (Codex reads this; its
│                                 session header declares root `r0` = this path)
├── canonical-repo/             this repo, RECORDED not copied — copying it into
│                                 itself would recurse
│   ├── tree-at-336622e.txt     full object listing at the pre-snapshot commit
│   └── history-at-336622e.txt  all 15 commits
└── everything-claude-code/     vendored upstream (affaan-m/everything-claude-code)
    ├── skills/                 provenance for the four-store comparison
    └── rules/                  provenance for the `~/.claude/rules` → `../common/` repair
```

The stores are kept **separate on purpose**. They are not merged, deduplicated,
or reconciled here — that is later work, and it needs this record to be safe.

## What `manifest.json` answers

For every skill in every store:

| Question | Field |
|---|---|
| Which source did it come from? | `sources[].key`, `sources[].source_path` |
| Which runtime consumed it? | `sources[].runtime_consumer` (+ `consumer_evidence`) |
| Was it modified? | `sources[].skills[].vcs_status` — `tracked-clean` / `modified` / `untracked` |
| Did Claude and Codex get the same instructions? | `cross_runtime_comparison` |

Hashes are `sha256` of raw bytes, plus `sha256_norm` over CRLF-normalised bytes
so that line-ending-only drift can be told apart from real divergence.

`audit_reconciliation` records where these verified counts supersede the earlier
audit's prose.

## Handling notes

- **Symlinks were dereferenced.** `archify`, `ask-matt` and `deep-research` are
  symlinks in `~/.claude/skills` pointing into `~/.agents/skills`. The archive
  stores their real content, and `manifest.json` records that they are shared
  rather than duplicated.
- **Excluded from the copy:** `.git`, `.github`, `node_modules`, virtualenvs,
  build/cache/coverage directories, and anything credential-shaped
  (`.env*`, `*.pem`, `*.key`, `credentials.json`, …). A scan confirmed no
  credential-shaped file existed in any source tree.
- **No secrets, environment values, or file contents** appear in `manifest.json`.

## Restoring from this archive

```bash
# inspect what a store held, without touching anything
jq '.sources[] | select(.key=="codex-runtime") | .skills[] | select(.vcs_status=="untracked")' \
   pre-consolidation/manifest.json

# recover one skill exactly as it was
cp -r pre-consolidation/codex-runtime/skills/<name> <destination>
```

Do not deploy this directory back to a runtime store wholesale — it is a record
of a state that was deliberately superseded.
