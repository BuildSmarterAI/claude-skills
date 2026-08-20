---
name: ads-audit
description: >
  Full multi-platform paid advertising audit with parallel subagent delegation.
  Analyzes Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads, and Microsoft Ads
  accounts. Generates health score per platform and aggregate score. Use when
  user says "audit", "full ad check", "analyze my ads", "account health check",
  or "PPC audit".
---

# Full Multi-Platform Ads Audit

## Process

1. **Collect account data** — request exports, screenshots, or API access
2. **Detect business type** — analyze account signals per ads orchestrator
3. **Identify active platforms** — determine which platforms are in use
4. **Delegate to subagents** (if available, otherwise run inline sequentially):
   - `audit-google` — Conversion tracking, wasted spend, structure, keywords, ads, settings (G01-G74)
   - `audit-meta` — Pixel/CAPI health, creative fatigue, structure, audience (M01-M46)
   - `audit-creative` — LinkedIn, TikTok, Microsoft creative checks + cross-platform synthesis
   - `audit-tracking` — LinkedIn, TikTok, Microsoft tracking + cross-platform tracking health
   - `audit-budget` — LinkedIn, TikTok, Microsoft budget/bidding + cross-platform allocation
   - `audit-compliance` — All-platform compliance, settings, performance benchmarks
   - `audit-hyros` — HYROS attribution checks H01-H20 (optional — only if HYROS API key present)
5. **Score** — calculate per-platform and aggregate Ads Health Score (0-100)
6. **Report** — generate prioritized action plan with Quick Wins

## Data Collection

Ask the user for available data. Accept any combination:
- Google Ads: account export, Change History, Search Terms Report
- Meta Ads: Ads Manager export, Events Manager screenshot, EMQ scores
- LinkedIn Ads: Campaign Manager export, Insight Tag status
- TikTok Ads: Ads Manager export, Pixel/Events API status
- Microsoft Ads: account export, UET tag status, import validation results
- HYROS: API key in `.env` (optional — provides independent attribution truth)

If no exports available, audit from screenshots or manual data entry.

If HYROS API key is available, run the HYROS fetch script first:
```bash
python3 ~/.claude/skills/ads/scripts/fetch_hyros_data.py --env-file .env --output output/hyros_data.json --verbose
```

## Scoring

Read `ads/references/scoring-system.md` for full algorithm.

### Per-Platform Weights

| Platform | Category Weights |
|----------|-----------------|
| Google | Conversion 25%, Waste 20%, Structure 15%, Keywords 15%, Ads 15%, Settings 10% |
| Meta | Pixel/CAPI 30%, Creative 30%, Structure 20%, Audience 20% |
| LinkedIn | Tech 25%, Audience 25%, Creative 20%, Lead Gen 15%, Budget 15% |
| TikTok | Creative 30%, Tech 25%, Bidding 20%, Structure 15%, Performance 10% |
| Microsoft | Tech 25%, Syndication 20%, Structure 20%, Creative 20%, Settings 15% |

### Aggregate Score

```
Aggregate = Sum(Platform_Score x Platform_Budget_Share)
Grade: A (90-100), B (75-89), C (60-74), D (40-59), F (<40)
```

## Output Files

- `ADS-AUDIT-REPORT.md` — Comprehensive multi-platform findings
- `ADS-ACTION-PLAN.md` — Prioritized recommendations (Critical > High > Medium > Low)
- `ADS-QUICK-WINS.md` — Items fixable in <15 minutes with high impact

## Report Structure

### Executive Summary
- Aggregate Ads Health Score (0-100) with grade
- Per-platform scores
- Business type detected
- Active platforms identified
- Top 5 critical issues across all platforms
- Top 5 quick wins across all platforms

### Per-Platform Sections
Each platform section includes:
- Platform Health Score with grade
- Category breakdown with pass/warning/fail per check
- Platform-specific Quick Wins
- Detailed findings with remediation steps

### Cross-Platform Analysis
- Budget allocation assessment (actual vs recommended)
- Tracking consistency (are all platforms tracking the same events?)
- Creative consistency (is messaging aligned across platforms?)
- Attribution overlap (are platforms double-counting conversions?)

### HYROS Attribution Layer (Optional)

When HYROS data is available (`output/hyros_data.json`), add to cross-platform analysis:
- Platform-reported conversions vs HYROS-attributed conversions (per platform)
- Over-reporting % per platform: (Platform - HYROS) / HYROS x 100
- True ROAS per platform using HYROS revenue attribution
- Campaigns flagged where platform claims >30% more conversions than HYROS
- MER (Marketing Efficiency Ratio) recalculated using HYROS-verified revenue
- Budget reallocation recommendations based on true attribution data

If HYROS data is NOT available, skip this section entirely.

### Strategic Recommendations
- Platform prioritization based on business type
- Budget reallocation recommendations
- Scaling opportunities (platforms/campaigns ready to scale)
- Kill list (campaigns/ad groups to pause immediately)

## Priority Definitions

- **Critical**: Revenue/data loss risk (fix immediately)
- **High**: Significant performance drag (fix within 7 days)
- **Medium**: Optimization opportunity (fix within 30 days)
- **Low**: Best practice, minor impact (backlog)

## Quick Wins Criteria

```
IF severity == "Critical" OR severity == "High"
AND estimated_fix_time < 15 minutes
THEN flag as Quick Win
SORT BY (severity_multiplier x estimated_impact) DESC
```
