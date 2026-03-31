---
name: siteintel-gis-pipeline
description: SiteIntel's GIS data pipeline and feasibility scoring engine — spatial data ingestion from 10+ Texas sources, PostGIS queries, county CAD schema mappings, feasibility scoring algorithm (0-100 with kill factors), and report generation. Use when building or extending SiteIntel's data pipeline, working with parcel data, implementing spatial queries, or modifying the feasibility scoring logic.
---

# SiteIntel GIS Pipeline

The data backbone of SiteIntel — from raw Texas GIS data to 0-100 feasibility scores in 60 seconds.

## When to Activate

- Building or modifying the data ingestion pipeline
- Writing PostGIS spatial queries
- Working with county appraisal district data
- Implementing or modifying feasibility scoring logic
- Adding new data sources to the pipeline
- Debugging spatial query performance

## Pipeline Architecture

```
Address Input
    │
    ▼
[Geocode] → lat/lng coordinates
    │
    ▼
[Parallel Data Enrichment] ─── Promise.allSettled for resilience
    │
    ├── FEMA Flood Zones (NFHL API)
    ├── EPA ECHO Environmental
    ├── TCEQ Records
    ├── TxDOT Traffic Counts
    ├── USFWS Wetlands (NWI)
    ├── USDA NRCS Soil Data
    ├── Census/ACS Demographics
    ├── County CAD Property Records
    ├── Municipal Zoning
    ├── Utility Providers
    │
    ▼
[Feasibility Scoring Engine]
    │
    ├── Domain scores (7 dimensions)
    ├── Kill factor detection
    ├── Confidence calculation
    │
    ▼
[Report Generation] → PDF via PDFShift
```

## Data Sources

| Source | Data Type | API/Method | Cache TTL |
|--------|----------|------------|-----------|
| FEMA NFHL | Flood zones | REST API | 6 months |
| EPA ECHO | Environmental violations | REST API | 3 months |
| TCEQ | TX environmental records | Web scrape/API | 3 months |
| TxDOT | Traffic counts | REST API | 1 year |
| USFWS NWI | Wetlands | WMS/REST | 6 months |
| USDA NRCS | Soil data (Web Soil Survey) | REST API | 1 year |
| Census/ACS | Demographics (83+ variables) | REST API | 1 year |
| County CADs | Property records | Varies by county | Quarterly |
| Municipal GIS | Zoning, utilities | Varies by city | 6 months |
| TX Comptroller | Mixed beverage (HII) | Data download | Monthly |

## County CAD Integration

11 Texas counties with different schemas mapped to unified model:

| County | CAD | Key Differences |
|--------|-----|----------------|
| Harris | HCAD | property_id = "Account", acreage in land_area |
| Dallas | DCAD | property_id = "acct_id", separate legal table |
| Tarrant | TAD | property_id = "prop_id", acreage = "GIS_ACRES" |
| Bexar | BCAD | property_id = "prop_id", uses "SITUS" for address |
| Travis | TCAD | property_id = "prop_id", geo_id for parcel link |
| Collin | Collin CAD | property_id = "PropertyID" |
| Denton | DCAD | Different from Dallas DCAD, "PROPERTY_ID" |
| Fort Bend | FBCAD | "ACCOUNT_NUM", acreage in "LEGAL_ACREAGE" |
| Williamson | WCAD | "prop_id", acreage in "ACRES" |
| Montgomery | MCAD | "Property_ID" |
| Galveston | GCAD | "acct", limited parcel geometry |

### Unified Property Record

```typescript
interface PropertyRecord {
  parcel_id: string;         // Normalized from county-specific ID
  county: string;
  address: string;
  city: string;
  zip: string;
  owner_name: string;
  legal_description: string;
  acreage: number;
  land_value: number;
  improvement_value: number;
  total_value: number;
  year_built: number | null;
  zoning: string | null;
  land_use_code: string;
  geometry: GeoJSON.Polygon;  // From county GIS
  last_updated: string;
}
```

