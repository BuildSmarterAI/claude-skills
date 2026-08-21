# D4 Runtime Activation — APPLIED

> Applied 2026-08-21. Every change on this page is reversible; nothing was deleted.

## Result

| Runtime | Live before | Live after | Tokens before | Tokens after | % of ~10k |
|---|---:|---:|---:|---:|---:|
| Claude | 133 | **87** | 9,776 | **6,722** | 98% → **67%** |
| Codex | 223 | **88** | 13,930 | **6,465** | 139% → **65%** |

Codex was **over** its description budget; both runtimes are now under it.

## Mechanism — the two runtimes differ

**Claude** disables declaratively: `skillOverrides` in `~/.claude/settings.json`, 59 → **105**
entries, all `"off"`. No file moved. Reversal = delete the key.

**Codex has no native disable mechanism.** `~/.agents/.skill-lock.json` is an *install ledger*
(44 tracked of 223 on disk); its `dismissed` field holds only `{"findSkillsPrompt": true}`, and no
Codex config references skills at all. So **135** non-active skills were **moved**, not deleted, to
`~/.agents/skills-disabled/`, outside the scanned root. `manifest.json` there records every move
with its source path and sha256 (0 hash failures). Reversal = move the directory back.
223 skills remain accounted for: 88 live + 135 staged.

## Deviation from plan: 15 skills deliberately retained

The plan targeted ~50%. It landed at 67% / 65% because **15 skills classified `repo-local` are
provided by no repository.** The classification is aspirational: all 35 `repo-local` entries carry
only the generic note "belongs to a product repo", and a scan of every repo under
`Documents/GitHub` found no copy of the `ads-*` family or `construction-industry`.

Disabling them would have deleted the capability outright — including the skill-side counterpart of
the live ad-audit agent fleet (`audit-budget`, `audit-creative`, `audit-google`, `audit-hyros`,
`audit-meta`, `audit-tracking`, `audit-compliance`) and construction-domain knowledge at a
commercial construction firm. They stay exposed until a repository actually owns them.

**Follow-up:** move the `ads-*` family and `construction-industry` into their owning product repo,
then disable globally. That reclaims the remaining ~16 points.

## Runtime git retired

Both runtime roots were single-commit git repos pinned to `f175f208…`, a commit on no remote, with
136 / 218 uncommitted files — so a stray `git checkout .` would have reverted the whole deployment.
The commit was first pushed to `origin/archive/runtime-pinned-f175f20` (183 files), then each
`.git` was **renamed** to `.git-retired-f175f20` rather than deleted, keeping the step reversible.

## Verification

- `deploy-skills.py --check` → **CLEAN**, `to CREATE: 0` — the deploy system does not re-create
  staged skills, so the reduction is stable.
- 13 D3.6 improvements deployed to runtime; 0 files deleted.
- `settings.json`: 15 top-level keys before and after, none lost, only `skillOverrides` changed.
  Backup at `settings.json.pre-d4.bak`.
- Registration spot-check across both runtimes: **0 failures**.
- Preservation snapshot `8a756b95…` unchanged at **1,214** files.
