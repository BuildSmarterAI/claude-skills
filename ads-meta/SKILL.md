---
name: ads-meta
description: >
  Meta Ads deep analysis covering Facebook and Instagram advertising.
  Evaluates 46 checks across Pixel/CAPI health, creative diversity and fatigue,
  account structure, and audience targeting. Includes Advantage+ assessment.
  Use when user says "Meta Ads", "Facebook Ads", "Instagram Ads", "Advantage+",
  or "Meta campaign".
---

# Meta Ads Deep Analysis

## Process (API-First Workflow)

Follow these steps in order. The API script handles 40 of 46 checks automatically.

### Step 0 (Optional): Collect HYROS Data

If the `HYROS` API key is available in `.env`, run the HYROS fetch script first:

```bash
python3 ~/.claude/skills/ads/scripts/fetch_hyros_data.py \
  --env-file .env \
  --output output/hyros_data.json \
  --verbose
```

This provides independent attribution data for cross-referencing Meta-reported metrics.

### Step 1: Collect Data via API

Run the Meta Marketing API script to pull all available data:

```bash
python3 ~/.claude/skills/ads/scripts/fetch_meta_ads.py \
  --env-file .env \
  --output output/meta_audit_data.json \
  --verbose
```

For campaign-specific audit:
```bash
python3 ~/.claude/skills/ads/scripts/fetch_meta_ads.py \
  --env-file .env \
  --campaign CAMPAIGN_ID \
  --output output/meta_audit_data.json \
  --verbose
```

**What the API collects automatically (no user action needed):**
- Campaign structure, budgets, objectives, bid strategies
- Ad set targeting, exclusions, attribution settings, learning phase status
- Ad creative references, format types (image/video/carousel)
- Account-level insights: CTR, CPC, CPM, ROAS, frequency, reach, spend
- Campaign-level and ad-set-level performance metrics
- Ad-level insights with quality rankings (quality_ranking, engagement_rate_ranking, conversion_rate_ranking)
- Placement breakdowns (Feed, Stories, Reels, etc.) with spend/CTR/conversions
- Age/gender demographic breakdowns
- CTR timeseries for fatigue detection (14-day daily data)
- Custom audiences (types, sizes, freshness)
- Pixel IDs and last fired times
- Derived metrics: fatigue alerts, budget adequacy, format counts, learning phase %

After the script runs, read the output JSON file for the full data payload.

### Step 2: Supplement with Manual Data (6 Chrome-Only Checks)

Only 6 of 46 checks require Events Manager access — the API cannot provide these:

| Check | What to Verify | Where to Check |
|-------|---------------|----------------|
| M02: CAPI active | Conversions API sending server events | Events Manager > Settings > CAPI status |
| M03: Dedup rate | Event deduplication ≥90% | Events Manager > Test Events > dedup % |
| M04: EMQ score | Event Match Quality ≥8.0 for Purchase | Events Manager > Overview > Purchase event EMQ |
| M05: Domain verified | Domain ownership confirmed | Business Settings > Brand Safety > Domains |
| M06: AEM config | Aggregated Event Measurement prioritized | Events Manager > AEM tab > event priority list |
| M08: CAPI Gateway | Gateway status (if applicable) | Events Manager > Settings > CAPI Gateway |

**To get this data, either:**
a) Ask the user: "I need 6 pieces of info that aren't available via API. Can you check Events Manager and tell me:
   1. Is CAPI active? (Events Manager > Settings)
   2. What's the dedup rate? (Test Events tab)
   3. What's the EMQ score for Purchase? (Overview > Purchase event)
   4. Is the domain verified? (Business Settings > Domains)
   5. Is AEM configured with event priorities? (AEM tab)
   6. Is CAPI Gateway active? (Settings > Gateway)"

b) Use Chrome browser tools to check directly if the user has Events Manager open

### Step 3: Load Reference Materials

Read these files to score the audit:
1. `ads/references/meta-audit.md` — full 46-check audit framework
2. `ads/references/benchmarks.md` — Meta-specific benchmarks
3. `ads/references/scoring-system.md` — weighted scoring methodology

### Step 4: Evaluate All 46 Checks

Using the API data + manual data, evaluate each check as PASS, WARNING, or FAIL.

**API-powered checks (automatic from JSON):**

