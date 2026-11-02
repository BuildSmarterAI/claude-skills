# marketingskills provenance (copywriting, copy-editing)

Third-party skills imported from `coreyhaines31/marketingskills` (MIT) at revision `15b38b5388dfdd17f4ab424e986ccd32c24d5b22`.

## Reproduce

```bash
# upstream blob shas for the shipped files (run from anywhere; needs gh)
gh api "repos/coreyhaines31/marketingskills/git/trees/15b38b5388dfdd17f4ab424e986ccd32c24d5b22?recursive=1" \
  --jq '.tree[] | select(.type=="blob" and ((.path|startswith("skills/copywriting/")) or (.path|startswith("skills/copy-editing/")) or .path=="LICENSE")) | "\(.sha) \(.path)"'
# local blob sha (run from the repo root; .gitattributes pins `* -text`, so these are comparable)
git hash-object copywriting/SKILL.md
# local sha256, for the second column
sha256sum copywriting/SKILL.md
```

Each skill directory is the upstream skill directory unchanged, plus two notice files that upstream does not have: `LICENSE.txt` (the upstream `LICENSE`
file, unchanged) and `NOTICE-Profound.txt` (a short explanatory header followed by the Profound repository's root `LICENSE`, unchanged; see Attribution).
Neither is forbidden by `scripts/check-skill-consistency.py`, and both deploy like any other file.
The deployer ships only skill directories (`docs/` is never deployed), so the notices must live inside each one.
`manifests/skills.json` pins `expected_sha256` for `SKILL.md` only (as it does for every entry); the table below records every file. No automated
check pins the other files, including `LICENSE.txt`: a later edit would pass CI and is caught only by diff review or by `deploy-skills.py --check`
on a machine whose runtime still holds the old bytes.

| File | git blob sha1 | sha256 |
|---|---|---|
| `copywriting/SKILL.md` | `2453731ab7a5e52535b7cf29beccbebe687d5a62` | `02f0ab1ddd41d95b3c230d4bcff3de6578c8f2e45776c8ef2e4b931636af5bee` |
| `copywriting/evals/evals.json` | `f903d8b9db5b201c71589278aff29bf3293043fa` | `ccec86052a0edd8646d0e50e63c08e0e971f443d8f6e9178843a1629f79efdb0` |
| `copywriting/references/ai-tells.md` | `0a93ab3b88fc2c683ff6280db187644a7aa04612` | `b98c3a19b3a75c714d69e80a0076e4c07244b0e833c2ce81ff2631224fb7f7b2` |
| `copywriting/references/copy-frameworks.md` | `c19bc984e6f64e89d7c234ee110a368e60284ab4` | `4db06c481a904be3e4571ad8f671532c97ec186ddf0fb8aee3e3a56ef8e3d441` |
| `copywriting/references/natural-transitions.md` | `5fba31a5d3bf0f35a9cc62605af5ceaa454a6186` | `9bd61b0de5be2c4de4ce130c68236b4f290b12737823827a458bb2b4c8584683` |
| `copywriting/LICENSE.txt` | `7c48dd638a9ebed49a8ef0c0c4eea90105381cdf` (upstream `LICENSE`) | `b70d71e24e40fce5da8f4b6f9cd862096a048e433db7f3c8cac5e348e6d34591` |
| `copy-editing/SKILL.md` | `7769981ddf9b2d2816a28e3fa2bb341e77503568` | `cec5a771ce37ade292f7f1f6b418e8a6ce6ec3f50163fa5e664afbcb03e085fc` |
| `copy-editing/evals/evals.json` | `583b3289c20d1f3f581192192210a0b4f4a8b0e6` | `cc18c9f51094058759267d465cfcc50da65f248f66b923326781aa642d622ca7` |
| `copy-editing/references/checklist.md` | `1f33b2100a1d49db4858987e4b6bcbbd783d5b79` | `4cf94c922286223681fc53721fcc65ae7299f1e36e797e7397d369d674580c60` |
| `copy-editing/references/content-refresh.md` | `5def44f806c36e66b1d69400c33ec63a4e0d024d` | `ba73cdf278fe6b552eee27eb1452494f11f9d17ef67d720657e0982f76fb961b` |
| `copy-editing/references/plain-english-alternatives.md` | `2fc323557dabdee6ee9f0a52e2a4c24f473fc775` | `df4f820d4c63ae8a517c64a243c101658352cd07d002355bf3c97de0a00f3775` |
| `copy-editing/LICENSE.txt` | `7c48dd638a9ebed49a8ef0c0c4eea90105381cdf` (upstream `LICENSE`) | `b70d71e24e40fce5da8f4b6f9cd862096a048e433db7f3c8cac5e348e6d34591` |
| `copywriting/NOTICE-Profound.txt` | `78b60f75033bb35d4f2a9987ab3363f2d44c4594` (not upstream; header + Profound `LICENSE`) | `25a397c287c700ce46273e645d93e8fe580542c7a67156557fa108025f4448f5` |
| `copy-editing/NOTICE-Profound.txt` | `78b60f75033bb35d4f2a9987ab3363f2d44c4594` (same bytes as the copywriting copy) | `25a397c287c700ce46273e645d93e8fe580542c7a67156557fa108025f4448f5` |

## Attribution

Upstream's MIT grant covers only what upstream owns. Its `LICENSE` names one holder ("Copyright (c) 2025 Corey Haines") and the repository has no NOTICE,
THIRD_PARTY or attribution file. Everything below was retrieved on 2026-11-01. Facts quote a primary source; judgements are engineering opinion, not legal
advice; unresolved items are listed last.

Method for every overlap figure: lower-case, drop apostrophes, turn non-alphanumerics into spaces, build word n-grams within one line or table cell, and count
n-grams the imported file shares with the source. N-gram counts find literal reuse only; they say nothing about reuse of structure or ideas, and a low
percentage is not a licensing conclusion. The measuring scripts are not committed (this catalogue carries no application tooling); they were kept in the
session scratch directory, and each figure can be reproduced by the method above from the URLs given.

### Facts

**Plain English Campaign (PEC), `copy-editing/references/plain-english-alternatives.md`.** The file's line 5 cites "Plain English Campaign A-Z of Alternative Words
(2001), Australian Government Style Manual (2024), plainlanguage.gov".
- PEC's A-Z PDF (the 2024 edition; the 2001 edition was not retrievable) states: "Plain English Campaign owns the copyright on this guide. You must not copy it
  without getting our permission first." Its site states "Copyright © 2026 Plain English Campaign. All rights reserved." and, on the free-guides page, that use
  "in your own publications or on your website" needs permission (https://www.plainenglish.co.uk/free-guides).
- Of the file's 238 table rows, 233 (97.9%) have a complex term that is a headword in PEC's A-Z, 202 (84.9%) have every listed alternative in PEC's entry, and
  the file's headwords cover about half (236 of 475 lines) of PEC's list. No row is long enough to share an 8-word sequence; 21 of 33 distinct row-level
  5-grams are shared, which is an artefact of rows being very short. Re-run once in this session from the saved download: 233 headwords, 97.9%.
- plainlanguage.gov's word list is a US government work, public domain/CC0 (GSA/plainlanguage.gov `LICENSE.md`, "You can copy, modify, distribute and perform the
  work, even for commercial purposes, all without asking permission"). 34.5% of the file's rows have a headword there.
- The Australian Government Style Manual's terms and word table were **not** retrieved (the site timed out on every attempt). Unmeasured.

**Academic Phrasebank, `copywriting/references/natural-transitions.md`.** Line 5: "Adapted from: University of Manchester Academic Phrasebank (2023), Plain English
Campaign, web content best practices".
- Manchester's copyright notice: "Material published by The University of Manchester on these web pages is copyright The University of Manchester and may not
  be reproduced without permission." No licence or permitted-reuse statement was found.
- Against the Phrasebank section pages fetched: 0 shared 5-word sequences, 0 shared 8-word sequences. 5 of the file's 76 phrases of three or more words appear verbatim, all generic
  connectives or hedges ("As a result,...", "Because of this,...", "in most cases"). Against PEC's A-Z and PEC's "How to write in plain English": 0 shared.

**`copywriting/references/ai-tells.md` sources.** Wikipedia "Signs of AI writing" (CC BY-SA 4.0): 0 shared 5-grams. tropes.fyi, Guo, Stockton, EQ-Bench and the
counter-view post share 1-4 generic 5-grams each and no 8-grams (for example "it's not X, it's Y"). Terms found: arXiv 2406.07016 CC BY-SA 4.0; arXiv 2510.15061 CC BY 4.0;
COLING 2025 paper CC BY 4.0; EQ-Bench slop lists MIT (Sam Paech); Guo, Stockton and the counter-view post show a copyright notice only; tropes.fyi shows no licence
(its file says "Add it to your AI assistant's system prompt or context") and two readers have asked for one. Only abstract or landing pages of the three papers were read.

**Upstream provenance of two files.** `plain-english-alternatives.md` and `natural-transitions.md` were added in upstream commit `91d2e6d` (2026-01-26),
"Cherry-picked the genuinely unique content from PR #10". PR #10 was opened by `bensabic` and closed without merging. Who wrote that content, and from what source, is
not stated. `ai-tells.md` was committed by Corey Haines (`12188f1`, `115c907`).

**Profound and Wispr Flow.** The credits inside the upstream files: `copywriting/SKILL.md` line 77 ("adapted from Profound's `improved-copywriting` skill ... (MIT),
re-expressed for this skill"), `copy-editing/references/checklist.md` line 26 (Profound's `improved-copywriting`, Wispr Flow's `copy-editing`), and
`copywriting/references/ai-tells.md` line 306 (Profound's `humanizer` and `improved-copywriting`, Wispr Flow's `writing`).
- `github.com/retieedra-profound/skills-marketing-library` at `80293f156c27d3f90aedebfb3c27309769b2eec6` has one licence file, the root `LICENSE`: MIT, "Copyright (c)
  2026 Profound". `profound/` and `wisprflow/` have no licence or notice of their own. The `wisprflow/` README says "Skills by the Wisprflow team"; the repository does
  not say whether the Profound holder licenses that folder.
- MIT requires: "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software." None of the three
  credits reproduces the copyright line or the permission text, and upstream's own `LICENSE` does not carry them.
- Measured overlap with the Profound/Wispr files is concentrated, not spread: `copywriting/SKILL.md` against `profound/improved-copywriting` shares 52 5-grams
  (3.35% of the imported file) and 16 8-grams (1.29%), including verbatim sentences ("plain, specific, and declarative. A page gets one or two punchy moments"). The other
  pairs measured in this session (`copywriting/references/ai-tells.md`, `copy-editing/SKILL.md` and `checklist.md`, each against the four Profound/Wispr skills, and
  `copywriting/SKILL.md` against the other three) share 0 8-grams; the remaining imported files were not paired with these sources. The earlier whole-corpus figure
  (21 of 13,273 8-grams, 0.16%, ten imported files against the repository's 24 text files) is an average that hides this concentration; its working is not preserved.
- Structural reuse (same ordered items, wording changed): the A/B/C situation diagnosis, the three-question gate and its keep/sharpen/rewrite rule, and "decompose and lock"
  in `copywriting/SKILL.md`; the same A/B/C modes in `checklist.md`; the five "build a writer" questions and the seven human-writing traits, in order, in `ai-tells.md`
  against `humanizer`. Roughly a dozen ordered units across three files.
- The credit to Wispr Flow's `copy-editing` in `checklist.md` could not be supported: that skill has no mode or point-edit taxonomy; one example sentence is shared.

### Judgements (engineering, not legal advice)

- **PEC is the highest-risk item and is not resolved here.** Individual word swaps are short and functional, but a near one-to-one match over about 230 rows reads as
  derivation of PEC's compilation, PEC reserves all rights, and upstream's MIT grant cannot license what upstream does not own. Because this repository is **public**,
  the file is visible on the PR branch today, and a merge would place it on `main`. The runtime and the `maxx-seo-agent` project copies already hold the same bytes, so
  the file is not new to those machines. This needs an owner decision (see PR #24), not a silent edit: removing or replacing the file ends byte-identity.
- **Academic Phrasebank:** the measured copying is negligible (no shared 5-gram), but the file's label claims an adaptation the text does not show. Ship as is; the label
  is upstream's and cannot be corrected without ending byte-identity.
- **Profound:** the licence is permissive, so the only open question is notice retention. Whether the reuse is a "substantial portion" is a legal question; the facts
  above are the inputs. The cheap, reversible answer is to carry the notice, which `NOTICE-Profound.txt` now does in both skills. This reverses the earlier "no second licence
  file" decision on new evidence (the concentration above and the absence of any Profound notice in the import).
- **Wispr Flow:** whose copyright covers `wisprflow/` is unclear; the notice file reproduces the only licence the repository has.
- **Wikipedia / arXiv CC BY-SA:** no shared text was found, so share-alike is not engaged. Treated as clear on the evidence.
- **tropes.fyi and the blog posts:** no licence to rely on, minimal overlap. Residual, bounded risk; no action taken.
- **Upstream's grant for the two PR #10 files** may not extend to them, independent of the PEC and Phrasebank findings.

### Unresolved

1. Australian Government Style Manual: licence and word table (retry from another network).
2. PEC's 2001 edition, and whether PEC would regard the file as copying; PEC has not been asked (no authority to contact them).
3. Who wrote the two PR #10 files and from what source.
4. Whether `wisprflow/` is licensed by the Profound copyright holder, and whether the Profound-derived structure is a "substantial portion".
5. tropes.fyi's licence; full text of the three papers; paywalled Substack text.

## Exposure and targets

- Catalog status is `on-demand` by intent (the skills overlap the active Copy OS family). The deployer does **not** enforce it: it only checks that the
  status is deliverable. In Claude Code, what is listed or auto-invoked comes from `skillOverrides` settings or `disable-model-invocation` frontmatter
  (editing frontmatter here would break the byte pin, so exposure must be set in runtime settings, owned outside this repository). How Codex exposure
  is controlled is not established here. Older text in `docs/consolidation/README.md` and `scripts/deploy-skills.py` describes `on-demand` as "not
  auto-loaded"; read that as the catalog's intent, not as something the deployer performs. A comment in `scripts/deploy-skills.py` (line 51) and the docstring of
  `tests/test_deploy_plan.py` (line 12) cite "105 skills switched off via `skillOverrides`" in the live runtime; checked 2026-11-01, the user-level settings hold no
  `skillOverrides` at all (the only match in the files inspected is five unrelated `name-only` entries in the `maxx-seo-agent` project settings), so both skills
  are fully auto-discoverable today and were before this PR. The supported Claude Code controls are the `skillOverrides` setting (`name-only`,
  `user-invocable-only`, `off`) and `disable-model-invocation` in a skill's frontmatter (Claude Code changelog and settings examples, via Context7 on 2026-11-01).
  Only the setting is available here without breaking the byte pin.
- Copy OS (`copy-os`, `copychief`, `humanizer`, `landing-page-copy` and seven others) is a separate family owned by this catalogue: `CLAUDE_ONLY`, `active`, with a
  pinned "provenance rule" against invented facts that `tests/test_copy_os_family.py` enforces for its own members only. These two skills are third-party, `on-demand`
  by intent, both targets, and carry no such rule; they are not members of that family and are not covered by that test. Their trigger scope overlaps Copy OS's.
- Targets are both runtimes because both stores already hold these skills (`~/.agents/skills` as real directories, `~/.claude/skills` as links into them,
  and neither is tracked in the installer lock), so a Claude-only target would still write through the link into the Codex store.
- A project copy of these skills in another repository is independent of this record. A repository that loads project skills only (for example an SDK
  orchestrator with `settingSources: ["project"]`) needs its own copy, and such a copy carries neither `LICENSE.txt` nor `NOTICE-Profound.txt` unless both are copied from here (the `maxx-seo-agent` copies hold the five upstream files only).

## Rollback

`deploy-skills.py` never deletes and acts only on skills declared in the manifest, so reverting this import does **not** restore older bytes: the
runtime would keep what was last deployed. To roll back, commit the previous upstream bytes into the two skill directories (upstream `e6fb742` for
`copywriting` and `158bd3a` for `copy-editing`: on 2026-10-31 and again 2026-11-01 the live runtime `SKILL.md` files were byte-identical to those
revisions), set each entry's `expected_sha256` to match, and run `deploy-skills.py --deploy --skill <name>`. This was rehearsed in scratch roots:
the rolled-back tree passed `check-skill-consistency.py` and `deploy-skills.py --check` reported CLEAN. Leftover `LICENSE.txt` and `NOTICE-Profound.txt` files are harmless (the deployer never deletes), and the rehearsal predates the notice files.
These skills were not in this catalogue before this import, so there is no older catalogue state to deploy from.
