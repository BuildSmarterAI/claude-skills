# Orphaned REPO_LOCAL Skills — Ownership Register

> Recomputed from evidence in D4.2. **The prior figure of 15 was wrong**: it counted orphans
> only within the live Claude drop list. Across the whole manifest there are **20**.

## Method

An entry is *orphaned* when it claims `REPO_LOCAL` (by status, mode, or classification) but no
repository under `Documents/GitHub` contains a `<skill>/SKILL.md` for it. 92 repositories were
walked, indexing 455 distinct skill names provided outside the canonical repo.

| Measure | Count |
|---|---:|
| entries claiming REPO_LOCAL | 35 |
| genuinely provided by a repo | 15 |
| **orphaned** | **20** |
| naming an owner before D4.2 | **0** |

## The orphan set

| Skill | Was | Now | Owner | Consumers | Reason |
|---|---|---|---|---|---|
| `ads` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | 7 audit agents | Entry point for the paid-advertising audit fleet: `ads/SKILL.md` explicitly spawns the seven audit-* subagents and names the thirteen ads-* deep-dive  |
| `ads-audit` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-budget` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-competitor` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-creative` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-google` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-hyros` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-landing` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-linkedin` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-meta` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-microsoft` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-plan` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-tiktok` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `ads-youtube` | REPO_LOCAL (no owner) | **AGENT-SUPPORTING-GLOBAL** | *(global)* | `ads (orchestrator)` | Deep-dive layer of the ads capability; referenced by name from `ads/SKILL.md`. The audit-* agents are self-contained and do NOT consume it, so the dep |
| `cold-outreach-pipeline` | REPO_LOCAL (no owner) | **SHARED-DOMAIN** | *(global)* | — | Its own description scopes it to "ConstructIntel.ai and SiteIntel sales" - two products, so no single repo can own it. Not currently present in either |
| `constructintel-extraction` | REPO_LOCAL (no owner) | **REPO-LOCAL** | constructintel.ai | — | Description scopes it unambiguously to "ConstructIntel.ai's AI-powered document extraction pipeline" (PDF processing, CSI classification, bid line-ite |
| `construction-industry` | REPO_LOCAL (no owner) | **SHARED-DOMAIN** | *(global)* | — | Generic construction domain knowledge - CSI MasterFormat divisions, estimating workflow, bid formats, scope-gap risk, Texas context - with only two pr |
| `lead-intelligence` | REPO_LOCAL (no owner) | **GLOBAL-ON-DEMAND** | *(global)* | — | Generic AI-native lead intelligence and outreach scoring (origin ECC). Names no product and is not construction-specific; the same capability serves a |
| `seo` | REPO_LOCAL (no owner) | **GLOBAL-ON-DEMAND** | *(global)* | — | Generic SEO auditing and implementation (origin ECC) - technical SEO, structured data, Core Web Vitals. No product coupling of any kind. |
| `siteintel-gis-pipeline` | REPO_LOCAL (no owner) | **REPO-LOCAL** | siteintelai | — | Description scopes it unambiguously to "SiteIntel's GIS data pipeline and feasibility scoring engine" (PostGIS, county CAD schemas, Texas spatial sour |

## Canonical-source gap found and closed

Fourteen `ads-*` skills and `construction-industry` existed **only in the two runtime stores**.
They had never been committed to the canonical repository, so the manifest claimed ownership
the repository could not honour. They are now imported (44 files) from the **Claude** side,
which D3 established as the clean one.

Importing also repaired real corruption: `ads`, `ads-audit`, `ads-hyros` and `ads-meta` carried
the blind `Claude`->`Codex` substitution on the Codex side (9 markers total). All four are now
byte-identical to canonical and the marker count is **0**.

> They were never at risk of loss - all 15 are present in the preservation snapshot
> `8a756b95` under both `claude-runtime/skills/` and `codex-runtime/skills/`.

## The 15 REPO_LOCAL entries that were already truthful

These do have a real owning repository. D4.2 records the verified path rather than the former
generic note "belongs to a product repo".

| Skill | Owner path |
|---|---|
| `branch-protection-override` | `maxx-sales-genius/.claude/skills/branch-protection-override` |
| `deploy` | `maxx-brace-fix-wt/.claude/skills/deploy` |
| `edge-drift-check` | `siteintelai/.claude/skills/edge-drift-check` |
| `edge-function-deploy` | `siteintelai/.claude/skills/edge-function-deploy` |
| `investor-materials` | `siteintelai/.agents/skills/investor-materials` |
| `investor-outreach` | `siteintelai/.agents/skills/investor-outreach` |
| `live-outreach-safety` | `maxx-sales-genius/.claude/skills/live-outreach-safety` |
| `migration-apply-verify` | `siteintelai/.claude/skills/migration-apply-verify` |
| `mutation-battery` | `maxx-sales-genius/.claude/skills/mutation-battery` |
| `pr-gate` | `maxx-sales-genius/.claude/skills/pr-gate` |
| `preconintel` | `preconintel/.agents/skills/preconintel` |
| `source-command-done` | `preconintel/.agents/skills/source-command-done` |
| `source-command-regen-types` | `preconintel/.agents/skills/source-command-regen-types` |
| `wt-bootstrap` | `maxx-sales-genius/.claude/skills/wt-bootstrap` |
| `wt-teardown` | `maxx-sales-genius/.claude/skills/wt-teardown` |
