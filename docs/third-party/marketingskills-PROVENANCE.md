# marketingskills provenance (copywriting, copy-editing)

Third-party skills imported from `coreyhaines31/marketingskills` (MIT) at revision `15b38b5388dfdd17f4ab424e986ccd32c24d5b22`.

## Reproduce

```bash
gh api "repos/coreyhaines31/marketingskills/git/trees/15b38b5388dfdd17f4ab424e986ccd32c24d5b22?recursive=1" --jq '.tree[] | select(.path|startswith("skills/copywriting/") or startswith("skills/copy-editing/") or .path=="LICENSE") | "\(.sha) \(.path)"'
git hash-object copywriting/SKILL.md   # compare each file with the git blob sha below
```

Each skill directory is the upstream skill directory unchanged, plus `LICENSE.txt` (the upstream `LICENSE` file, unchanged).
The deployer ships only skill directories (`docs/` is never deployed), so the notice must live inside each one.
`manifests/skills.json` pins `expected_sha256` for `SKILL.md` only; the table below records every file.

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

The upstream files credit Profound's `skills-marketing-library` (MIT) for adapted ideas, "re-expressed" in their own words. Checked 2026-11-01 by measuring
verbatim overlap between these ten files and the 24 text files of that repository: 21 shared 8-word sequences out of 13,273 (0.16%). Most come from
generic trigger phrasing in the frontmatter description; 4 short phrases in `copywriting/references/ai-tells.md` match Profound's `humanizer`.
That is not a substantial portion of the work, and upstream's own credit lines are preserved in the files, so no second licence file is shipped.
This is an engineering judgement, not legal advice; if the four phrases matter, the remedy is to add Profound's MIT notice next to this one.

## Exposure and targets

- Catalog status is `on-demand` by intent (the skills overlap the active Copy OS family). The deployer does **not** enforce it: Claude Code decides what is
  listed or auto-invoked from `skillOverrides` settings or `disable-model-invocation` frontmatter. Editing frontmatter here would break the byte pin, so
  exposure must be set in runtime settings, owned outside this repository.
- Targets are both runtimes because both stores already hold these skills (`~/.agents/skills` as real directories, `~/.claude/skills` as links into them,
  and neither is tracked in the installer lock), so a Claude-only target would still write through the link into the Codex store.
- A project copy of these skills in another repository is independent of this record. A repository that loads project skills only (for example an SDK
  orchestrator with `settingSources: ["project"]`) needs its own copy.

## Rollback

`deploy-skills.py` never deletes. Roll back by reverting the import and deploying the older bytes (upstream `e6fb742` for copywriting, `158bd3a` for
copy-editing were the previously installed states); a leftover `LICENSE.txt` is harmless.
