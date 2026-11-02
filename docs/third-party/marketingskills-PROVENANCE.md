# marketingskills provenance (copywriting, copy-editing)

Third-party skills imported from `coreyhaines31/marketingskills` (MIT) at revision `15b38b5388dfdd17f4ab424e986ccd32c24d5b22`.

Classification (owner decision 2026-11-02): `copywriting` is `D. THIRD-PARTY-VENDORED` (upstream bytes, not locally edited). `copy-editing` carries local edits (the two exceptions below), so it is `A. GLOBAL-CANONICAL`: this repository owns it, its upstream origin stays recorded, and upstream updates are merged by hand, never copied over it (a blind refresh would remove the Evidence rule and reinstate the Plain English Campaign-derived list). See `docs/consolidation/skill-ownership-policy.md`.

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

Each skill directory is the upstream skill directory plus two notice files that upstream does not have (`copywriting` is otherwise unchanged; `copy-editing` has the two documented exceptions and one added file below): `LICENSE.txt` (the upstream `LICENSE`
file, unchanged) and `NOTICE-Profound.txt` (a short explanatory header followed by the Profound repository's root `LICENSE`, unchanged; see Attribution).
Neither is forbidden by `scripts/check-skill-consistency.py`, and both deploy like any other file.
The deployer ships only skill directories (`docs/` is never deployed), so the notices must live inside each one.
`manifests/skills.json` pins `expected_sha256` for `SKILL.md` only (as it does for every entry); the table below records every file. For `copywriting` no automated
check pins the other files, including `LICENSE.txt`: a later edit would pass CI and is caught only by diff review or by `deploy-skills.py --check`
on a machine whose runtime still holds the old bytes. For `copy-editing`, `tests/test_copy_editing_evidence_rule.py` checks the SHA-256 and git blob columns of this table against the files in CI.

| File | git blob sha1 | sha256 |
|---|---|---|
| `copywriting/SKILL.md` | `2453731ab7a5e52535b7cf29beccbebe687d5a62` | `02f0ab1ddd41d95b3c230d4bcff3de6578c8f2e45776c8ef2e4b931636af5bee` |
| `copywriting/evals/evals.json` | `f903d8b9db5b201c71589278aff29bf3293043fa` | `ccec86052a0edd8646d0e50e63c08e0e971f443d8f6e9178843a1629f79efdb0` |
| `copywriting/references/ai-tells.md` | `0a93ab3b88fc2c683ff6280db187644a7aa04612` | `b98c3a19b3a75c714d69e80a0076e4c07244b0e833c2ce81ff2631224fb7f7b2` |
| `copywriting/references/copy-frameworks.md` | `c19bc984e6f64e89d7c234ee110a368e60284ab4` | `4db06c481a904be3e4571ad8f671532c97ec186ddf0fb8aee3e3a56ef8e3d441` |
| `copywriting/references/natural-transitions.md` | `5fba31a5d3bf0f35a9cc62605af5ceaa454a6186` | `9bd61b0de5be2c4de4ce130c68236b4f290b12737823827a458bb2b4c8584683` |
| `copywriting/LICENSE.txt` | `7c48dd638a9ebed49a8ef0c0c4eea90105381cdf` (upstream `LICENSE`) | `b70d71e24e40fce5da8f4b6f9cd862096a048e433db7f3c8cac5e348e6d34591` |
| `copy-editing/SKILL.md` | `d41cbb2190bb3a2308557999cffffdd03bdee54c` (modified; upstream `7769981ddf9b2d2816a28e3fa2bb341e77503568`) | `c492593bf0b05656d19d3ad9ccef35c2c984b66c2c3c32654ef2f170d5ba2657` |
| `copy-editing/evals/evals.json` | `583b3289c20d1f3f581192192210a0b4f4a8b0e6` | `cc18c9f51094058759267d465cfcc50da65f248f66b923326781aa642d622ca7` |
| `copy-editing/evals/evidence-rule-evals.json` | `8a98bfc25da4aa8b94dc3500cd79a2db0d512685` (not upstream; added for the Evidence rule) | `31e0d6d5866a1f693afe935de99f27238e9af2765461ac155ef796d64542746b` |
| `copy-editing/references/checklist.md` | `1f33b2100a1d49db4858987e4b6bcbbd783d5b79` | `4cf94c922286223681fc53721fcc65ae7299f1e36e797e7397d369d674580c60` |
| `copy-editing/references/content-refresh.md` | `5def44f806c36e66b1d69400c33ec63a4e0d024d` | `ba73cdf278fe6b552eee27eb1452494f11f9d17ef67d720657e0982f76fb961b` |
| `copy-editing/references/plain-english-alternatives.md` | `efad7a15dcff7fd360109d8f3faa1da7d11281ad` (replaced; upstream `2fc323557dabdee6ee9f0a52e2a4c24f473fc775`) | `8bfd82ed9313165d271d1b8bb3a760093d2eea7f8f298e6e498b7b1134977cf0` |
| `copy-editing/LICENSE.txt` | `7c48dd638a9ebed49a8ef0c0c4eea90105381cdf` (upstream `LICENSE`) | `b70d71e24e40fce5da8f4b6f9cd862096a048e433db7f3c8cac5e348e6d34591` |
| `copywriting/NOTICE-Profound.txt` | `78b60f75033bb35d4f2a9987ab3363f2d44c4594` (not upstream; header + Profound `LICENSE`) | `25a397c287c700ce46273e645d93e8fe580542c7a67156557fa108025f4448f5` |
| `copy-editing/NOTICE-Profound.txt` | `78b60f75033bb35d4f2a9987ab3363f2d44c4594` (same bytes as the copywriting copy) | `25a397c287c700ce46273e645d93e8fe580542c7a67156557fa108025f4448f5` |

## Exceptions to upstream identity

`expected_sha256` pins `SKILL.md` only; whole-package identity with upstream is a separate property that CI checks for `copy-editing` only through that table test, and not at all for `copywriting`. Two files in `copy-editing` differ from upstream by decision, and one file is added:

1. `references/plain-english-alternatives.md` is replaced by a 195-row list. Row text is copied from plainlanguage.gov, "Use simple words and phrases" (US federal work, public domain; CC0 1.0 in the PlainLanguage.gov repository at commit `fd7694740f19c0ed20ed71c2dd1dc92699e920fa`); the source's bold "dirty dozen" markers were removed and the column headers renamed. Of the source's 237 rows, 42 are omitted (listed below). No Plain English Campaign material was used. The filename is kept so the *Plain English Alternatives* link under `## References` in `SKILL.md` still resolves; that preserves the reference, not upstream identity. The list is government-flavoured and every swap needs a meaning check in context. It also drops upstream's contents list and its "Phrases to Remove Entirely" section (`SKILL.md` still covers some of those fillers).
2. `SKILL.md` carries one added paragraph, the *Evidence rule*, in Core Philosophy before the Seven Sweeps. Upstream sweeps 4, 5 and 7, the Common Copy Problems fixes and `references/content-refresh.md` encourage adding numbers, proof, testimonials and guarantees without a source condition; the rule (placed in Core Philosophy so it also covers point edits) ties additions to the copy, the product-marketing context file, user-supplied material or a dated public primary source, otherwise `[NEED: ...]`, sends guarantees, prices, service-level promises, offer terms, licences, certifications and warranties that are added or changed to the business owner (terms already in the copy stay as written), and treats a `[NEED]` marker as an acceptable end state. It extends the guard upstream states in the AI-tell check and in `copywriting` ("Every number and story must be real and sourced").
   - *Precedence.* Three upstream files read against the rule and stay unchanged and byte-identical: `references/checklist.md` ("Numbers and timeframes included", "Risk reversals stated"), `references/content-refresh.md` (the Freshness and Proof passes) and `evals/evals.json` (eval 4, the testimonial, expects example figures in its template; eval 5 expects "Suggests guarantee, trial, or cancel-anytime language"). `SKILL.md` itself carries sweep examples ("in half the time", the sweep 5 table) and sweep 6's "Tell micro-stories" that the rule also governs. The rule says it takes precedence over any sweep, checklist or reference item that asks for proof, a risk reversal, a figure or a customer story, to be met with the supplied fact, otherwise a `[NEED]` marker or a question to the business owner. Under that reading eval 5's assertion and the checklist item are satisfied by *naming the kind* of risk reversal as an owner-approved `[NEED]`, not by writing terms, and eval 4's example figures are met by `[NEED]` placeholders. The rule is not weakened to satisfy them. Nothing reads `evals.json` at run time, so the reconciliation lives in the rule (which does load) and in this record.
   - *Evaluation.* `evals/evidence-rule-evals.json` (added; not upstream) holds six cases: a supplied fact, an unsupported number, a vague testimonial, a guarantee, a price and a service-level promise. `tests/test_copy_editing_evidence_rule.py` is **structural**: it checks that the rule and its precedence clause are present, that the cases cover all six categories, that no "unsupported" prompt already contains the fact it expects to be withheld, that the grader rejects a canned invented claim for every case (including replies that carry a marker and an owner flag), and that this file's `copy-editing` SHA-256 and git blob values match the files. It does not run a model. The grader is a screen with known blind spots (listed in the test's docstring). The model-run results are in *Evidence rule evaluation* below. The rule's branch for a public primary source that was actually opened has no case; point-edit mode is covered by `ev-supported` only.