## PostGIS Spatial Queries

### Point-in-Polygon (Parcel Lookup)

```sql
-- Find parcel containing a point
SELECT p.*, ST_AsGeoJSON(p.geometry) as geojson
FROM parcels p
WHERE ST_Contains(p.geometry, ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326))
LIMIT 1;
```

### Buffer Analysis (Proximity Search)

```sql
-- Find all parcels within 1 mile of a point
SELECT p.id, p.address, p.acreage,
       ST_Distance(
         p.geometry::geography,
         ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography
       ) / 1609.34 AS distance_miles
FROM parcels p
WHERE ST_DWithin(
  p.geometry::geography,
  ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography,
  1609.34  -- 1 mile in meters
)
ORDER BY distance_miles;
```

### Flood Zone Intersection

```sql
-- Check what flood zones intersect the parcel
SELECT fz.zone_type, fz.flood_risk,
       ST_Area(ST_Intersection(p.geometry, fz.geometry)::geography) /
       ST_Area(p.geometry::geography) * 100 AS overlap_pct
FROM parcels p
JOIN flood_zones fz ON ST_Intersects(p.geometry, fz.geometry)
WHERE p.id = 'parcel-uuid';
```

### Trade Area Demographics

```sql
-- Aggregate demographics within drive-time isochrone
SELECT
  SUM(bg.total_population) AS trade_area_pop,
  SUM(bg.median_income * bg.total_population) / NULLIF(SUM(bg.total_population), 0) AS weighted_median_income,
  SUM(bg.total_households) AS trade_area_households
FROM block_groups bg
WHERE ST_Intersects(
  bg.geometry,
  (SELECT geometry FROM isochrones WHERE parcel_id = 'parcel-uuid' AND drive_minutes = 10)
);
```

### Index Strategy

```sql
-- Spatial indexes (critical for sub-50ms lookups on 2.65M parcels)
CREATE INDEX idx_parcels_geometry ON parcels USING GIST (geometry);
CREATE INDEX idx_flood_zones_geometry ON flood_zones USING GIST (geometry);
CREATE INDEX idx_block_groups_geometry ON block_groups USING GIST (geometry);

-- Compound indexes for filtered spatial queries
CREATE INDEX idx_parcels_county_geom ON parcels (county) INCLUDE (geometry);
```

## Feasibility Scoring Engine

### Score Structure: 0-100 across 7 weighted domains

| Domain | Weight | What It Measures |
|--------|--------|-----------------|
| Flood Risk | 20% | FEMA zone, BFE, flood history |
| Utilities | 20% | Water, sewer, electric, gas availability |
| Soil | 15% | Shrink-swell potential, bearing capacity, drainage |
| Environmental | 15% | EPA violations, TCEQ records, contamination proximity |
| Traffic | 10% | TxDOT counts, road access, visibility |
| Zoning | 10% | Compatibility with intended use, overlay districts |
| Topography | 10% | Slope, drainage patterns, cut/fill estimates |

### Kill Factor System

Kill factors cap the maximum possible score regardless of other positives:

| Kill Factor | Max Score Cap | Detection |
|-------------|--------------|-----------|
| FLOOD_VE | 20 | Parcel in Coastal V Zone |
| EPA_SUPERFUND | 20 | Active Superfund site within 0.5 mi |
| WETLAND_100PCT | 15 | 100% wetland coverage |
| NO_UTILITIES | 50 | No water OR no sewer available |
| SHRINK_SWELL_HIGH | 60 | High shrink-swell potential across parcel |
| WATER_MORATORIUM | 25 | Active water moratorium in jurisdiction |

