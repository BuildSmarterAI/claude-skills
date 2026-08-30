# Claude Code Skills — BuildSmarter Holdings

Curated and optimized Claude Code skills for the BuildSmarter Holdings ecosystem.

## Portfolio

| Entity | Focus |
|--------|-------|
| **SiteIntel™** | GIS-based CRE feasibility intelligence |
| **ConstructIntel.ai** | AI-powered construction cost & bid intelligence |
| **Maxx Builders** | Commercial GC, $3-15M projects |
| **Maxx Designers** | Architecture firm |
| **BuildSmarter AI** | AI construction management platform |
| **Buzz Digital Agency** | CRE digital marketing |

## Stack

- **Frontend:** React, TypeScript, Next.js, Tailwind CSS, shadcn/ui
- **Backend:** Supabase (PostgreSQL, Auth, Edge Functions, Storage, Realtime)
- **Processing:** Google Cloud Run (Python/FastAPI)
- **AI/LLM:** Anthropic Claude API, Google Gemini
- **GIS:** PostGIS, MapLibre GL, Google Maps API
- **Hosting:** Vercel (frontend), GCP (backend)

## Skills Overview

### Core Development
| Skill | Purpose |
|-------|---------|
| `api-design` | REST API patterns for TypeScript/Next.js, Supabase, Python/FastAPI |
| `backend-patterns` | Edge Function → Cloud Run architecture, repository/service patterns |
| `coding-standards` | TypeScript, React, Tailwind, Python naming and conventions |
| `frontend-patterns` | React components, Supabase hooks, state management, performance |
| `python-patterns` | FastAPI, Pydantic, async pipelines, Cloud Run services |
| `supabase-patterns` | RLS, Edge Functions, Storage, Realtime, CLI workflows |
| `postgres-patterns` | Query optimization, indexing, schema design |

### Testing & Quality
| Skill | Purpose |
|-------|---------|
| `e2e-testing` | Playwright patterns for SiteIntel/ConstructIntel |
| `python-testing` | pytest for FastAPI, pipeline testing, Supabase mocking |
| `security-review` | Auth, RLS, secrets, input validation, XSS/CSRF |
| `tdd-workflow` | Test-driven development discipline |

### AI & Data
| Skill | Purpose |
|-------|---------|
| `cost-aware-llm-pipeline` | Claude/Gemini model routing, budget tracking, prompt caching |
| `regex-vs-llm-structured-text` | Hybrid parsing for bid documents and permits |
| `content-hash-cache-pattern` | SHA-256 caching for PDF processing results |

### Infrastructure
| Skill | Purpose |
|-------|---------|
| `deployment-patterns` | Vercel, Cloud Run, Edge Function deployment and CI/CD |
| `database-migrations` | Supabase CLI migrations, zero-downtime patterns |

### Content & Business
| Skill | Purpose |
|-------|---------|
| `article-writing` | Blog posts, case studies, guides for construction/PropTech |
| `content-engine` | Social media, multi-platform campaigns |
| `investor-materials` | Pitch decks, one-pagers, investor memos |
| `investor-outreach` | Cold emails, follow-ups, investor communications |
| `market-research` | Competitive analysis, industry research |
| `proptech-product-strategy` | Pricing, sprint planning, GTM, feature prioritization |

### Copy OS
Reusable copywriting and marketing-intelligence methodology. **Methodology is global; truth is
local** — these skills carry no company facts and read repository-local context before writing
anything company-specific. See [`docs/copy-os.md`](docs/copy-os.md).

| Skill | Purpose |
|-------|---------|
| `copy-os` | Router + shared contracts: routing table, Copy Brief schema, fact-provenance rules |
| `copy-strategist` | Awareness stage, market sophistication, proof inventory, offer architecture |
| `direct-response-copy` | Headlines, leads, body architecture, offers, CTAs, editing rules |
| `persuasion-engine` | Behavioral principles matched to audience temperature, with hard stops |
| `copychief` | Adversarial review: 15 scored dimensions, an exact rewrite per defect |
| `humanizer` | Final editorial pass removing AI tells without weakening the copy |
| `compliance-review` | Claim substantiation ledger, platform exposure, human-review routing |
| `landing-page-copy` | Page structure and section copy with message match to the traffic source |
| `ad-copy` | Paid ad copy per platform intent and format limits |
| `email-copy` | Cold, nurture, lifecycle email plus sequence architecture |
| `social-copy` | Organic social posts and short-video scripts in native register |

### Meta / Utility
| Skill | Purpose |
|-------|---------|
| `continuous-learning-v2` | Instinct-based learning from Claude Code sessions |
| `eval-harness` | Evaluation framework for Claude Code |
| `search-first` | Research-before-coding workflow |
| `skill-stocktake` | Audit and quality-check skills |
| `strategic-compact` | Context management for long sessions |
| `verification-loop` | Session verification system |

## Installation

```bash
git clone https://github.com/BuildSmarterAI/claude-skills.git ~/.claude/skills
```

## Updating

```bash
cd ~/.claude/skills
git pull
```

## Syncing Changes

After modifying skills on any machine:

```bash
cd ~/.claude/skills
git add -A
git commit -m "Update: description of changes"
git push
```

Then on other machines:

```bash
cd ~/.claude/skills
git pull
```

## Audit History

- **Initial audit:** March 2026
- **Skills removed:** 25+ irrelevant language/framework skills (Django, Spring Boot, Swift, Go, Kotlin, Laravel, Rust, Perl, etc.)
- **Skills rewritten:** 18 skills customized for BuildSmarter stack (Supabase, Cloud Run, FastAPI, React/TypeScript)
- **Skills created:** 2 new skills (supabase-patterns, proptech-product-strategy)
- **Result:** 57 → 34 focused skills with 40% noise reduction

## License

Private — BuildSmarter Holdings internal use only.