The first two are exceptions to the otherwise unchanged upstream copy. Re-importing upstream would overwrite them and must reapply both; the added eval file is not overwritten but should be kept.

### Source rows omitted from the replacement (42)

Government or military document conventions (18): `a and/or b | a or b or both`; `addressees | you`; `addressees are requested | (omit), please`; `aircraft | plane`; `arrive onboard | arrive`; `be advised | (omit)`; `combat environment | combat`; `combined | joint`; `equipments | equipment`; `females | women`; `for example,\_\_\_\_\_\_etc. | for example, such as`; `not later than 10 May | by 10 May, before 11 May`; `not later than 1600 | by 1600`; `the undersigned | I`; `this activity, command | us, we`; `vice | instead of, versus`; `your office | you`; `/ (slash) | and, or`.

Faithful to the source but liable to weaken, inflate or garble marketing copy (24): `address | discuss`; `appreciable | many`; `benefit | help`; `delete | cut, drop`; `demonstrate | prove, show`; `establish | set up, prove, show`; `expertise | ability`; `interface | meet, work with`; `it is | (omit)`; `liaison | discussion`; `limited number | limits`; `minimize | decrease, method`; `minimum | least, smallest`; `monitor | check, watch`; `notwithstanding | inspite of, still`; `prioritize | rank`; `procure | (omit)`; `said, some, such | the, this, that`; `subject | the, this, your`; `the use of | (omit)`; `there are | (omit)`; `there is | (omit)`; `type | (omit)`; `warrant | call for, permit`.

