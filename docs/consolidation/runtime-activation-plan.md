# D4 Runtime Activation Plan

> **Nothing in this document has been applied.** D3.5 changed the catalog, not runtime
> exposure. This is the input to D4.

## Budget

| Set | Skills | Chars | Est. tokens | % of ~10k |
|---|---:|---:|---:|---:|
| Claude — current live | 133 | 35,192 | 9,776 | 98% |
| Claude — D2 proposed | 67 | 17,006 | 4,724 | 47% |
| **Claude — D3.5 revised** | **72** | **17,965** | **4,990** | **50%** |
| Codex — current live | 223 | 50,149 | 13,930 | 139% |
| **Codex — D3.5 revised** | **75** | **17,158** | **4,766** | **48%** |

The D3.5 set is larger than D2 proposed because reconciliation **resolved** skills that D3
had frozen as `hold`; resolving a skill returns it to its pre-hold exposure rather than
silently hiding it. D4 decides exposure; D3.5 only made the catalog correct.

## ACTIVE — proposed

| Skill | Family | Usage | Desc chars | Why active |
|---|---|---:|---:|---|
| `21st-cli-use` | — | 1 | 609 | used (1) |
| `21st-design-sync` | — | 1 | 497 | used (1) |
| `21st-ui-review` | — | 1 | 512 | used (1) |
| `ai-regression-testing` | ai-evals | 0 | 228 | core methodology family: ai-evals |
| `api-design` | stack-patterns | 0 | 156 | stack pattern for the active tech stack |
| `api-integration` | stack-patterns | 2 | 380 | used (2) |
| `archify` | architecture | 3 | 652 | recurring use (3 recorded invocations) |
| `architecture-decision-records` | architecture | 0 | 267 | core methodology family: architecture |
| `backend-patterns` | stack-patterns | 1 | 142 | used (1) |
| `benchmark` | ai-evals | 0 | 117 | core methodology family: ai-evals |
| `blueprint` | specs-plans-tickets | 12 | 628 | recurring use (12 recorded invocations) |
| `browser-qa` | — | 5 | 124 | recurring use (5 recorded invocations) |
| `canary-watch` | deployment | 0 | 103 | no recorded use and not a core methodology |
| `claude-handoff` | handoff-memory | 0 | 97 | core methodology family: handoff-memory |
| `code-review` | review | 20 | 417 | blocked on naming decision |
| `code-review-patterns` | — | 0 | 415 | created by the D3 split |
| `codebase-design` | domain-modeling | 4 | 265 | recurring use (4 recorded invocations) |
| `context-budget` | handoff-memory | 1 | 188 | core methodology family: handoff-memory |
| `continuous-agent-loop` | autonomous-parallel | 0 | 96 | no recorded use and not a core methodology |
| `continuous-learning` | handoff-memory | 0 | 113 | core methodology family: handoff-memory |
| `continuous-learning-v2` | handoff-memory | 0 | 235 | core methodology family: handoff-memory |
| `cost-aware-llm-pipeline` | ai-evals | 2 | 130 | core methodology family: ai-evals |
| `deep-research` | research | 5 | 336 | recurring use (5 recorded invocations) |
| `design-an-interface` | domain-modeling | 2 | 214 | core methodology family: domain-modeling |
| `design-system` | architecture | 3 | 112 | recurring use (3 recorded invocations) |
| `diagnosing-bugs` | debugging | 4 | 156 | recurring use (4 recorded invocations) |
| `documentation-lookup` | research | 4 | 212 | recurring use (4 recorded invocations) |
| `domain-modeling` | domain-modeling | 3 | 216 | recurring use (3 recorded invocations) |
| `e2e-testing` | stack-patterns | 4 | 133 | recurring use (3 recorded invocations) |
| `edit-article` | — | 3 | 159 | recurring use (3 recorded invocations) |
| `eval-harness` | ai-evals | 0 | 106 | core methodology family: ai-evals |
| `frontend-patterns` | stack-patterns | 1 | 116 | used (1) |
| `git-guardrails-claude-code` | git-worktrees | 12 | 243 | recurring use (12 recorded invocations) |
| `git-workflow` | git-worktrees | 25 | 333 | recurring use (25 recorded invocations) |
| `git-workflow-patterns` | — | 0 | 180 | created by the D3 split |
| `grill-me` | brainstorming | 0 | 51 | core methodology family: brainstorming |
| `grill-with-docs` | brainstorming | 2 | 106 | core methodology family: brainstorming |
| `grilling` | brainstorming | 7 | 151 | recurring use (7 recorded invocations) |
| `handoff` | handoff-memory | 83 | 86 | recurring use (83 recorded invocations) |
| `implement` | specs-plans-tickets | 0 | 62 | core methodology family: specs-plans-tickets |
| `improve-codebase-architecture` | architecture | 7 | 125 | recurring use (7 recorded invocations) |
| `market-research` | research | 1 | 380 | core methodology family: research |
| `mcp-server-patterns` | stack-patterns | 0 | 163 | stack pattern for the active tech stack |
| `nextjs-turbopack` | stack-patterns | 0 | 110 | stack pattern for the active tech stack |
| `plankton-code-quality` | review | 0 | 135 | core methodology family: review |
| `postgres-patterns` | stack-patterns | 1 | 125 | used (1) |
| `product-lens` | brainstorming | 3 | 169 | recurring use (3 recorded invocations) |
| `project-guidelines-example` | — | 0 | 81 | no recorded use and not a core methodology |
| `prompt-optimizer` | — | 1 | 717 | used (1) |
| `prototype` | specs-plans-tickets | 0 | 179 | core methodology family: specs-plans-tickets |
| `python-patterns` | stack-patterns | 0 | 377 | stack pattern for the active tech stack |
| `python-testing` | stack-patterns | 0 | 345 | stack pattern for the active tech stack |
| `qa` | debugging | 2 | 281 | core methodology family: debugging |
| `react-typescript-patterns` | stack-patterns | 1 | 467 | used (1) |
| `regex-vs-llm-structured-text` | — | 0 | 146 | no recorded use and not a core methodology |
| `research` | research | 0 | 238 | core methodology family: research |
| `resolving-merge-conflicts` | git-worktrees | 8 | 72 | recurring use (8 recorded invocations) |
| `risk-based-tdd` | tdd | 4 | 466 | core methodology family: tdd |
| `safety-guard` | — | 0 | 115 | no recorded use and not a core methodology |
| `santa-method` | — | 0 | 127 | no recorded use and not a core methodology |
| `search-first` | research | 1 | 141 | core methodology family: research |
| `skill-comply` | review | 0 | 239 | core methodology family: review |
| `skill-stocktake` | — | 0 | 169 | no recorded use and not a core methodology |
| `strategic-compact` | handoff-memory | 298 | 134 | recurring use (292 recorded invocations) |
| `supabase-dev` | stack-patterns | 3 | 590 | recurring use (3 recorded invocations) |
| `team-builder` | autonomous-parallel | 0 | 69 | no recorded use and not a core methodology |
| `to-spec` | specs-plans-tickets | 0 | 150 | core methodology family: specs-plans-tickets |
| `to-tickets` | specs-plans-tickets | 1 | 232 | core methodology family: specs-plans-tickets |
| `triage` | debugging | 0 | 137 | core methodology family: debugging |
| `ubiquitous-language` | domain-modeling | 1 | 313 | core methodology family: domain-modeling |
| `verification-loop` | — | 5 | 63 | recurring use (5 recorded invocations) |
| `wayfinder` | specs-plans-tickets | 0 | 204 | core methodology family: specs-plans-tickets |

