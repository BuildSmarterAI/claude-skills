---
name: ads-hyros
description: >
  HYROS attribution tracking audit and cross-platform truth analysis.
  Evaluates 20 checks across API setup, attribution accuracy, integration
  health, and reporting. Provides independent attribution data to compare
  against platform-reported metrics. Use when user says "HYROS", "hyros",
  "attribution tracking", "true ROAS", "HYROS audit", or "attribution audit".
---

# HYROS Attribution Audit

## Process

### Step 1: Collect Data via API

Run the HYROS API script to pull attribution data:

```bash
python3 ~/.Codex/skills/ads/scripts/fetch_hyros_data.py \
  --env-file .env \
  --output output/hyros_data.json \
  --verbose
```

For dry-run validation only:
```bash
python3 ~/.Codex/skills/ads/scripts/fetch_hyros_data.py \
  --env-file .env \
  --dry-run
```

**What the API collects:**
- Lead data with source attribution (email, source, tags)
- Sales data with revenue attribution (email, amount, product, source)
- Custom events (funnel events, upsells, refunds)
- Derived metrics: revenue by source, platform attribution, lead-to-sale rate

### Step 2: Load Reference Materials

Read these files to score the audit:
1. `ads/references/hyros-audit.md` — full 20-check audit framework
2. `ads/references/scoring-system.md` — weighted scoring methodology
3. `ads/references/benchmarks.md` — platform benchmarks for variance comparison

### Step 3: Evaluate All 20 Checks

Using the API data, evaluate each check as PASS, WARNING, or FAIL.

**API-powered checks (automatic from JSON):**

API & Tracking Setup:
- H01: API key valid → check `metadata.errors` for auth failures
- H05: Revenue mapping → check `derived.has_revenue_data` and `sales.total_revenue`

Attribution Accuracy:
- H07: Cross-platform consistency → check `attribution.platform_attribution` for all platforms
- H08: HYROS vs platform variance → compare `attribution.platform_attribution` against platform data
- H09: Lead-to-sale path → check `attribution.lead_to_sale_rate`
- H10: Organic vs paid → check `derived.has_source_tagging`

Reporting & ROI:
- H16: True ROAS → check `derived.revenue_attribution_available`
- H18: Funnel tracking → check `derived.has_leads`, `has_sales`, `has_events`
- H19: Refund tracking → check `attribution.refund_count`

**Manual checks (require user input or HYROS dashboard access):**
- H02: Tracking pixel installed (check site source or HYROS dashboard)
- H03: UTM parameters (check ad platform URL templates)
- H04: Custom events (check HYROS event configuration)
- H06: Multi-touch model (check HYROS attribution settings)
- H11: API connectivity timing (check HYROS dashboard)
- H12: Webhook delivery (check HYROS webhook logs)
- H13: Ad platform connections (check HYROS integrations page)
- H14: Payment processor sync (check HYROS payment settings)
- H15: CRM sync (check HYROS CRM integration)
- H17: Campaign-level reports (check HYROS reporting dashboard)
- H20: LTV enabled (check HYROS LTV settings)

### Step 4: Calculate HYROS Health Score (0-100)

Apply weighted scoring per `ads/references/scoring-system.md`:
- API & Tracking Setup: 30% weight
- Attribution Accuracy: 30% weight
- Integration Health: 20% weight
- Reporting & ROI: 20% weight

### Step 5: Generate Cross-Platform Comparison

When platform audit data is also available, generate the HYROS Cross-Reference:

| Metric | Platform-Reported | HYROS-Attributed | Variance |
|--------|------------------|------------------|----------|
| Conversions | X | Y | Z% |
| Revenue | $X | $Y | Z% |
| ROAS | X.Xx | Y.Yx | Z% |

Flag any platform with >30% variance for manual review.

### Step 6: Generate Report

Produce the final `HYROS-REPORT.md` with all findings.

## HYROS Cross-Reference Guide

The primary value of HYROS is exposing platform over-reporting. Every ad platform
(Google, Meta, LinkedIn, TikTok, Microsoft) over-claims conversions due to:
- View-through attribution inflation
- Cross-device double-counting
- Post-iOS 14.5 modeled conversions (Meta)
- Broad match attribution (Google)

### How to Use HYROS Data

1. **True ROAS**: Use HYROS revenue attribution instead of platform-reported ROAS
2. **Kill/Scale decisions**: Base budget decisions on HYROS CPA, not platform CPA
3. **Platform comparison**: Use HYROS as neutral arbiter when platforms disagree
4. **Creative evaluation**: Map HYROS revenue to specific creatives for true performance
5. **Funnel analysis**: Track full lead → sale → LTV path that no single platform can see

### Over-Reporting Benchmarks

Typical platform over-reporting vs HYROS (varies by industry):

| Platform | Typical Over-Reporting | Notes |
|----------|----------------------|-------|
| Google Ads | 10-25% | View-through and cross-device inflation |
| Meta Ads | 20-40% | Post-iOS 14.5 modeled conversions |
| TikTok Ads | 30-60% | Aggressive view-through attribution |
| LinkedIn Ads | 15-30% | Long B2B sales cycles inflate attribution |
| YouTube | 25-50% | View-through attribution on video views |
| Microsoft Ads | 10-20% | Smaller audience, less overlap |

## Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| API connectivity | <24hr | 24-72hr | >72hr |
| Platform variance | <20% | 20-40% | >40% |
| Lead-to-sale rate | Tracked | Partial | Not tracked |
| Revenue mapping | All products | Some products | No revenue |
| Funnel stages | ≥3 stages | 2 stages | 1 stage |

## Output

### HYROS Health Score

```
HYROS Attribution Health Score: XX/100 (Grade: X)

API & Tracking Setup:    XX/100  ████████░░  (30%)
Attribution Accuracy:    XX/100  ██████████  (30%)
Integration Health:      XX/100  ███████░░░  (20%)
Reporting & ROI:         XX/100  █████░░░░░  (20%)
```

### Deliverables
- `HYROS-REPORT.md` — Full 20-check findings with pass/warning/fail
- Cross-platform attribution variance table
- True ROAS by source/campaign
- Platform over-reporting analysis
- Kill/scale recommendations based on true attribution
- Quick Wins sorted by impact
