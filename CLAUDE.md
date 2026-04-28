# CLAUDE.md — Repository Guide for AI Assistants

This file orients Claude Code (and other AI assistants) working inside this repo. Read it before editing.

## What this repository is

`claude-skills` is BuildSmarter Holdings' curated library of **Claude Code skills**. Each top-level directory is one skill. The repo is consumed by cloning it to `~/.claude/skills` so Claude Code can load skills at runtime — there is no application to build or run.

- **No build, no tests, no linters at the root.** Validation = "does the SKILL.md render and is the YAML frontmatter valid?"
- **Content repository.** Do not introduce `package.json`, lockfiles, or framework code at the root.
- **Skills are markdown-first.** A few skills also ship Python or `.mjs` scripts under sub-directories.

For the portfolio context, stack overview, and install commands, see `README.md`.

## Repository layout

```
/                          # README.md, this file
<skill-name>/              # one folder per skill, kebab-case
  SKILL.md                 # required for standard skills (YAML frontmatter + body)
  CLAUDE.md                # used INSTEAD of SKILL.md by team aggregator skills only
  scripts/    agents/      # optional sub-dirs for complex skills
  hooks/      commands/
  rules/      references/
  prompts/    fixtures/
  tests/      config.json
```

There are ~129 skill folders. All folder names are **kebab-case** and match the `name` field in their frontmatter.

### Standard skills

A standard skill is a single `SKILL.md` file. See `api-design/SKILL.md` for the canonical example.

### Complex / meta skills

A few skills add sub-directories when markdown alone is not enough:

- `continuous-learning-v2/` — `agents/`, `hooks/`, `scripts/`, `config.json` (session-automation framework).
- `ck/` — `commands/` (`.mjs` CLI handlers), `hooks/` (CLI extension).
- `skill-comply/` — `prompts/`, `scripts/`, `tests/`, `fixtures/`, `pyproject.toml` (validation tooling).
- `remotion-video-creation/` — `rules/` (per-topic markdown rule files).
- `lead-intelligence/`, `brand-voice/`, `videodb/`, `manim-video/`, `rules-distill/`, `skill-stocktake/` — assorted `agents/`, `references/`, `assets/`, `scripts/`.

### Team aggregator skills (use `CLAUDE.md`, not `SKILL.md`)

These seven folders are routing/index documents for clusters of related sub-skills and Python tools — they intentionally use `CLAUDE.md` instead of `SKILL.md`. Preserve that pattern when extending them:

- `engineering-team/` · `product-team/` · `project-management/`
- `marketing-skill/` · `business-growth/` · `finance/` · `c-level-advisor/`

Do **not** add `CLAUDE.md` files inside ordinary skill folders. The only `CLAUDE.md` at the repo root is this file.

## SKILL.md format (authoritative)

```markdown
---
name: api-design
description: REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs.
origin: ECC
---

# API Design Patterns

Conventions and best practices for designing consistent, developer-friendly REST APIs.

## When to Activate

- Designing new API endpoints
- Reviewing existing API contracts
- ...

## <Topical Section>

<prose + fenced code blocks tagged with a language>
```

**Frontmatter keys:**
- `name` — required; must equal the folder name (kebab-case).
- `description` — required; 1–2 concrete, action-oriented sentences. The harness matches against this string when deciding whether to load the skill, so keep it specific.
- `origin` — optional attribution (e.g. `ECC`).

**Body conventions:**
- `# Title` immediately after frontmatter.
- `## When to Activate` bullet list near the top.
- Topical `##` sections with examples in fenced code blocks (` ```python `, ` ```typescript `, ` ```bash `, etc.).
- Length norm: 5–15 KB. Trim aggressively before exceeding 20 KB.

Reference: `api-design/SKILL.md:1-19`.

## Skill categories

Mirrors the index in `README.md`. Browse the relevant category before creating a new skill — most needs already have a home.

| Category | Examples |
|----------|----------|
| Core Development | `api-design`, `backend-patterns`, `coding-standards`, `frontend-patterns`, `python-patterns`, `postgres-patterns` |
| Testing & Quality | `e2e-testing`, `python-testing`, `security-review`, `tdd-workflow` |
| AI & Data | `cost-aware-llm-pipeline`, `regex-vs-llm-structured-text`, `content-hash-cache-pattern`, `claude-api` |
| Infrastructure | `deployment-patterns`, `database-migrations`, `docker-patterns` |
| Content & Business | `article-writing`, `content-engine`, `investor-materials`, `market-research` |
| Meta / Utility | `continuous-learning-v2`, `eval-harness`, `search-first`, `skill-stocktake`, `strategic-compact`, `verification-loop` |
| Team aggregators | `engineering-team`, `product-team`, `project-management`, `marketing-skill`, `business-growth`, `finance`, `c-level-advisor` |

## Tech stack assumed by skill examples

When you write or edit code samples inside a skill, default to this stack so examples stay consistent across the library:

- **Frontend:** React, TypeScript, Next.js, Tailwind, shadcn/ui
- **Backend:** Supabase (Postgres, Auth, Edge Functions, Storage, Realtime)
- **Processing:** Google Cloud Run (Python / FastAPI)
- **AI / LLM:** Anthropic Claude API, Google Gemini
- **GIS:** PostGIS, MapLibre GL, Google Maps API
- **Hosting:** Vercel (frontend), GCP (backend)

## Conventions when adding or editing skills

1. **Search before creating.** Grep across `*/SKILL.md` and `*/CLAUDE.md` for the topic first. Extend the existing skill instead of creating a near-duplicate.
2. **Folder name = `name` frontmatter value**, kebab-case. No prefixes/suffixes.
3. **One concern per skill.** Don't bundle unrelated topics.
4. **Keep `description` concrete.** It's what the harness matches against — vague descriptions never get loaded.
5. **Prefer markdown.** Add a sub-directory (`scripts/`, `agents/`, `hooks/`, etc.) only when a single `SKILL.md` cannot express the skill.
6. **Preserve aggregator pattern.** Team folders use `CLAUDE.md` and list sub-skills + tools; do not convert them to `SKILL.md`.
7. **Update `README.md`** when adding a skill that fits one of the existing category tables.
8. **Don't add tooling at the root.** No `package.json`, no CI, no schema validators unless explicitly requested.

## Git workflow

- The default branch is `main`. Never push directly to `main`.
- Develop on the feature branch the harness specifies (e.g. `claude/add-claude-documentation-IaLZN`).
- Commit subject style follows the repo's existing pattern: short imperative — `Add: …`, `Update: …`, `Fix: …` (see install/update notes in `README.md`).
- Push with `git push -u origin <branch>`. Retry transient network failures with exponential backoff; do not force-push.
- There is no CI to wait on.

## Anti-patterns

- ❌ Creating a new skill when an existing one covers the topic.
- ❌ Adding `CLAUDE.md` inside a standard skill folder (use `SKILL.md`).
- ❌ Frontmatter `description` longer than ~2 sentences, or written as marketing copy rather than triggers.
- ❌ Mismatched `name` and folder name.
- ❌ Committing `.env`, API keys, customer data, or `node_modules` / virtualenvs.
- ❌ Introducing root-level tooling, build steps, or framework code.
- ❌ Editing many skills at once for a single conceptual change without confirming the diff.

## Useful pointers

- Canonical `SKILL.md`: `api-design/SKILL.md`
- Canonical team-aggregator `CLAUDE.md`: `engineering-team/CLAUDE.md`
- Canonical complex-skill layout: `continuous-learning-v2/`
- Canonical CLI-extension skill: `ck/`
- Portfolio + install/update commands: `README.md`
