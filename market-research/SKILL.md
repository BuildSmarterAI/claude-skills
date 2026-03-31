---
name: market-research
description: Conduct market research, competitive analysis, investor due diligence, and industry intelligence for CRE, PropTech, ConTech, and construction markets. Use when researching competitors (TestFit, Feasibly, Procore), sizing markets, preparing investor dossiers, analyzing Texas CRE trends, or pressure-testing product positioning for SiteIntel, ConstructIntel.ai, or BuildSmarter AI.
origin: ECC (customized for BuildSmarter stack)
---

# Market Research

Produce research that supports decisions, not research theater.

## When to Activate

- Researching PropTech/ConTech competitors or adjacent products
- Building TAM/SAM/SOM estimates for CRE intelligence markets
- Preparing investor dossiers before outreach
- Analyzing Texas CRE market trends
- Evaluating potential integrations or partnerships
- Pressure-testing product positioning

## Research Standards

1. Every important claim needs a source.
2. Prefer recent data and call out stale data.
3. Include contrarian evidence and downside cases.
4. Translate findings into a decision, not just a summary.
5. Separate fact, inference, and recommendation clearly.

## Research Modes

### Competitive Analysis (PropTech/ConTech)

For each competitor, collect:

| Category | What to Find |
|----------|-------------|
| Product reality | What it actually does vs. marketing claims |
| Pricing | Public tiers, estimated enterprise pricing |
| Funding | Total raised, last round, investors |
| Traction | Users, customers, revenue signals (job posts, reviews, press) |
| Target market | Who they sell to, who they ignore |
| Strengths | What they do well |
| Weaknesses | Gaps, complaints, missing features |
| Differentiation | How BuildSmarter is different |

**Key competitors to track:**

| Product | Category | Overlap with BuildSmarter |
|---------|----------|--------------------------|
| TestFit | Site design/feasibility | SiteIntel (design-focused, not data-focused) |
| Feasibly | Entitlements/approvals | SiteIntel (entitlements only, not full feasibility) |
| Procore | Construction PM | BuildSmarter AI / Maxx Builders (PM, not intelligence) |
| PlanSwift | Manual takeoff | ConstructIntel (manual vs. AI-powered) |
| RSMeans | Cost data | ConstructIntel (static data vs. project-derived) |
| REONOMY | CRE data | SiteIntel (national but shallow, not Texas-deep) |
| CoStar | CRE analytics | SiteIntel (enterprise pricing, not feasibility-focused) |
| Briq | Construction finance | ConstructIntel (finance, not cost intelligence) |

### Market Sizing (CRE / PropTech)

Use both approaches:

**Top-down:**
- Total US CRE market value
- PropTech market size (Deloitte, JLL, CBRE reports)
- ConTech market size
- Texas share of US CRE activity

**Bottom-up:**
- Number of target buyers in Texas (developers, GCs, lenders, brokers)
- Estimated willingness to pay per segment
- Realistic penetration rate by year
- Revenue per customer × addressable customers = SAM

**Always include:**
- Explicit assumptions for every leap
- Texas-specific data where available
- Growth rates and trends
- Sources and dates

### Investor / Fund Diligence

Before outreach to any investor, collect:

- Fund size, stage focus, typical check size
- PropTech/ConTech/CRE portfolio companies
- Recent investments and announcements
- Public thesis (blog posts, podcast appearances, conference talks)
- Partner who leads relevant deals
- Geographic focus (do they invest in Texas?)
- Reasons the fund IS or IS NOT a fit
- Red flags or mismatches

### Texas CRE Market Intelligence

Key data sources:
- Texas Comptroller (mixed beverage receipts for hospitality analysis)
- TDLR (permit filings for construction activity)
- County appraisal districts (HCAD, DCAD, TCAD, BCAD + 7 more)
- TxDOT (traffic counts for site access analysis)
- Census/ACS (demographics for trade area analysis)
- FEMA (flood zone data)
- CoStar/LoopNet (comparable sales and lease rates)

Track:
- Permit volume trends by metro and building type
- Construction cost trends (materials, labor)
- Cap rate trends by metro and property type
- Population growth and migration patterns
- Infrastructure and transportation developments

### Technology / Vendor Research

For evaluating tools, APIs, or platforms to integrate:

| Category | What to Evaluate |
|----------|-----------------|
| Functionality | Does it solve the problem? |
| Integration | API quality, Supabase/Cloud Run compatibility |
| Pricing | Per-call, per-seat, or flat rate? |
| Lock-in risk | Data portability, contract terms |
| Reliability | Uptime, support quality, community |
| Security | SOC 2, data handling, compliance |

## Output Format

Default structure:
1. **Executive summary** — key finding and recommendation in 2-3 sentences
2. **Key findings** — organized by theme, sourced
3. **Implications for BuildSmarter** — what this means for product/strategy
4. **Risks and caveats** — what could be wrong, what's missing
5. **Recommendation** — specific action to take
6. **Sources** — with dates

## CRE-Specific Formatting

- Currency: $1,234,567
- Cap rates: X.XX%
- Square footage: always include SF equivalent with acreage
- Growth rates: 1 decimal (12.5%)
- Per-unit metrics: $/SF, $/unit
- Market data: always note the date and source

## Quality Gate

Before delivering:

- [ ] All numbers sourced or labeled as estimates
- [ ] Old data flagged with dates
- [ ] Recommendation follows from evidence
- [ ] Risks and counterarguments included
- [ ] Texas-specific data used where available
- [ ] Competitive analysis based on product reality, not marketing
- [ ] Output makes a decision easier, not just more information