## ON-DEMAND — source retained, not globally exposed

166 skills. Reactivate by setting `status: active` in
`manifests/skills.json` and running `scripts/deploy-skills.py --deploy`; for Claude also
clear the `skillOverrides` entry. Source is retained in this repository in every case.

| Skill | Why not exposed |
|---|---|
| `21st-ai` | no recorded use and not a core methodology |
| `21st-registry` | no recorded use and not a core methodology |
| `21st-ui-build` | no recorded use and not a core methodology |
| `21st-ui-explore` | no recorded use and not a core methodology |
| `agent-harness-construction` | no recorded use and not a core methodology |
| `agent-introspection-debugging` | no recorded use and not a core methodology |
| `agent-sort` | no recorded use and not a core methodology |
| `agentic-engineering` | no recorded use and not a core methodology |
| `ai-first-engineering` | no recorded use and not a core methodology |
| `android-clean-architecture` | already disabled / off-stack; source retained |
| `api-connector-builder` | no recorded use and not a core methodology |
| `article-writing` | no recorded use and not a core methodology |
| `ask-matt` | no recorded use and not a core methodology |
| `automation-audit-ops` | no recorded use and not a core methodology |
| `autonomous-agent-harness` | no recorded use and not a core methodology |
| `autonomous-loops` | already disabled / off-stack; source retained |
| `brand-voice` | no recorded use and not a core methodology |
| `bun-runtime` | already disabled / off-stack; source retained |
| `carrier-relationship-management` | already disabled / off-stack; source retained |
| `ck` | no recorded use and not a core methodology |
| `claude-api` | no recorded use and not a core methodology |
| `claude-devfleet` | no recorded use and not a core methodology |
| `click-path-audit` | no recorded use and not a core methodology |
| `clickhouse-io` | already disabled / off-stack; source retained |
| `code-tour` | no recorded use and not a core methodology |
| `coding-standards` | no recorded use and not a core methodology |
| `compose-multiplatform-patterns` | already disabled / off-stack; source retained |
| `configure-ecc` | already disabled / off-stack; source retained |
| `connections-optimizer` | no recorded use and not a core methodology |
| `content-engine` | no recorded use and not a core methodology |
| `content-hash-cache-pattern` | no recorded use and not a core methodology |
| `council` | no recorded use and not a core methodology |
| `cpp-coding-standards` | already disabled / off-stack; source retained |
| `cpp-testing` | already disabled / off-stack; source retained |
| `crosspost` | no recorded use and not a core methodology |
| `customer-billing-ops` | no recorded use and not a core methodology |
| `customs-trade-compliance` | already disabled / off-stack; source retained |
| `dashboard-builder` | no recorded use and not a core methodology |
| `data-scraper-agent` | no recorded use and not a core methodology |
| `django-patterns` | already disabled / off-stack; source retained |
| `django-security` | already disabled / off-stack; source retained |
| `django-tdd` | already disabled / off-stack; source retained |
| `django-verification` | already disabled / off-stack; source retained |
| `dmux-workflows` | already disabled / off-stack; source retained |
| `docker-patterns` | no recorded use and not a core methodology |
| `ecc-tools-cost-audit` | no recorded use and not a core methodology |
| `email-ops` | no recorded use and not a core methodology |
| `energy-procurement` | already disabled / off-stack; source retained |
| `enterprise-agent-ops` | no recorded use and not a core methodology |
| `exa-search` | already disabled / off-stack; source retained |
| `fal-ai-media` | already disabled / off-stack; source retained |
| `finance-billing-ops` | no recorded use and not a core methodology |
| `find-skills` | no recorded use and not a core methodology |
| `flutter-dart-code-review` | already disabled / off-stack; source retained |
| `foundation-models-on-device` | already disabled / off-stack; source retained |
| `frontend-design` | no recorded use and not a core methodology |
| `frontend-slides` | no recorded use and not a core methodology |
| `gan-style-harness` | no recorded use and not a core methodology |
| `gemini-api-dev` | no recorded use and not a core methodology |
| `github-ops` | no recorded use and not a core methodology |
| `golang-patterns` | already disabled / off-stack; source retained |
| `golang-testing` | already disabled / off-stack; source retained |
| `google-workspace-ops` | no recorded use and not a core methodology |
| `hexagonal-architecture` | no recorded use and not a core methodology |
| `hookify-rules` | no recorded use and not a core methodology |
| `inventory-demand-planning` | already disabled / off-stack; source retained |
| `java-coding-standards` | already disabled / off-stack; source retained |
| `jira-integration` | no recorded use and not a core methodology |
| `jpa-patterns` | already disabled / off-stack; source retained |
| `knowledge-ops` | no recorded use and not a core methodology |
| `kotlin-coroutines-flows` | already disabled / off-stack; source retained |
| `kotlin-exposed-patterns` | already disabled / off-stack; source retained |
| `kotlin-ktor-patterns` | already disabled / off-stack; source retained |
| `kotlin-patterns` | already disabled / off-stack; source retained |
| `kotlin-testing` | already disabled / off-stack; source retained |
| `laravel-patterns` | already disabled / off-stack; source retained |
| `laravel-security` | already disabled / off-stack; source retained |
| `laravel-tdd` | already disabled / off-stack; source retained |
| `laravel-verification` | already disabled / off-stack; source retained |
| `liquid-glass-design` | no recorded use and not a core methodology |

