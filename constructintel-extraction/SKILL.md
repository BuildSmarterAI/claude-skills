---
name: constructintel-extraction
description: ConstructIntel.ai's AI-powered document extraction pipeline — PDF processing, CSI MasterFormat classification, bid line item parsing, quantity takeoff extraction, multi-agent validation, and confidence scoring. Use when building, debugging, or extending the extraction pipeline, working with bid documents, or implementing new extraction features.
---

# ConstructIntel Extraction Pipeline

The core AI pipeline that powers ConstructIntel.ai — from raw PDF to structured, validated construction cost data.

## When to Activate

- Building or modifying the extraction pipeline
- Adding new document types to extraction
- Debugging extraction accuracy issues
- Implementing CSI classification logic
- Working on confidence scoring or validation
- Optimizing extraction cost (model routing)

## Pipeline Architecture

```
PDF Upload (Supabase Storage)
    │
    ▼
[Edge Function: Job Dispatcher]
    │ Creates job record, fires to Cloud Run
    ▼
[Cloud Run: PDF Processor]
    │
    ├── Stage 1: Text Extraction (pdfplumber / OCR)
    ├── Stage 2: Document Classification
    ├── Stage 3: Section Segmentation
    ├── Stage 4: AI Line Item Extraction (Claude/Gemini)
    ├── Stage 5: CSI Classification
    ├── Stage 6: Validation & Confidence Scoring
    │
    ▼
[Supabase: Store Results]
    │ Update job status via Realtime
    ▼
[Frontend: Display Results]
```

## Pipeline States

Track via `processing_jobs` table, broadcast via Supabase Realtime:

```
queued (5%) → extracting_text (15%) → classifying (30%) →
extracting_items (50%) → validating (75%) → scoring (85%) →
storing (95%) → completed (100%)
```

Always update status at each stage transition so the frontend can show progress.

## Stage 1: Text Extraction

```python
import pdfplumber
from pathlib import Path

def extract_text_by_page(pdf_path: str) -> list[dict]:
    """Extract text from each page with metadata."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            pages.append({
                "page_number": i + 1,
                "text": text,
                "text_length": len(text),
                "has_tables": len(tables) > 0,
                "tables": tables,
                "width": page.width,
                "height": page.height,
            })
    return pages

# If text extraction fails (scanned PDF), fall back to OCR
def needs_ocr(pages: list[dict]) -> bool:
    """Check if PDF is scanned and needs OCR."""
    total_text = sum(p["text_length"] for p in pages)
    return total_text < 100  # Less than 100 chars across all pages
```

## Stage 2: Document Classification

Classify the document type to route to the correct extraction logic:

```python
DOCUMENT_TYPES = {
    "bid_tabulation": "Structured bid comparison with multiple contractor prices",
    "cost_estimate": "Detailed cost breakdown by CSI division",
    "schedule_of_values": "AIA-style schedule of values for payment applications",
    "subcontractor_bid": "Individual sub bid with scope and pricing",
    "quantity_takeoff": "Quantity list from plan takeoff",
    "general_bid_form": "Generic bid form with total price",
}

async def classify_document(first_pages_text: str, client) -> str:
    """Classify document type using cheapest model."""
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=50,
        system="Classify this construction document. Return ONLY the type key.",
        messages=[{
            "role": "user",
            "content": f"Document types: {list(DOCUMENT_TYPES.keys())}\n\nText:\n{first_pages_text[:3000]}",
        }],
    )
    return response.content[0].text.strip()
```

## Stage 3: AI Line Item Extraction

```python
EXTRACTION_SYSTEM_PROMPT = """You are a construction cost extraction specialist.
Extract line items from this bid document into structured JSON.

For each line item, extract:
- description: what the work item is
- quantity: numeric amount
- unit: unit of measure (CY, SF, LF, EA, LS, TON, etc.)
- unit_cost: price per unit (if available)
- total_cost: extended total (if available)
- csi_division: 2-digit CSI MasterFormat division code (your best guess)

Return JSON array of objects. If a field is not available, use null.
Be precise with numbers — do not round or estimate."""

async def extract_line_items(
    document_text: str,
    document_type: str,
    client,
    model: str = "claude-sonnet-4-6",
) -> list[dict]:
    """Extract structured line items from document text."""
    response = await client.messages.create(
        model=model,
        max_tokens=4096,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Document type: {document_type}\n\n{document_text}",
        }],
    )

    # Parse JSON from response
    text = response.content[0].text
    # Handle markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return json.loads(text)
```

## Stage 4: CSI MasterFormat Classification

```python
CSI_DIVISIONS = {
    "01": "General Requirements",
    "02": "Existing Conditions",
    "03": "Concrete",
    "04": "Masonry",
    "05": "Metals",
    "06": "Wood, Plastics, and Composites",
    "07": "Thermal and Moisture Protection",
    "08": "Openings",
    "09": "Finishes",
    "10": "Specialties",
    "11": "Equipment",
    "12": "Furnishings",
    "13": "Special Construction",
    "14": "Conveying Equipment",
    "21": "Fire Suppression",
    "22": "Plumbing",
    "23": "HVAC",
    "26": "Electrical",
    "27": "Communications",
    "28": "Electronic Safety and Security",
    "31": "Earthwork",
    "32": "Exterior Improvements",
    "33": "Utilities",
}

# Classification rules (regex first, LLM fallback)
CSI_KEYWORDS = {
    "03": ["concrete", "rebar", "formwork", "slab", "footing", "foundation", "psi"],
    "05": ["steel", "structural steel", "metal deck", "joist", "beam", "column"],
    "07": ["roofing", "insulation", "waterproofing", "membrane", "flashing", "sealant"],
    "09": ["drywall", "gypsum", "paint", "flooring", "tile", "carpet", "ceiling"],
    "23": ["hvac", "ductwork", "air handler", "chiller", "boiler", "mechanical"],
    "26": ["electrical", "conduit", "panel", "switchgear", "lighting", "wire"],
    "31": ["excavation", "grading", "earthwork", "fill", "backfill", "soil"],
}

def classify_csi_by_keywords(description: str) -> str | None:
    """Fast keyword-based CSI classification."""
    desc_lower = description.lower()
    for division, keywords in CSI_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return division
    return None  # Falls to LLM classification
```

