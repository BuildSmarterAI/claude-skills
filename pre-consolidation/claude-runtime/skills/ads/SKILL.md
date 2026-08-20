---
name: ads
description: >
  Comprehensive paid advertising audit and optimization for any business type.
  Performs full multi-platform audits (Google Ads, Meta Ads, LinkedIn Ads, TikTok
  Ads, Microsoft Ads), single-platform deep analysis, conversion tracking health
  checks, creative quality assessment, budget allocation optimization, bidding
  strategy evaluation, and compliance verification. Industry detection for SaaS,
  e-commerce, local service, B2B enterprise, info products, mobile app, real
  estate, healthcare, finance, and agency. Triggers on: "ads", "PPC", "paid
  advertising", "Google Ads", "Meta Ads", "Facebook Ads", "LinkedIn Ads",
  "TikTok Ads", "Microsoft Ads", "Bing Ads", "ad audit", "campaign audit",
  "ROAS", "conversion tracking", "creative fatigue", "bid strategy".
argument-hint: "audit | google | meta | youtube | linkedin | tiktok | microsoft | creative | landing | budget | plan <type> | competitor"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
---

# Ads — Multi-Platform Paid Advertising Audit & Optimization

Comprehensive ad account analysis across all major platforms (Google, Meta,
LinkedIn, TikTok, Microsoft). Orchestrates 13 specialized sub-skills and
7 subagents. Optional HYROS integration for independent attribution truth.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/ads audit` | Full multi-platform audit with parallel subagent delegation |
| `/ads google` | Google Ads deep analysis (Search, PMax, YouTube) |
| `/ads meta` | Meta Ads deep analysis (FB, IG, Advantage+) |
| `/ads youtube` | YouTube Ads specific analysis |
| `/ads linkedin` | LinkedIn Ads deep analysis (B2B, Lead Gen) |
| `/ads tiktok` | TikTok Ads deep analysis (Creative, Shop, Smart+) |
| `/ads microsoft` | Microsoft/Bing Ads deep analysis (Copilot, Import) |
| `/ads creative` | Cross-platform creative quality audit |
| `/ads landing` | Landing page quality assessment for ad campaigns |
| `/ads budget` | Budget allocation and bidding strategy review |
| `/ads plan <business-type>` | Strategic ad plan with industry templates |
| `/ads competitor` | Competitor ad intelligence analysis |
| `/ads hyros` | HYROS attribution audit (optional — requires API key) |

## Orchestration Logic

When the user invokes `/ads audit`, delegate to subagents in parallel:
1. Collect account data (exports, screenshots, or API access details)
2. Detect business type and identify active platforms
3. **HYROS check**: If `HYROS` env var is present in `.env`, run `fetch_hyros_data.py` first to generate `output/hyros_data.json`
4. Spawn subagents: audit-google, audit-meta, audit-creative, audit-tracking, audit-budget, audit-compliance, and optionally audit-hyros (if HYROS API key present)
5. Collect results and generate unified report with Ads Health Score (0-100)
6. If HYROS data available, include cross-platform attribution variance analysis
7. Create prioritized action plan with Quick Wins

For individual commands (`/ads google`, `/ads meta`, etc.), load the relevant
sub-skill directly.

## Industry Detection

Detect business type from ad account signals:
- **SaaS**: trial_start/demo_request events, pricing page targeting, long attribution windows
- **E-commerce**: purchase events, product catalog/feed, Shopping/PMax campaigns
- **Local Service**: call extensions, location targeting, store visits, directions events
- **B2B Enterprise**: LinkedIn Ads active, ABM lists, high CPA tolerance ($50+), long sales cycle
- **Info Products**: webinar/course funnels, lead gen forms, low-ticket offers
- **Mobile App**: app install campaigns, in-app events, deep linking
- **Real Estate**: listing feeds, property-specific landing pages, geo-heavy targeting
- **Healthcare**: HIPAA compliance flags, healthcare-specific ad policies
- **Finance**: Special Ad Categories declared, financial products compliance
- **Agency**: multiple client accounts, white-label reporting needs

## Quality Gates

Hard rules — never violate these:
- Never recommend Broad Match without Smart Bidding (Google)
- 3x Kill Rule: flag any ad group/campaign with CPA >3x target for pause
- Budget sufficiency: Meta ≥5x CPA per ad set, TikTok ≥50x CPA per ad group
- Learning phase: never recommend edits during active learning phase
- Compliance: always check Special Ad Categories for housing/employment/credit/finance
- Creative: never run silent video ads on TikTok (sound-on platform)
- Attribution: default to 7-day click / 1-day view (Meta), data-driven (Google)

## Reference Files

Load these on-demand as needed — do NOT load all at startup.

**Path resolution:** All references are installed at `~/.claude/skills/ads/references/`.
When sub-skills or agents reference `ads/references/*.md`, resolve to
`~/.claude/skills/ads/references/*.md`.

- `references/scoring-system.md` — Weighted scoring algorithm and grading thresholds
- `references/benchmarks.md` — Industry benchmarks by platform (CPC, CTR, CVR, ROAS)
- `references/bidding-strategies.md` — Bidding decision trees per platform
- `references/budget-allocation.md` — Platform selection matrix, scaling rules, MER
- `references/platform-specs.md` — Creative specifications across all platforms
- `references/conversion-tracking.md` — Pixel, CAPI, EMQ, ttclid implementation
- `references/compliance.md` — Regulatory requirements, ad policies, privacy
- `references/google-audit.md` — 74-check Google Ads audit checklist
- `references/meta-audit.md` — 46-check Meta Ads audit checklist
- `references/linkedin-audit.md` — 25-check LinkedIn Ads audit checklist
- `references/tiktok-audit.md` — 25-check TikTok Ads audit checklist
- `references/microsoft-audit.md` — 20-check Microsoft Ads audit checklist
- `references/hyros-audit.md` — 20-check HYROS attribution audit checklist (optional)

## Scoring Methodology

### Ads Health Score (0-100)

Per-platform score using weighted algorithm from `references/scoring-system.md`.
Cross-platform aggregate weighted by budget share:

```
Aggregate = Sum(Platform_Score x Platform_Budget_Share)
```

### Grading

| Grade | Score | Action Required |
|-------|-------|-----------------|
| A | 90-100 | Minor optimizations only |
| B | 75-89 | Some improvement opportunities |
| C | 60-74 | Notable issues need attention |
| D | 40-59 | Significant problems present |
| F | <40 | Urgent intervention required |

### Priority Levels

- **Critical**: Revenue/data loss risk (fix immediately)
- **High**: Significant performance drag (fix within 7 days)
- **Medium**: Optimization opportunity (fix within 30 days)
- **Low**: Best practice, minor impact (backlog)

## Sub-Skills

This skill orchestrates 13 specialized sub-skills:

1. **ads-audit** — Full multi-platform audit with parallel delegation
2. **ads-google** — Google Ads deep analysis (Search, PMax, YouTube)
3. **ads-meta** — Meta Ads deep analysis (FB, IG, Advantage+)
4. **ads-youtube** — YouTube Ads specific analysis
5. **ads-linkedin** — LinkedIn Ads deep analysis
6. **ads-tiktok** — TikTok Ads deep analysis
7. **ads-microsoft** — Microsoft/Bing Ads deep analysis
8. **ads-creative** — Cross-platform creative quality audit
9. **ads-landing** — Landing page quality for ad campaigns
10. **ads-budget** — Budget allocation and bidding strategy
11. **ads-plan** — Strategic ad planning with industry templates
12. **ads-competitor** — Competitor ad intelligence
13. **ads-hyros** — HYROS attribution audit (optional — requires HYROS API key in `.env`)

## Subagents

For parallel analysis during full audits:
- `audit-google` — Google Ads checks (G01-G74)
- `audit-meta` — Meta Ads checks (M01-M46)
- `audit-creative` — Creative quality for LinkedIn, TikTok, Microsoft
- `audit-tracking` — Conversion tracking health across all platforms
- `audit-budget` — Budget, bidding, structure for LinkedIn, TikTok, Microsoft
- `audit-compliance` — Compliance, settings, performance across all platforms
- `audit-hyros` — HYROS attribution checks H01-H20 (optional — only if HYROS API key present in `.env`)

## HYROS Cross-Reference (Optional)

When the `HYROS` environment variable is detected in `.env`, all platform sub-skills
and agents should use HYROS data for independent attribution comparison:

1. Run `~/.claude/skills/ads/scripts/fetch_hyros_data.py --env-file .env --output output/hyros_data.json` before platform analysis
2. Each platform skill reads `output/hyros_data.json` to compare platform-reported vs HYROS-attributed conversions/revenue
3. Calculate over-reporting %: (Platform - HYROS) / HYROS x 100
4. Flag campaigns with >30% variance for manual review
5. Use HYROS true ROAS for kill/scale budget recommendations

If HYROS key is NOT present, skip all HYROS sections entirely (no warning needed).