## HOLD — unresolved, needs a human merge

| Skill | Why |
|---|---|
| `agent-eval` | D3.5: both sides hold unique material (28/4 lines) - needs a merge - genuine merge still owed. |
| `codebase-onboarding` | D3.5: both sides hold unique material (18/18 lines) - needs a merge - genuine merge still owed. |
| `database-migrations` | D3.5: both sides hold unique material (1/51 lines) - needs a merge - genuine merge still owed. |
| `deployment-patterns` | D3.5: both sides hold unique material (1/59 lines) - needs a merge - genuine merge still owed. |
| `iterative-retrieval` | D3.5: both sides hold unique material (98/83 lines) - needs a merge - genuine merge still owed. |
| `security-review` | D3.5: both sides hold unique material (1/30 lines) - needs a merge - genuine merge still owed. |
| `tdd-workflow` | D3.5: both sides hold unique material (35/152 lines) - needs a merge - genuine merge still owed. |
| `x-api` | D3.5: both sides hold unique material (24/14 lines) - needs a merge - genuine merge still owed. |

## REPO_LOCAL — owned by a product repository

| Skill | Owning product |
|---|---|
| `ads` | belongs to a product repo |
| `ads-audit` | belongs to a product repo |
| `ads-budget` | belongs to a product repo |
| `ads-competitor` | belongs to a product repo |
| `ads-creative` | belongs to a product repo |
| `ads-google` | belongs to a product repo |
| `ads-hyros` | belongs to a product repo |
| `ads-landing` | belongs to a product repo |
| `ads-linkedin` | belongs to a product repo |
| `ads-meta` | belongs to a product repo |
| `ads-microsoft` | belongs to a product repo |
| `ads-plan` | belongs to a product repo |
| `ads-tiktok` | belongs to a product repo |
| `ads-youtube` | belongs to a product repo |
| `branch-protection-override` | belongs to a product repo |
| `cold-outreach-pipeline` | belongs to a product repo |
| `constructintel-extraction` | belongs to a product repo |
| `construction-industry` | belongs to a product repo |
| `deploy` | belongs to a product repo |
| `edge-drift-check` | belongs to a product repo |
| `edge-function-deploy` | belongs to a product repo |
| `investor-materials` | belongs to a product repo |
| `investor-outreach` | belongs to a product repo |
| `lead-intelligence` | belongs to a product repo |
| `live-outreach-safety` | belongs to a product repo |
| `migration-apply-verify` | belongs to a product repo |
| `mutation-battery` | belongs to a product repo |
| `pr-gate` | belongs to a product repo |
| `preconintel` | belongs to a product repo |
| `seo` | belongs to a product repo |
| `siteintel-gis-pipeline` | belongs to a product repo |
| `source-command-done` | belongs to a product repo |
| `source-command-regen-types` | belongs to a product repo |
| `wt-bootstrap` | belongs to a product repo |
| `wt-teardown` | belongs to a product repo |

