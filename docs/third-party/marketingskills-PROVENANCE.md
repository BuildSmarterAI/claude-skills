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

Each skill directory is the upstream skill directory unchanged, plus `LICENSE.txt` (the upstream `LICENSE` file, unchanged). It is the first licence
file inside a skill directory in this catalogue; nothing in `scripts/check-skill-consistency.py` forbids it, and it deploys like any other file.
The deployer ships only skill directories (`docs/` is never deployed), so the notice must live inside each one.
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

## Attribution

### Profound and Wispr Flow (credited inside the upstream files)

`copywriting/SKILL.md` (line 77) says its diagnosis, gate and decompose-and-lock material is "adapted from Profound's `improved-copywriting` skill
... (MIT), re-expressed for this skill". `copy-editing/references/checklist.md` (line 26) credits Profound's `improved-copywriting` and Wispr Flow's
`copy-editing`; `copywriting/references/ai-tells.md` (line 306) credits Profound's `humanizer` and `improved-copywriting` and Wispr Flow's `writing`.
Wispr Flow's skills are published in the same repository: `github.com/retieedra-profound/skills-marketing-library` (MIT).

Check, run once on 2026-11-01 against that repository at commit `80293f156c27d3f90aedebfb3c27309769b2eec6`: lower-case both sides, strip URLs and
punctuation, and count 8-word sequences shared between the ten imported files and the 24 `.md`/`.txt`/`.json` files of that repository (this includes
the `profound/` and `wisprflow/` directories). Result: 21 shared sequences out of 13,273 (0.16%). Most are generic trigger phrasing in the frontmatter
description; 4 short phrases in `copywriting/references/ai-tells.md` match Profound's `humanizer`. The script is not committed (this catalogue carries no
application tooling), so the figure is reproducible only from this description.

Judgement: that is not a substantial portion of the work, upstream's own credit lines are preserved in the files, and no second licence file is shipped.
This is an engineering judgement, not legal advice. If the four phrases matter, the remedy is to add the Profound repository's MIT notice next to this one.

### Open item: other sources named inside the upstream files (not measured, not resolved)

Upstream's MIT grant covers only what upstream owns. These files name third-party sources whose terms are not stated in this repository:

- `copywriting/references/natural-transitions.md` line 5: "Adapted from: University of Manchester Academic Phrasebank (2023), Plain English Campaign".
- `copy-editing/references/plain-english-alternatives.md` line 5: Plain English Campaign A-Z of Alternative Words (2001), Australian Government Style Manual
  (2024), plainlanguage.gov.
- `copywriting/references/ai-tells.md` lines 299-307: Wikipedia "Signs of AI writing" (CC BY-SA), papers and blog posts, stated to be "rewritten in our own words".

No overlap measurement was made for these. The two phrase-list files are the kind of content that could be reproduced verbatim. The owner decides whether
to accept the risk as is, measure it, or ship without those two reference files (which would end byte-identity with the upstream directory).

## Exposure and targets

- Catalog status is `on-demand` by intent (the skills overlap the active Copy OS family). The deployer does **not** enforce it: it only checks that the
  status is deliverable. In Claude Code, what is listed or auto-invoked comes from `skillOverrides` settings or `disable-model-invocation` frontmatter
  (editing frontmatter here would break the byte pin, so exposure must be set in runtime settings, owned outside this repository). How Codex exposure
  is controlled is not established here. Older text in `docs/consolidation/README.md` and `scripts/deploy-skills.py` describes `on-demand` as "not
  auto-loaded"; read that as the catalog's intent, not as something the deployer performs.
- Targets are both runtimes because both stores already hold these skills (`~/.agents/skills` as real directories, `~/.claude/skills` as links into them,
  and neither is tracked in the installer lock), so a Claude-only target would still write through the link into the Codex store.
- A project copy of these skills in another repository is independent of this record. A repository that loads project skills only (for example an SDK
  orchestrator with `settingSources: ["project"]`) needs its own copy, and such a copy carries no `LICENSE.txt` unless it is copied from here.

## Rollback

`deploy-skills.py` never deletes and acts only on skills declared in the manifest, so reverting this import does **not** restore older bytes: the
runtime would keep what was last deployed. To roll back, commit the previous upstream bytes into the two skill directories (upstream `e6fb742` for
`copywriting` and `158bd3a` for `copy-editing`: on 2026-10-31 and again 2026-11-01 the live runtime `SKILL.md` files were byte-identical to those
revisions), set each entry's `expected_sha256` to match, and run `deploy-skills.py --deploy --skill <name>`. This was rehearsed in scratch roots:
the rolled-back tree passed `check-skill-consistency.py` and `deploy-skills.py --check` reported CLEAN. A leftover `LICENSE.txt` is harmless.
These skills were not in this catalogue before this import, so there is no older catalogue state to deploy from.