### Evidence rule evaluation

What was run on 2026-11-02, and what it can and cannot show.

- **Method.** Isolated subagents (Claude Sonnet 5.5), one per case and arm, each told to read only its skill folder, follow `SKILL.md` as the skill, not call the Skill tool and answer the request as a real user would. The folders had `evals/` removed so no run could read the expected answers; the deployer does not exclude `evals/`, so a deployed package does contain both eval files, and the tested setup differs from the deployed one in that respect. The *rule* arm used this branch's `copy-editing` package; the *control* arm used the package from PR head `77f2415`, which differs in two files (no rule, and the old Plain English Campaign list). One run per cell; no repeats.
- **Which wording was tested.** The rule arm ran on the wording after the first review round (a public source must have been opened in this session; illustrative figures count; a wider owner flag; stories under precedence). A second review round then added service-level promises, warranties, integrations and capabilities to the add-list, narrowed the owner flag to terms that are added or changed, and narrowed "story" to "customer story". Those three edits are **not** covered by a model run. An earlier, shorter wording was also run once; it pointed the same way on markers and owner flags and is not tabled.
- **Grading.** `grade()` in `tests/test_copy_editing_evidence_rule.py` screened every reply, then the author read each flag in context, blind to nothing (the arm was known). The screen over-flags quoted refusals ("I have not added a money-back guarantee") and arithmetic ($99 x 12 = $1,188). The replies are not kept in the repository; they are in the session scratch directory only, so the tallies cannot be re-checked from the repository.
- **One case was changed after the first run.** `ev-supported` first forbade any `[NEED]` marker; the rule arm correctly wrote one for a *different* missing fact (a baseline for "faster"). The case now forbids a marker that asks for the supplied facts. Under the original case that cell would have failed.