## Stage 5: Validation & Confidence Scoring

```python
@dataclass(frozen=True)
class ValidationResult:
    item_index: int
    confidence: float
    flags: tuple[str, ...]
    is_valid: bool

def validate_line_item(item: dict, index: int) -> ValidationResult:
    """Validate extracted line item and assign confidence score."""
    flags = []
    score = 1.0

    # Check required fields
    if not item.get("description"):
        flags.append("missing_description")
        score -= 0.5

    # Check quantity
    qty = item.get("quantity")
    if qty is None:
        flags.append("missing_quantity")
        score -= 0.3
    elif qty <= 0:
        flags.append("invalid_quantity")
        score -= 0.4

    # Check unit
    unit = item.get("unit", "").upper()
    valid_units = {"CY", "SF", "LF", "EA", "LS", "TON", "GAL", "HR", "SY", "MBF"}
    if unit and unit not in valid_units:
        flags.append("unusual_unit")
        score -= 0.1

    # Check CSI division
    csi = item.get("csi_division")
    if csi and csi not in CSI_DIVISIONS:
        flags.append("invalid_csi_division")
        score -= 0.2

    # Check for suspiciously high values
    total = item.get("total_cost") or 0
    if total > 10_000_000:
        flags.append("suspiciously_high_total")
        score -= 0.2

    # Short description might be truncated
    if item.get("description") and len(item["description"]) < 5:
        flags.append("short_description")
        score -= 0.2

    confidence = max(0.0, min(1.0, score))

    return ValidationResult(
        item_index=index,
        confidence=confidence,
        flags=tuple(flags),
        is_valid=confidence >= 0.7,
    )
```

## Multi-Agent Validation Pattern

For high-value bids, run a second LLM pass to validate:

```python
async def multi_agent_validate(
    original_items: list[dict],
    source_text: str,
    low_confidence_indices: set[int],
    client,
) -> list[dict]:
    """Second LLM pass validates low-confidence items against source."""
    validated = list(original_items)

    for idx in low_confidence_indices:
        item = original_items[idx]
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",  # Cheap model for validation
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"Verify this extraction against the source text.\n\n"
                    f"Extracted: {json.dumps(item)}\n\n"
                    f"Source: {source_text[:2000]}\n\n"
                    f"Return corrected JSON or exact same JSON if correct."
                ),
            }],
        )
        corrected = json.loads(response.content[0].text)
        validated[idx] = corrected

    return validated
```

## Model Routing for Extraction

| Task | Model | Why |
|------|-------|-----|
| Document classification | Haiku | Simple classification, high volume |
| Short document extraction (<5 pages) | Haiku | Low complexity |
| Complex bid extraction (5+ pages) | Sonnet | Accuracy critical |
| High-value bid (>$50K) | Sonnet | Error cost is high |
| CSI classification (keyword miss) | Haiku | Simple mapping task |
| Validation pass | Haiku | Comparing structured data |

## Job Record Schema

```sql
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    org_id UUID REFERENCES organizations(id),
    type TEXT NOT NULL,  -- 'pdf_extraction', 'quantity_takeoff', 'bid_analysis'
    status TEXT NOT NULL DEFAULT 'queued',
    progress INTEGER DEFAULT 0,  -- 0-100
    input_data JSONB,  -- { pdf_url, extraction_type, options }
    result_data JSONB,  -- { line_items, summary, confidence }
    error_message TEXT,
    error_details JSONB,
    model_used TEXT,
    tokens_used INTEGER,
    cost_usd NUMERIC(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "org_isolation" ON processing_jobs
    FOR ALL USING (org_id = (SELECT org_id FROM profiles WHERE id = auth.uid()));
```

## Quality Metrics

Track per extraction job:

| Metric | Target |
|--------|--------|
| Items extracted | Matches document (±5%) |
| CSI classification accuracy | >95% |
| Confidence score (average) | >0.85 |
| Low-confidence items (<0.7) | <10% of total |
| Processing time | <30s for <10 pages |
| Cost per extraction | <$0.50 for Haiku, <$2 for Sonnet |

## Debugging Extraction Issues

```
Problem: Missing line items
→ Check if text extraction captured all pages
→ Check if document type classification was correct
→ Try with Sonnet instead of Haiku

Problem: Wrong quantities
→ Check source text for OCR errors
→ Add explicit "extract exact numbers" to prompt
→ Run validation pass

Problem: Wrong CSI divisions
→ Check keyword matching first
→ Add more keywords for the failing division
→ Add few-shot examples to LLM classification prompt

Problem: Timeout on large documents
→ Chunk document into sections
→ Process pages in parallel
→ Use streaming for LLM calls
```