## Rollback

Every exposure change is reversible from `manifests/skills.json` plus
`scripts/deploy-skills.py`, and every byte is recoverable from the preservation snapshot
`8a756b95b122ffad19f22199679bc6536d0a94d6`.


## Runtime `.git` transition — RECOMMENDATION ONLY, not executed

Both runtime stores are still single-commit **orphan** repositories pinned to `f175f208`, a commit
that does not exist on the remote they declare. They have never accepted a commit from us and they
cannot be reconciled by git.

| Option | Assessment |
|---|---|
| **A. Keep runtime `.git` temporarily** | Current state. Harmless but misleading — it implies the runtimes are sources when they are outputs, and `git status` there now shows large diffs that are simply deployment results. |
| **B. Remove after D4 activation** | **RECOMMENDED.** Once D4 sets the active set and a deploy proves reproducible end to end, the metadata has no remaining purpose. |
| **C. Replace with a deployment-state manifest** | **RECOMMENDED companion to B.** Write `.deployment-state.json` (source commit, manifest hash, per-skill SHA-256, deploy timestamp) so the runtimes remain auditable without pretending to be repositories. |

### Migration steps (do not execute yet)

1. Confirm `deploy-skills.py --check` is CLEAN and D4 activation has settled.
2. Archive both `.git` directories to a timestamped external location and verify hashes.
3. Write `.deployment-state.json` into each runtime root.
4. Remove `.git` from `~/.claude/skills` and `~/.agents/skills`.
5. Re-run `--check`; it must remain CLEAN (the deploy system never depended on runtime git).
6. Record the transition in `docs/consolidation/`.

**Precondition:** do not start until the 8 remaining HOLD skills are resolved — losing runtime git
while unmerged runtime-only content still exists would remove a recovery path, even though the
preservation snapshot `8a756b95…` remains the authoritative backstop.