Pixel/CAPI Health:
- M01: Pixel installed and firing → check `pixels` array for IDs and `last_fired_time`
- M07: Standard events configured → check `insights` for action types (ViewContent, AddToCart, Purchase, Lead)
- M09: Pixel value/currency → check ad-level `action_values` for currency params
- M10: Customer info params → check custom audiences for data_source types

Creative:
- M11: ≥3 formats → check `derived.creative_format_counts` and `creative_format_unique`
- M12: ≥5 creatives/ad set → check `derived.avg_creatives_per_adset` and `min_creatives_per_adset`
- M13: Fatigue detection → check `derived.fatigue_alerts` for CTR drop >20%
- M14-M18: Quality rankings → check `derived.ad_quality_rankings`, `below_avg_quality_count`

Account Structure:
- M19: CBO vs ABO → check `derived.cbo_campaign_count` vs `abo_campaign_count`
- M20: Campaign consolidation → check `derived.campaigns_by_objective`
- M21: Learning phase → check `derived.adsets_in_learning_limited_pct` (<30% pass, >50% fail)
- M22: Budget adequacy → check `derived.budget_analysis` (adequate/marginal/insufficient)
- M23: Attribution → check `derived.attribution_configs`
- M24: Naming conventions → inspect campaign/adset/ad name patterns

Audience:
- M25: Frequency → check `derived.account_frequency` and `avg_frequency_overall`
- M26: Custom audiences → check `derived.audience_types` and `total_custom_audiences`
- M27: Placement mix → check `derived.placement_performance` for spend distribution
- M28: Demographics → check `derived.demographic_performance` for concentration

**Manual checks (from Step 2):**
- M02: CAPI active → user/Chrome input
- M03: Dedup rate → user/Chrome input
- M04: EMQ score → user/Chrome input
- M05: Domain verified → user/Chrome input
- M06: AEM configured → user/Chrome input
- M08: CAPI Gateway → user/Chrome input

### Step 5: Calculate Meta Ads Health Score (0-100)

Apply weighted scoring per `ads/references/scoring-system.md`:
- Pixel / CAPI Health: 30% weight
- Creative: 30% weight
- Account Structure: 20% weight
- Audience & Targeting: 20% weight

### Step 6: Generate Report

Produce the final `META-ADS-REPORT.md` with all findings.

## What to Analyze

### Pixel / CAPI Health (30% weight)
- Meta Pixel installed and firing on all pages
- Conversions API (CAPI) active (30-40% data loss without it post-iOS 14.5)
- Event deduplication configured (event_id matching, ≥90% dedup rate)
- Event Match Quality (EMQ) ≥8.0 for Purchase event
- All standard events configured (ViewContent, AddToCart, Purchase, Lead)
- Custom conversions created for non-standard events
- Aggregated Event Measurement (AEM) configured for iOS
- Domain verification completed
- Server-side events include customer_information parameters
- Pixel fires with correct currency and value parameters

### Creative (30% weight)
- ≥3 creative formats active (image, video, carousel, collection)
- ≥5 creatives per ad set (Meta recommendation)
- Creative fatigue detection: CTR drop >20% over 14 days = FAIL
- Video creative: 15s max for Stories/Reels, 30s max for Feed
- UGC/testimonial creative tested
- Dynamic Creative Optimization (DCO) tested
- Ad copy: headline under 40 chars, primary text under 125 chars
- Creative refresh cadence: every 2-4 weeks for high-spend
- Quality ranking: ads with BELOW_AVERAGE quality_ranking flagged
- Engagement ranking: ads with BELOW_AVERAGE engagement_rate_ranking flagged
- Conversion ranking: ads with BELOW_AVERAGE conversion_rate_ranking flagged

### Account Structure (20% weight)
- Campaign Budget Optimization (CBO) vs Ad Set Budget (ABO) intentional
- Campaign consolidation: ≤5 active campaigns per objective type
- Learning phase health: <30% ad sets in "Learning Limited" (FAIL >50%)
- Budget per ad set: ≥5x target CPA (minimum for learning phase exit)
- Ad set audience overlap <30% (Audience Overlap tool)
- Campaign naming conventions consistent and descriptive
- Advantage+ Shopping Campaigns (ASC) active for e-commerce
- Simplified campaign structure (fewer, larger ad sets preferred)

