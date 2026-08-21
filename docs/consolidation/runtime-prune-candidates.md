# Runtime Prune Candidates — REVIEW ONLY, NOTHING REMOVED

> **No skill was disabled or deleted in D2.** This list exists to be reviewed in D3.
> Every skill below is retained in the canonical source regardless of runtime exposure.
> **Source retention and runtime exposure are different decisions.**

Claude runtime currently exposes **131 active** skills ≈ **9,698 tokens** of descriptions
against a ~10k effective budget. The proposed active set is **67 skills ≈ 4,724 tokens**.

## SAFE_TO_DISABLE

59 skills already disabled via `skillOverrides` — off-stack language packs,
supply-chain verticals, media tooling. Confirming their manifest status changes nothing
at runtime.

| Skill | Reason |
|---|---|
| `android-clean-architecture` | already disabled / off-stack; source retained |
| `autonomous-loops` | already disabled / off-stack; source retained |
| `bun-runtime` | already disabled / off-stack; source retained |
| `carrier-relationship-management` | already disabled / off-stack; source retained |
| `clickhouse-io` | already disabled / off-stack; source retained |
| `compose-multiplatform-patterns` | already disabled / off-stack; source retained |
| `configure-ecc` | already disabled / off-stack; source retained |
| `cpp-coding-standards` | already disabled / off-stack; source retained |
| `cpp-testing` | already disabled / off-stack; source retained |
| `customs-trade-compliance` | already disabled / off-stack; source retained |
| `django-patterns` | already disabled / off-stack; source retained |
| `django-security` | already disabled / off-stack; source retained |
| `django-tdd` | already disabled / off-stack; source retained |
| `django-verification` | already disabled / off-stack; source retained |
| `dmux-workflows` | already disabled / off-stack; source retained |
| `energy-procurement` | already disabled / off-stack; source retained |
| `exa-search` | already disabled / off-stack; source retained |
| `fal-ai-media` | already disabled / off-stack; source retained |
| `flutter-dart-code-review` | already disabled / off-stack; source retained |
| `foundation-models-on-device` | already disabled / off-stack; source retained |
| `golang-patterns` | already disabled / off-stack; source retained |
| `golang-testing` | already disabled / off-stack; source retained |
| `inventory-demand-planning` | already disabled / off-stack; source retained |
| `java-coding-standards` | already disabled / off-stack; source retained |
| `jpa-patterns` | already disabled / off-stack; source retained |
| `kotlin-coroutines-flows` | already disabled / off-stack; source retained |
| `kotlin-exposed-patterns` | already disabled / off-stack; source retained |
| `kotlin-ktor-patterns` | already disabled / off-stack; source retained |
| `kotlin-patterns` | already disabled / off-stack; source retained |
| `kotlin-testing` | already disabled / off-stack; source retained |
| `laravel-patterns` | already disabled / off-stack; source retained |
| `laravel-security` | already disabled / off-stack; source retained |
| `laravel-tdd` | already disabled / off-stack; source retained |
| `laravel-verification` | already disabled / off-stack; source retained |
| `logistics-exception-management` | already disabled / off-stack; source retained |
| `migrate-to-shoehorn` | already disabled / off-stack; source retained |
| `nanoclaw-repl` | already disabled / off-stack; source retained |
| `nuxt4-patterns` | already disabled / off-stack; source retained |
| `obsidian-vault` | already disabled / off-stack; source retained |
| `perl-patterns` | already disabled / off-stack; source retained |
| `perl-security` | already disabled / off-stack; source retained |
| `perl-testing` | already disabled / off-stack; source retained |
| `production-scheduling` | already disabled / off-stack; source retained |
| `pytorch-patterns` | already disabled / off-stack; source retained |
| `quality-nonconformance` | already disabled / off-stack; source retained |
| `returns-reverse-logistics` | already disabled / off-stack; source retained |
| `rust-patterns` | already disabled / off-stack; source retained |
| `rust-testing` | already disabled / off-stack; source retained |
| `springboot-patterns` | already disabled / off-stack; source retained |
| `springboot-security` | already disabled / off-stack; source retained |
| `springboot-tdd` | already disabled / off-stack; source retained |
| `springboot-verification` | already disabled / off-stack; source retained |
| `swift-actor-persistence` | already disabled / off-stack; source retained |
| `swift-concurrency-6-2` | already disabled / off-stack; source retained |
| `swift-protocol-di-testing` | already disabled / off-stack; source retained |
| `swiftui-patterns` | already disabled / off-stack; source retained |
| `video-editing` | already disabled / off-stack; source retained |
| `videodb` | already disabled / off-stack; source retained |
| `visa-doc-translate` | already disabled / off-stack; source retained |