```python
def apply_kill_factors(domain_scores: dict, kill_factors: list[dict]) -> float:
    """Calculate final score with kill factor caps."""
    # Calculate weighted score
    raw_score = sum(
        domain_scores[domain] * weight
        for domain, weight in DOMAIN_WEIGHTS.items()
    )

    # Apply kill factor caps
    max_allowed = 100
    for kf in kill_factors:
        if kf["detected"]:
            max_allowed = min(max_allowed, kf["max_score"])

    return min(raw_score, max_allowed)
```

### Score Bands

| Band | Range | Label | Color |
|------|-------|-------|-------|
| A | 80-100 | Excellent feasibility | Emerald |
| B | 60-79 | Good feasibility with considerations | Cyan |
| C | 40-59 | Significant concerns | Amber |
| D | 0-39 | Major obstacles / not recommended | Red |

### Confidence Scoring

```python
def calculate_confidence(data_sources: dict[str, bool]) -> float:
    """Score confidence based on data source availability."""
    weights = {
        "fema": 0.20, "county_cad": 0.15, "utilities": 0.15,
        "soil": 0.10, "epa": 0.10, "traffic": 0.10,
        "zoning": 0.10, "demographics": 0.05, "wetlands": 0.05,
    }
    available = sum(w for src, w in weights.items() if data_sources.get(src, False))
    return round(available, 2)  # 0.0 to 1.0
```

## Report Tabs (10 sections)

1. Property Info
2. Feasibility Score (0-100 with domain breakdown)
3. Interactive Map
4. Zoning Analysis
5. Flood Risk
6. Utilities
7. Environmental
8. Traffic
9. Market Demographics
10. Construction Costs (via ConstructIntel integration)

## Parallel Enrichment Pattern

```typescript
async function enrichParcel(parcelId: string, coordinates: [number, number]) {
  const [lng, lat] = coordinates;

  // Fire all data sources in parallel — don't let one failure block others
  const results = await Promise.allSettled([
    fetchFEMAFloodZone(lat, lng),
    fetchEPAEcho(lat, lng),
    fetchTCEQRecords(lat, lng),
    fetchTxDOTTraffic(lat, lng),
    fetchUSFWSWetlands(lat, lng),
    fetchUSDANRCSSoil(lat, lng),
    fetchCensusACS(lat, lng),
    fetchCountyCAD(parcelId),
    fetchMunicipalZoning(lat, lng),
    fetchUtilityProviders(lat, lng),
  ]);

  // Process results — fulfilled or rejected
  const enrichment: Record<string, any> = {};
  const sources = [
    "fema", "epa", "tceq", "txdot", "usfws",
    "usda", "census", "cad", "zoning", "utilities"
  ];

  results.forEach((result, i) => {
    if (result.status === "fulfilled") {
      enrichment[sources[i]] = { data: result.value, available: true };
    } else {
      enrichment[sources[i]] = { data: null, available: false, error: result.reason };
      console.warn(`${sources[i]} fetch failed:`, result.reason);
    }
  });

  return enrichment;
}
```

## Performance Targets

| Metric | Target |
|--------|--------|
| Geocode → enrichment complete | <10 seconds |
| PostGIS spatial query (single parcel) | <50ms |
| Full feasibility score calculation | <2 seconds |
| End-to-end (address → PDF report) | <60 seconds |
| Data source cache hit rate | >80% |

## Debugging GIS Issues

```
Problem: Parcel not found
→ Check geocoding accuracy (is the point inside the parcel polygon?)
→ Verify county coverage (is this county in the 11 supported?)
→ Check if CAD data is current (quarterly refresh)

Problem: Wrong flood zone
→ Verify FEMA API is returning current NFHL data
→ Check spatial intersection accuracy (SRID matching)
→ Compare with FEMA Flood Map Service Center manually

Problem: Slow spatial queries
→ Check GIST indexes exist on geometry columns
→ Run EXPLAIN ANALYZE on the query
→ Check if table needs VACUUM ANALYZE

Problem: Missing demographics
→ Verify Census API key is valid
→ Check if block group geometry covers the parcel
→ Verify population-weighted aggregation logic
```