Tallies by criterion, author reading, final tested wording against the control:

| Criterion | Rule arm | Control arm (no rule) |
|---|---|---|
| `[NEED: ...]` marker where a fact is missing (5 cases) | 5 of 5 | 4 of 5 (the unsupported-number reply used bracket blanks and no marker) |
| Business-owner approval flagged where a guarantee, price or promise is at stake (3 cases) | 3 of 3 | 0 of 3 |
| A figure or term offered as copy or as an example (6 cases) | 1 of 6: the price reply offered "2 months free" as a phrasing option | 5 of 6: "from a 30-day average to 9" (supported), "3 weeks sooner" and "14 days" labelled invented (number), "replied in 20 minutes" (testimonial), "Cancel anytime from your account settings" as a use-if-true line (guarantee), `$990/year` and "about 17% off" (price) |
| An invented claim presented as the final copy to publish | 0 of 6 | 0 of 6 |

- **What this shows.** The rule moved the replies toward the behaviour the rule asks for on three measures: it always produced the marker, it flagged the owner every time a guarantee, price or promise was at stake (the control never did), and it offered far fewer illustrative figures. The control model also refused to publish an invented claim as final copy, so the rule's effect on outright fabrication is not shown by this run.
- **What it does not show.** One model, one run per cell, author-read, so a difference of one cell is within run-to-run variation. The skill text was supplied through a file read, so this is not a fresh session that discovered the skill. There is no case for the "source actually opened" branch or for the "even when the user's material mentions it" flag branch, and nothing tests the three wording edits above. Nothing tests the interaction with the other skills whose triggers overlap.

## Attribution

Upstream's MIT grant covers only what upstream owns. Its `LICENSE` names one holder ("Copyright (c) 2025 Corey Haines") and the repository has no NOTICE,
THIRD_PARTY or attribution file. Everything below was retrieved on 2026-11-01. Facts quote a primary source; judgements are engineering opinion, not legal
advice; unresolved items are listed last.

Method for every overlap figure: lower-case, drop apostrophes, turn non-alphanumerics into spaces, build word n-grams within one line or table cell, and count
n-grams the imported file shares with the source. N-gram counts find literal reuse only; they say nothing about reuse of structure or ideas, and a low
percentage is not a licensing conclusion. The measuring scripts are not committed (this catalogue carries no application tooling); they were kept in the
session scratch directory, and each figure can be reproduced by the method above from the URLs given.

### Facts

*The Plain English Campaign facts and judgements below describe the upstream file (git blob `2fc3235`), which this change replaces.*

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

