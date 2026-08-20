# HYROS Attribution Audit Checklist

<!-- Updated: 2026-02-25 -->
<!-- Sources: HYROS API documentation, attribution best practices -->
<!-- Total Checks: 20 | Categories: 4 | See scoring-system.md for weights and algorithm -->

## Quick Reference

| Category | Weight | Check Count |
|----------|--------|-------------|
| API & Tracking Setup | 30% | H01-H05 (5 checks) |
| Attribution Accuracy | 30% | H06-H10 (5 checks) |
| Integration Health | 20% | H11-H15 (5 checks) |
| Reporting & ROI | 20% | H16-H20 (5 checks) |

---

## API & Tracking Setup (30% weight)

| ID | Check | Severity | Pass | Warning | Fail |
|----|-------|----------|------|---------|------|
| H01 | API key valid and active | Critical | API key authenticates successfully; returns 200 | Key works but some endpoints return errors | 401 unauthorized or key expired |
| H02 | Tracking pixel/script installed | Critical | HYROS tracking script firing on all pages | Firing on most pages (>90%) | Script not installed or not firing |
| H03 | UTM parameters configured | High | All ad platforms passing UTMs to HYROS (source, medium, campaign) | Some platforms passing UTMs | UTMs missing or inconsistent across platforms |
| H04 | Custom events configured | High | Key funnel events tracked (lead, sale, upsell, refund) | Basic events only (lead, sale) | No custom events configured |
| H05 | Revenue mapping active | Critical | Revenue values passing correctly for all products/offers | Revenue passing for some products | No revenue data flowing to HYROS |

---

## Attribution Accuracy (30% weight)

| ID | Check | Severity | Pass | Warning | Fail |
|----|-------|----------|------|---------|------|
| H06 | Multi-touch attribution active | Critical | Multi-touch model configured (first-touch + last-touch + linear available) | Single-touch model only | Attribution not configured |
| H07 | Cross-platform consistency | High | All active ad platforms connected and attributed in HYROS | Most platforms connected (>80%) | Major platforms missing from HYROS |
| H08 | HYROS vs platform variance | High | Variance <20% between HYROS and platform-reported conversions | Variance 20-40% | Variance >40% (tracking gap likely) |
| H09 | Lead-to-sale path tracking | High | Full funnel path visible (ad click → lead → sale) with source attribution | Partial path tracking (lead or sale only) | No path tracking configured |
| H10 | Organic vs paid tagging | Medium | Organic and paid traffic clearly separated with accurate source tagging | Some overlap between organic/paid attribution | No distinction between organic and paid sources |

---

## Integration Health (20% weight)

| ID | Check | Severity | Pass | Warning | Fail |
|----|-------|----------|------|---------|------|
| H11 | API connectivity | Critical | Successful API response within last 24 hours | Last successful response 24-72 hours ago | No successful API response in >72 hours |
| H12 | Webhook delivery | High | Webhooks firing for sale.attributed events with <1% failure rate | Webhook failure rate 1-5% | Webhook failure rate >5% or webhooks not configured |
| H13 | Ad platform connections | High | All active ad platforms (Google, Meta, TikTok, etc.) connected to HYROS | Most platforms connected | Major platforms disconnected |
| H14 | Payment processor sync | High | Payment processor (Stripe, PayPal, etc.) synced with accurate revenue | Payment processor connected but some transactions missing | Payment processor not connected |
| H15 | CRM sync active | Medium | CRM (HubSpot, Salesforce, etc.) synced with lead/sale data flowing | CRM connected but sync delayed >24 hours | CRM not connected to HYROS |

---

## Reporting & ROI (20% weight)

| ID | Check | Severity | Pass | Warning | Fail |
|----|-------|----------|------|---------|------|
| H16 | True ROAS calculated | Critical | HYROS true ROAS available per campaign/source with spend data | ROAS available at source level only (not campaign) | No ROAS calculation possible (missing spend or revenue) |
| H17 | Campaign-level reports | High | Attribution data available at campaign level for all platforms | Campaign-level data for some platforms only | Only aggregate/source-level data available |
| H18 | Funnel tracking configured | High | Full funnel stages tracked (click → lead → sale → upsell) | Partial funnel (2-3 stages) | Single event tracking only |
| H19 | Refund tracking active | Medium | Refunds tracked and deducted from revenue attribution | Refunds tracked but not deducted from attribution | No refund tracking configured |
| H20 | LTV (Lifetime Value) enabled | Medium | LTV tracking active with cohort analysis available | LTV tracking enabled but <90 days of data | LTV not configured |

---

## Scoring

Apply weighted scoring per `ads/references/scoring-system.md`:
- API & Tracking Setup: 30% weight
- Attribution Accuracy: 30% weight
- Integration Health: 20% weight
- Reporting & ROI: 20% weight

Severity multipliers: Critical (5.0x), High (3.0x), Medium (1.5x), Low (0.5x)