## REVIEW

46 skills with no recorded use that are **not** already disabled. Zero usage is
evidence, not a verdict — several are recently installed methodology skills that have not
yet had an occasion to fire.

| Skill | Family | Usage | Reason |
|---|---|---:|---|
| `21st-ai` | — | 0 | no recorded use and not a core methodology |
| `21st-registry` | — | 0 | no recorded use and not a core methodology |
| `21st-ui-build` | — | 0 | no recorded use and not a core methodology |
| `21st-ui-explore` | — | 0 | no recorded use and not a core methodology |
| `agent-harness-construction` | — | 0 | no recorded use and not a core methodology |
| `agentic-engineering` | — | 0 | no recorded use and not a core methodology |
| `ai-first-engineering` | — | 0 | no recorded use and not a core methodology |
| `article-writing` | — | 0 | no recorded use and not a core methodology |
| `ask-matt` | — | 0 | no recorded use and not a core methodology |
| `canary-watch` | deployment | 0 | no recorded use and not a core methodology |
| `claude-api` | — | 0 | no recorded use and not a core methodology |
| `claude-devfleet` | autonomous-parallel | 0 | no recorded use and not a core methodology |
| `click-path-audit` | — | 0 | no recorded use and not a core methodology |
| `coding-standards` | — | 0 | no recorded use and not a core methodology |
| `content-engine` | — | 0 | no recorded use and not a core methodology |
| `content-hash-cache-pattern` | — | 0 | no recorded use and not a core methodology |
| `continuous-agent-loop` | autonomous-parallel | 0 | no recorded use and not a core methodology |
| `crosspost` | — | 0 | no recorded use and not a core methodology |
| `data-scraper-agent` | — | 0 | no recorded use and not a core methodology |
| `docker-patterns` | deployment | 0 | no recorded use and not a core methodology |
| `enterprise-agent-ops` | autonomous-parallel | 0 | no recorded use and not a core methodology |
| `frontend-slides` | — | 0 | no recorded use and not a core methodology |
| `liquid-glass-design` | — | 0 | no recorded use and not a core methodology |
| `loop-me` | — | 0 | no recorded use and not a core methodology |
| `nutrient-document-processing` | — | 0 | no recorded use and not a core methodology |
| `project-guidelines-example` | — | 0 | no recorded use and not a core methodology |
| `ralphinho-rfc-pipeline` | autonomous-parallel | 0 | no recorded use and not a core methodology |
| `regex-vs-llm-structured-text` | — | 0 | no recorded use and not a core methodology |
| `request-refactor-plan` | — | 0 | no recorded use and not a core methodology |
| `rules-distill` | — | 0 | no recorded use and not a core methodology |
| `safety-guard` | — | 0 | no recorded use and not a core methodology |
| `santa-method` | — | 0 | no recorded use and not a core methodology |
| `scaffold-exercises` | — | 0 | no recorded use and not a core methodology |
| `security-scan` | — | 0 | no recorded use and not a core methodology |
| `setup-matt-pocock-skills` | — | 0 | no recorded use and not a core methodology |
| `setup-pre-commit` | — | 0 | no recorded use and not a core methodology |
| `skill-stocktake` | — | 0 | no recorded use and not a core methodology |
| `teach` | — | 0 | no recorded use and not a core methodology |
| `team-builder` | autonomous-parallel | 0 | no recorded use and not a core methodology |
| `tech-docs` | — | 0 | no recorded use and not a core methodology |
| `wizard` | — | 0 | no recorded use and not a core methodology |
| `writing-beats` | — | 0 | no recorded use and not a core methodology |
| `writing-fragments` | — | 0 | no recorded use and not a core methodology |
| `writing-great-skills` | — | 0 | no recorded use and not a core methodology |
| `writing-shape` | — | 0 | no recorded use and not a core methodology |
| `x-api` | — | 0 | no recorded use and not a core methodology |

## KEEP (explicitly protected)

Matt Pocock methodology and Superpowers-adjacent capabilities are **KEEP** regardless of
telemetry — low dispatch counts reflect recent installation, not low value:

`grill-with-docs` · `domain-modeling` · `ubiquitous-language` · `to-spec` · `to-tickets` ·
`wayfinder` · `implement` · `prototype` · `research` · `diagnosing-bugs` · `codebase-design` ·
`handoff` · `triage` · `risk-based-tdd`

## Rollback

Any runtime change is reversible from two places: the preservation snapshot
`8a756b95b122ffad19f22199679bc6536d0a94d6` (byte-exact, `.gitattributes * -text`), and the
canonical source itself via `scripts/deploy-skills.py --deploy`.