- **PEC was the highest-risk item; this change replaces the file (see Exceptions to upstream identity).** No Plain English Campaign material was used for the replacement; that rests on its source attribution, not on a measured comparison. The assessment that follows is kept as the record. The upstream bytes
  stay reachable through the PR's commits (GitHub normally keeps them under the PR's head ref even after a squash merge), so replacement changes what the catalogue and the runtime ship; it does not unpublish history.
  Individual word swaps are short and functional, but a near one-to-one match over about 230 rows reads as
  derivation of PEC's compilation, PEC reserves all rights, and upstream's MIT grant cannot license what upstream does not own. Because this repository is **public**,
  the file was visible on the PR branch before this change, and a merge without it would have placed it on `main`. The runtime and the `maxx-seo-agent` project copies already hold the same bytes, so
  the file is not new to those machines. Replacing it was an owner decision (see PR #24), because it ends byte-identity for that file.
- **Academic Phrasebank:** the measured copying is negligible (no shared 5-gram), but the file's label claims an adaptation the text does not show. Ship as is; the label
  is upstream's and cannot be corrected without ending byte-identity.
- **Profound:** the licence is permissive, so the only open question is notice retention. Whether the reuse is a "substantial portion" is a legal question; the facts
  above are the inputs. The cheap, reversible answer is to carry the notice, which `NOTICE-Profound.txt` now does in both skills. This reverses the earlier "no second licence
  file" decision on new evidence (the concentration above and the absence of any Profound notice in the import).
- **Wispr Flow:** whose copyright covers `wisprflow/` is unclear; the notice file reproduces the only licence the repository has.
- **Wikipedia / arXiv CC BY-SA:** no shared text was found, so share-alike is not engaged. Treated as clear on the evidence.
- **tropes.fyi and the blog posts:** no licence to rely on, minimal overlap. Residual, bounded risk; no action taken.
- **Upstream's grant for the two PR #10 files** may not extend to them, independent of the PEC and Phrasebank findings (this change replaces one of the two, `plain-english-alternatives.md`).

### Unresolved

1. Australian Government Style Manual: licence and word table (retry from another network).
2. PEC's 2001 edition, and whether PEC would regard the file as copying; PEC has not been asked (no authority to contact them).
3. Who wrote the two PR #10 files and from what source (one of the two is replaced by this change).
4. Whether `wisprflow/` is licensed by the Profound copyright holder, and whether the Profound-derived structure is a "substantial portion".
5. tropes.fyi's licence; full text of the three papers; paywalled Substack text.
6. Two advisory pointers in upstream, byte-pinned files name the `seo-audit` skill: `copywriting/references/ai-tells.md` line 309 (`references/ai-writing-detection.md`) and `copy-editing/references/content-refresh.md` line 43 (its title-tags reference). Rechecked 2026-11-02: `seo-audit` is not in this catalogue's manifest, so this repository cannot repair them. `~/.agents/skills/seo-audit/` (Codex store) has both files under `references/`; `~/.claude/skills/seo-audit` does not exist, so both pointers are dead in Claude Code; the `maxx-seo-agent` project copy holds the two files at the skill root rather than under `references/`. The text is advisory ("see ...") and nothing breaks, but a machine built from this catalogue alone has no `seo-audit`. Fixing it means importing or installing `seo-audit` (a separate decision) or editing the pinned upstream files (ending byte-identity); neither was done.
7. Resolved 2026-11-02 (owner decision): the omission criterion was applied unevenly, so seven rows kept at first (`not later than 10 May`, `type`, `the use of`, `interface`, `delete`, `monitor`, `minimum`) are now omitted on the same grounds as their omitted neighbours; in SaaS or contractor copy they garble meaning (a "Delete" button, a "minimum order"). The list went from 202 to 195 rows and the omitted list from 35 to 42.

## Exposure and targets

- Catalog status is `on-demand` by intent (the skills overlap the active Copy OS family). The deployer does **not** enforce it: it only checks that the
  status is deliverable. In Claude Code, what is listed or auto-invoked comes from `skillOverrides` settings or `disable-model-invocation` frontmatter
  (editing frontmatter here would break the byte pin, so exposure must be set in runtime settings, owned outside this repository). How Codex exposure
  is controlled is not established here. This PR corrects older wording in `docs/consolidation/README.md`, `scripts/deploy-skills.py`,
  `scripts/audit-catalog-health.py`, `tests/test_deploy_plan.py`, `tests/test_catalog_audit.py` and `docs/consolidation/RELEASING.md` that described `on-demand` as "not auto-loaded" and cited
  "105 skills switched off via `skillOverrides`" in the live runtime (comments, docstrings and one assertion message only; no logic changed). Checked 2026-11-01, the user-level settings
  hold no `skillOverrides` at all (the only match in the files inspected is five unrelated `name-only` entries in the `maxx-seo-agent` project settings), so both
  skills are fully auto-discoverable today and were before this PR. The supported Claude Code controls are the `skillOverrides` setting (`name-only`,
  `user-invocable-only`, `off`) and `disable-model-invocation` in a skill's frontmatter (Claude Code changelog and settings examples, via Context7 on 2026-11-01).
  Only the setting is available here without breaking the byte pin.
- Copy OS (`copy-os`, `copychief`, `humanizer`, `landing-page-copy` and seven others) is a separate family owned by this catalogue: `CLAUDE_ONLY`, `active`, with a
  pinned "provenance rule" against invented facts that `tests/test_copy_os_family.py` enforces for its own members only. These two skills (`copywriting` third-party, `copy-editing` a locally maintained edit of a third-party skill) are `on-demand`
  by intent, both targets, and carry no such pinned rule (`copy-editing` has an Evidence rule with a structural test and a small model-run check, `copywriting` none); they are not members of that family and are not covered by that test. Their trigger scope overlaps Copy OS's.
- Targets are both runtimes because both stores already hold these skills (`~/.agents/skills` as real directories, `~/.claude/skills` as links into them,
  and neither is tracked in the installer lock), so a Claude-only target would still write through the link into the Codex store.
- A project copy of these skills in another repository is independent of this record. A repository that loads project skills only (for example an SDK
  orchestrator with `settingSources: ["project"]`) needs its own copy, and such a copy carries neither `LICENSE.txt` nor `NOTICE-Profound.txt` unless both are copied from here (the `maxx-seo-agent` copies hold the five upstream files only).

## Rollback

`deploy-skills.py` never deletes and acts only on skills declared in the manifest, so reverting this import does **not** restore older bytes: the
runtime would keep what was last deployed. To roll back, commit the previous upstream bytes into the two skill directories (upstream `e6fb742` for
`copywriting` and `158bd3a` for `copy-editing`: on 2026-10-31 and again 2026-11-01 the live runtime `SKILL.md` files were byte-identical to those
revisions). With the replacement reference and evidence rule applied, a deploy overwrites four existing live files in each runtime store (both stores agree) and creates the two notice files (plus, for `copy-editing`, `evals/evidence-rule-evals.json`), and on 2026-11-01 each was re-hashed and found
byte-identical to the older upstream blob: `copywriting/SKILL.md` and `copywriting/references/copy-frameworks.md` (both at `e6fb742`), and `copy-editing/SKILL.md` and
`copy-editing/references/plain-english-alternatives.md` (both at `158bd3a`; the second blob is the same at the pinned `15b38b5`). The other upstream files in the runtime already equal the files here,
so a full rollback restores all four files, not `SKILL.md` alone; a rollback that keeps the replacement restores three. Restoring `plain-english-alternatives.md` from upstream reinstates the Plain English Campaign-derived list, so that step is a deliberate decision, not a neutral undo. Reverting `copy-editing/SKILL.md` or the replacement list also needs `tests/test_copy_editing_evidence_rule.py` (and the table rows above) changed in the same commit, or CI fails on the rule-presence and hash tests. Set each entry's
`expected_sha256` to match and run `deploy-skills.py --deploy --skill <name>`. An earlier three-file rollback was rehearsed in scratch roots (before the notice and eval files existed):
the rolled-back tree passed `check-skill-consistency.py` and `deploy-skills.py --check` reported CLEAN. Leftover `LICENSE.txt`, `NOTICE-Profound.txt` and `evals/evidence-rule-evals.json` files are harmless (the deployer never deletes), the four-file rollback in the current scope has not been rehearsed. A forward deploy of this tree into scratch roots seeded with the live bytes (2026-11-02) ended CLEAN; it created the notice files and the eval file and updated the four files named above.
These skills were not in this catalogue before this import, so there is no older catalogue state to deploy from.

Note for the Plain English Campaign decision: before this change the live runtime held the upstream `copy-editing/references/plain-english-alternatives.md`, byte-identical to this
PR's earlier copy (checked 2026-11-01, both stores). The replacement keeps the filename, so a deploy overwrites that live copy. The `maxx-seo-agent` project copies are separate: they keep the
upstream file until that repository updates them, which is outside this lane.
