---
name: construction-industry
description: >
  Construction industry domain knowledge for software development. Use this skill when
  working with CSI divisions, MasterFormat codes, construction estimating workflows,
  bid management, subcontractor relationships, general contractor operations, preconstruction
  processes, change orders, scope of work, or any construction-specific terminology.
  Also trigger when parsing construction documents, understanding bid formats, working
  with permit data, or building features for construction professionals. Even for
  general questions about how GCs estimate, bid, or manage subcontractors.
---

# Construction Industry Domain Knowledge

## CSI Division Structure

### Legacy 16-Division System (Broadscope)
Used by many GCs internally and in legacy systems. Simpler, maps to how estimators
actually think about trades.

```
01 — General Requirements (insurance, bonds, supervision, temp facilities)
02 — Site Construction (excavation, grading, paving, landscaping, utilities)
03 — Concrete (foundations, slabs, structures, formwork, rebar)
04 — Masonry (brick, block, stone, mortar)
05 — Metals (structural steel, misc metals, railings, stairs)
06 — Wood & Plastics (framing, rough carpentry, finish carpentry, casework)
07 — Thermal & Moisture Protection (roofing, waterproofing, insulation, caulking)
08 — Doors & Windows (hollow metal, wood doors, storefronts, glazing, hardware)
09 — Finishes (drywall, framing, paint, flooring, ceilings, tile)
10 — Specialties (signage, toilet accessories, fire extinguishers, lockers)
11 — Equipment (kitchen, laundry, loading dock, athletic)
12 — Furnishings (window treatments, furniture, artwork)
13 — Special Construction (clean rooms, pools, pre-engineered buildings)
14 — Conveying Equipment (elevators, escalators, dumbwaiters)
15 — Mechanical (HVAC, plumbing, fire protection — the "big MEP" division)
16 — Electrical (power, lighting, low voltage, fire alarm, data/comm)
```

### MasterFormat 50-Division System (CSI 2020)
Industry standard. More granular. Required for Procore cost codes. Division 15 splits
into 21 (Fire Protection), 22 (Plumbing), 23 (HVAC). Division 16 becomes 26 (Electrical).

## Estimating Workflow

```
1. PROJECT IDENTIFIED
   └→ GC receives invitation to bid (ITB) or plans/specs from owner/architect

2. PLAN REVIEW
   └→ Estimator reviews drawings and specifications
   └→ Identifies scope by CSI division
   └→ Determines which trades need subcontractor bids

3. BID SOLICITATION
   └→ Send bid invitations to subcontractors per division
   └→ Typically want 3+ bids per division for competition
   └→ Include drawings, specs, addenda, bid form

4. BID RECEIPT
   └→ Subcontractors submit bids (PDF, email, fax, online)
   └→ Bids arrive in various formats: lump sum, itemized, partial
   └→ Must track: base amount, alternates, inclusions, exclusions

5. BID LEVELING / COMPARISON
   └→ Normalize bids to compare apples-to-apples
   └→ Identify scope gaps (what's excluded that should be included)
   └→ Add allowances for missing scope
   └→ Calculate "adjusted total" = base + missing scope allowances
   └→ THIS IS WHERE PRECONINTEL ADDS MOST VALUE

6. SUBCONTRACTOR SELECTION
   └→ Low price isn't always the winner
   └→ Consider: scope completeness, CO history, reliability, relationships
   └→ Estimator recommends, PM/principal approves

7. ESTIMATE ASSEMBLY
   └→ Combine all selected subs into total estimate
   └→ Add GC markups: overhead, profit, contingency, bonds
   └→ Submit to owner/architect

8. AWARD → CONTRACT → CONSTRUCTION
```

## Key Construction Terms

| Term | Meaning |
|------|---------|
| GC | General Contractor — manages the overall project |
| Sub | Subcontractor — performs specific trade work |
| Precon | Preconstruction — estimating and planning phase |
| ITB | Invitation to Bid |
| Scope | The specific work included/excluded in a bid |
| Leveling | Normalizing bids for fair comparison |
| CO | Change Order — additional cost after contract |
| Alternate | Optional pricing for scope changes |
| Allowance | Budget placeholder for undefined scope |
| NTE | Not To Exceed — cost ceiling |
| GMP | Guaranteed Maximum Price |
| T&M | Time and Materials |
| Lump Sum | Single price for all work (no breakdown) |
| Unit Price | Cost per unit ($/SF, $/LF, $/CY, $/EA) |
| Addendum | Changes to plans/specs before bid due date |
| RFI | Request for Information |
| Submittal | Product data/samples for approval |
| Punchlist | Final deficiency list before project closeout |

## Common Unit Price Abbreviations
- SF — Square Foot
- LF — Linear Foot
- CY — Cubic Yard
- SY — Square Yard
- EA — Each
- LS — Lump Sum
- TON — Ton
- GAL — Gallon
- MBF — Thousand Board Feet

## Bid Format Types

**Lump Sum**: Single total price, no breakdown. Hard to compare.
```
ABC Drywall: $145,000 for all Division 09 work per plans and specs.
```

**Partially Itemized**: Some breakdown but not complete.
```
ABC Drywall:
  Metal Framing: $45,000
  Drywall: $62,000
  Acoustical Ceilings: $18,000
  Other: $20,000
  TOTAL: $145,000
```

**Fully Itemized**: Complete unit-price breakdown. Ideal for comparison.
```
ABC Drywall:
  Metal Framing: 15,000 SF × $3.00/SF = $45,000
  Type X Drywall: 12,400 SF × $2.85/SF = $35,340
  Level 4 Finish: 12,400 SF × $1.50/SF = $18,600
  ACT Ceilings: 6,000 SF × $3.00/SF = $18,000
  Painting: 12,400 SF × $0.55/SF = $6,820
  TOTAL: $123,760
```

## Scope Gap Risk by Division

High-risk divisions for scope gaps (common exclusions that create COs):
- **Div 02 Site**: Unforeseen conditions, rock, contaminated soil
- **Div 03 Concrete**: Pumping, winter protection, testing
- **Div 07 Roofing**: Tear-off, deck repair, insulation type
- **Div 09 Finishes**: Paint touch-up scope, ceiling grid vs tiles
- **Div 15 Mechanical**: Controls, test & balance, permits, startup
- **Div 16 Electrical**: Temporary power, low voltage infrastructure

## Texas-Specific Context
- No state income tax affects contractor pricing
- TDI (Texas Dept of Insurance) licenses for MEP
- TDLR (Texas Dept of Licensing & Regulation) for elevators
- Local jurisdiction permits (Houston, Dallas, Austin, San Antonio)
- Hurricane/wind code requirements along Gulf Coast
- Expansive clay soil conditions in Houston area
