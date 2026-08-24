# Canonical ↔ Runtime Reconciliation — REQUIRED BEFORE ANY DEPLOY

> 🔴 **Do not run `deploy-skills.py --deploy` against the live runtimes until this list is
> resolved.** Doing so would overwrite live Claude-runtime content with the older frozen
> canonical variant for the skills below.

## What happened

D2 imported the 103 skills that existed *only* in a runtime, so coverage is now complete.
But for the **115 skills that were already in the canonical repo** (frozen since 2026-05/07),
canonical and the live Claude runtime have drifted apart independently.

**22 skills** differ in real content (line-ending-only differences excluded).

Neither side is uniformly authoritative:

- live runtime larger in **15** cases
- canonical larger in **7** cases

So this **cannot be auto-resolved by size, mtime, or line count** — it needs per-skill review.
`git-workflow` is the clearest example: canonical is 15,057 bytes and the runtime is 3,102.
They are almost certainly different documents that share a name, exactly like `code-review`.

## Reconciliation set

| Skill | diff lines | canonical bytes | live runtime bytes | larger side |
|---|---:|---:|---:|---|
| `python-testing` | 825 | 10,554 | 19,678 | runtime |
| `python-patterns` | 751 | 9,307 | 17,498 | runtime |
| `git-workflow` | 581 | 15,057 | 3,102 | canonical |
| `iterative-retrieval` | 218 | 8,593 | 6,898 | canonical |
| `market-research` | 144 | 5,665 | 2,301 | canonical |
| `api-design` | 86 | 16,461 | 13,633 | canonical |
| `deployment-patterns` | 82 | 8,463 | 11,427 | runtime |
| `database-migrations` | 78 | 9,481 | 12,268 | runtime |
| `security-review` | 48 | 11,025 | 12,709 | runtime |
| `e2e-testing` | 39 | 6,633 | 8,391 | runtime |
| `agent-eval` | 28 | 6,272 | 4,671 | canonical |
| `ai-regression-testing` | 28 | 11,533 | 11,920 | runtime |
| `strategic-compact` | 28 | 4,142 | 5,412 | runtime |
| `prompt-optimizer` | 13 | 16,066 | 16,625 | runtime |
| `blueprint` | 11 | 5,379 | 5,449 | runtime |
| `product-lens` | 9 | 3,090 | 2,843 | canonical |
| `benchmark` | 7 | 2,331 | 2,549 | runtime |
| `continuous-learning-v2` | 6 | 12,454 | 12,913 | runtime |
| `browser-qa` | 3 | 2,614 | 2,860 | runtime |
| `design-system` | 3 | 2,480 | 2,730 | runtime |
| `context-budget` | 2 | 5,695 | 5,825 | runtime |
| `continuous-learning` | 2 | 3,888 | 3,763 | canonical |

## Why D2 stopped here

D2's contract was preserve → classify → adjudicate → canonicalize → **verify** → only then prune.
Deploying now would fail the preservation contract: it would destroy live content that has never
been reviewed against its canonical counterpart. The deployment system is built and proven
(see the golden test), and it is deliberately left un-run against the live runtimes.

## Recommended D3 order

1. Adjudicate these 22 skills, highest diff first — treat any with a very low shared-line ratio
   as *two different skills sharing a name*, not as drift.
2. Resolve the `code-review` naming decision.
3. Re-run `--check` until only intended differences remain.
4. Deploy, then verify hashes.
5. Only after that, consider the runtime active-set reduction.



---

# D3 OUTCOME — reconciled and deployed

Recomputed from scratch: **160 conflict rows across 92 distinct skills** (D2's "22" counted the
Claude side only). 111 rows / 78 skills were substantive; 49 rows were line-endings alone.

| Classification | Rows |
|---|---:|
| G. TRIVIAL_NORMALIZATION | 49 |
| A. RUNTIME_NEWER_SAME_CAPABILITY | 34 |
| F. CORRUPTION (all Codex; canonical clean in every case) | 33 |
| B. CANONICAL_NEWER_SAME_CAPABILITY | 27 |
| D. TWO_DIFFERENT_SKILLS_SAME_NAME | 13 |
| H. HUMAN_DECISION_REQUIRED | 4 |

## Same-name / different-capability splits

| Skill | Classification | Canonical before | Runtime before | Decision | Canonical after | Why | Risk | Verification |
|---|---|---|---|---|---|---|---|---|
| `code-review` | D (ratio **0.019**) | engineering-quality checklist | Codex: dual-axis Standards+Spec reviewer | **SPLIT** | `code-review` = dual-axis reviewer; `code-review-patterns` = checklist | Only 2 shared lines. The dual-axis reviewer is the capability the audit called "truly missing"; it existed Codex-only. | Rename affects a 20-use skill. Mitigated: the 350-invocation `code-reviewer` **agent is independent** (0 skill references), no rule/repo file dispatches the name. | Both held out of deploy; runtime dispatch unchanged pending confirmation |
| `git-workflow` | D (ratio **0.13**, **4.85x** size) | generic ECC branching-strategy encyclopedia (15,057 b) | BuildSmarter commit/branch **conventions** (3,102 b, 25 uses) | **SPLIT** | `git-workflow` = live conventions; `git-workflow-patterns` = ECC reference | One is a strategy encyclopedia, the other is this org's actual conventions. | Low — conventions keep the used name | Deployed; all three hashes `26aaab53` |

## Same-capability adjudications

| Skill | Classification | Decision | Why | Verification |
|---|---|---|---|---|
| `crosspost` | A | canonical corrected **from** runtime | runtime is a superset (adds Platform Specifications) | canonical == runtime, deploy is a no-op |
| `market-research` | B | **canonical wins**, deployed | canonical carries `origin: ECC (customized for BuildSmarter stack)` and CRE/PropTech targeting the generic runtime copy lost | deployed; description now shows the BuildSmarter customization |
| `investor-materials`, `investor-outreach` | B | canonical wins | canonical holds BuildSmarter Portfolio Context / Investor Targeting Segments | canonical only (classified REPO_LOCAL, not globally deployed) |
| 33 Codex skills | F | **canonical wins** | runtime carries the blind `Claude`->`Codex` substitution; canonical clean in every case | 6 deployed this round; the rest are on-demand and stay held *(transitional D3 state; on-demand does not mean withheld — see README.md)* |
| 49 rows | G | canonical wins | line endings only | deployed where active |

## Held for human decision

| Skill | Why |
|---|---|
| `python-patterns` | Canonical is sharper (EAFP vs LBYL, decision matrices); runtime is broader. Needs a merge, not a winner. |
| `python-testing` | Canonical holds institutional knowledge (the patch-vs-autospec binding trap); runtime is generic TDD boilerplate. Needs a merge. |
| `deep-research` | Two different designs (canonical = firecrawl/exa MCP workflow; runtime = citation tracking + evidence persistence + output contract). Ratio 0.029. |
| 47 A/B skills | Same capability, drift not individually adjudicated. Set `status: hold` so `--deploy` cannot touch them. |

## Deployment executed

57 file operations, **0 deletions**. Claude +1 create / 27 updates; Codex +1 create / 28 updates.
Post-deploy `--check`: **CLEAN**. `risk-based-tdd` byte-identical across canonical, Claude and Codex.