### Audience & Targeting (20% weight)
- Prospecting frequency (7-day): <3.0 (WARNING 3-5, FAIL >5)
- Retargeting frequency (7-day): <8.0 (WARNING 8-12, FAIL >12)
- Custom Audiences: website visitors, customer lists, engagement
- Lookalike Audiences: multiple seed sizes tested (1%, 3%, 5%)
- Advantage+ Audience tested vs manual targeting
- Interest targeting: broad enough for algorithm optimization
- Exclusions: purchasers excluded from prospecting, overlap managed
- Location targeting reviewed for relevance
- Placement performance: identify underperforming placements from breakdown data
- Demographic performance: flag age/gender segments with high spend but low conversion

## Advantage+ Assessment

If Advantage+ features are in use:
- **ASC (Shopping Campaigns)**: catalog connected, existing customer cap set
- **Advantage+ Audience**: performance vs manual audience compared
- **Advantage+ Creative**: enhancements enabled (text, brightness, music)
- **Advantage+ Placements**: enabled (let Meta optimize placement mix)
- **Budget allocation**: Advantage+ campaigns getting fair test budget

## Special Ad Categories

If ads are in restricted categories:
- Special Ad Category declared before campaign creation
- Targeting restrictions verified (no ZIP, age 18-65+ only, no Lookalike)
- Creative compliance with category-specific policies
- Read `ads/references/compliance.md` for full requirements

## EMQ Optimization Guide

| EMQ Score | Status | Action |
|-----------|--------|--------|
| 8.0-10.0 | Excellent | Maintain current setup |
| 6.0-7.9 | Good | Add more customer_information parameters |
| 4.0-5.9 | Fair | Implement CAPI, improve data quality |
| <4.0 | Poor | Critical: CAPI + Enhanced Matching required |

Key parameters to maximize EMQ:
- `em` (email) — highest match rate signal
- `ph` (phone) — second highest match signal
- `fn`, `ln` (first/last name) — improves match accuracy
- `ct`, `st`, `zp` (city, state, zip) — geographic matching
- `external_id` — CRM/user ID for cross-device matching

## Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| EMQ (Purchase) | ≥8.0 | 6.0-7.9 | <6.0 |
| Dedup rate | ≥90% | 70-90% | <70% |
| CTR | ≥1.0% | 0.5-1.0% | <0.5% |
| Creative formats | ≥3 | 2 | 1 |
| Creatives per ad set | ≥5 | 3-4 | <3 |
| Learning Limited | <30% | 30-50% | >50% |
| Budget per ad set | ≥5x CPA | 2-5x CPA | <2x CPA |
| Quality ranking | ABOVE/AVERAGE | — | BELOW_AVERAGE |
| Frequency (prospecting) | <3.0 | 3-5 | >5 |
| Frequency (retargeting) | <8.0 | 8-12 | >12 |

## Output

### Meta Ads Health Score

```
Meta Ads Health Score: XX/100 (Grade: X)

Pixel / CAPI Health: XX/100  ████████░░  (30%)
Creative:            XX/100  ██████████  (30%)
Account Structure:   XX/100  ███████░░░  (20%)
Audience:            XX/100  █████░░░░░  (20%)
```

### Deliverables
- `META-ADS-REPORT.md` — Full 46-check findings with pass/warning/fail
- EMQ improvement roadmap
- Creative fatigue alerts (any creative with CTR declining >20%)
- Ad quality ranking analysis (ads below average flagged with recommendations)
- Placement performance analysis (underperforming placements identified)
- Demographic insights (top/bottom performing age/gender segments)
- Quick Wins sorted by impact
- Advantage+ adoption recommendations

## HYROS Cross-Reference (Optional)

When `output/hyros_data.json` is available, enrich this analysis with independent attribution data:

1. Check if `output/hyros_data.json` exists (run `fetch_hyros_data.py` if not)
2. Read HYROS data and extract Meta attribution from `attribution.platform_attribution.meta`
3. Compare Meta-reported ROAS vs HYROS true ROAS
4. Identify Meta campaigns over-claiming by >30%
5. Use HYROS data for more accurate fatigue detection (revenue-based, not just CTR)
6. Add HYROS revenue attribution to the ad-level quality analysis

| Metric | Meta-Reported | HYROS-Attributed | Variance |
|--------|--------------|------------------|----------|
| Conversions | X | Y | Z% |
| Revenue | $X | $Y | Z% |
| ROAS | X.Xx | Y.Yx | Z% |

Meta typically over-reports by 20-40% post-iOS 14.5 due to modeled conversions.
Flag campaigns where Meta claims >30% more conversions than HYROS.

If HYROS data is NOT available, skip this section entirely.
