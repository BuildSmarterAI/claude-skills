#!/usr/bin/env python3
"""
Fetch HYROS attribution data via API for cross-platform audit analysis.

Collects leads, sales, events, and revenue attribution data. Outputs structured
JSON with pre-computed derived metrics for the 20-check HYROS audit and
cross-platform attribution comparison.

Usage:
    python fetch_hyros_data.py --api-key API_abda3d6c...
    python fetch_hyros_data.py --env-file /path/to/.env
    python fetch_hyros_data.py --env-file .env --dry-run
    python fetch_hyros_data.py --env-file .env --output output/hyros_data.json --verbose
    python fetch_hyros_data.py --env-file .env --days 30 --json
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://api.hyros.com/v1"
DEFAULT_DAYS = 30
RATE_LIMIT_PAUSE = 2  # seconds base for exponential backoff
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# API Request Helper
# ---------------------------------------------------------------------------

def api_request(endpoint, api_key, payload=None, method="POST", retries=MAX_RETRIES):
    """Make a HYROS API request with Bearer auth and retry logic for rate limits.

    Returns the parsed JSON on success, or a dict with 'error' key on failure.
    """
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for attempt in range(retries):
        try:
            if method == "POST":
                response = requests.post(
                    url, headers=headers, json=payload or {},
                    timeout=REQUEST_TIMEOUT
                )
            else:
                response = requests.get(
                    url, headers=headers, params=payload or {},
                    timeout=REQUEST_TIMEOUT
                )
        except requests.exceptions.RequestException as exc:
            return {"error": f"Request failed: {exc}", "code": -1}

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return {"error": "Invalid JSON response", "code": -2}

        if response.status_code == 429:  # Rate limited
            wait = RATE_LIMIT_PAUSE * (2 ** attempt)
            print(f"  Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        elif response.status_code == 401:
            return {"error": "Invalid API key. Check your HYROS API key in .env", "code": 401}
        elif response.status_code == 400:
            try:
                body = response.json()
                msg = body.get("message", body.get("error", "Bad request"))
            except ValueError:
                msg = "Bad request (invalid JSON payload)"
            return {"error": f"Bad request: {msg}", "code": 400}
        elif response.status_code == 500:
            return {"error": "HYROS server error. Try again later.", "code": 500}
        else:
            try:
                body = response.json()
                msg = body.get("message", body.get("error", f"HTTP {response.status_code}"))
            except ValueError:
                msg = f"HTTP {response.status_code}"
            return {"error": msg, "code": response.status_code}

    return {"error": "Rate limit exceeded after retries", "code": 429}


# ---------------------------------------------------------------------------
# API Key Management
# ---------------------------------------------------------------------------

def load_api_key(args):
    """Load HYROS API key from --api-key arg, --env-file, or HYROS env var."""
    # Direct argument
    if args.api_key:
        return args.api_key

    # Load from .env file
    if args.env_file:
        if load_dotenv:
            load_dotenv(args.env_file)
        else:
            # Manual .env parsing fallback
            try:
                with open(args.env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, val = line.partition("=")
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            os.environ[key] = val
            except FileNotFoundError:
                print(f"Error: env file not found: {args.env_file}", file=sys.stderr)
                sys.exit(1)

    # Read from environment
    api_key = os.environ.get("HYROS", "")
    if not api_key:
        print("Error: HYROS API key not found. Provide via --api-key, --env-file, or HYROS env var.", file=sys.stderr)
        sys.exit(1)

    return api_key


def validate_api_key(api_key):
    """Validate the HYROS API key format and connectivity."""
    # HYROS keys typically start with API_ prefix
    if not api_key:
        return False, "API key is empty"

    # Test connectivity with a minimal request
    result = api_request("leads", api_key, payload={"limit": 1})
    if "error" in result:
        return False, result["error"]

    return True, "API key valid"


# ---------------------------------------------------------------------------
# Data Fetchers
# ---------------------------------------------------------------------------

def fetch_leads(api_key, days, verbose=False):
    """Fetch lead data from HYROS."""
    if verbose:
        print("  Fetching leads...", file=sys.stderr)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    payload = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    }

    result = api_request("leads", api_key, payload=payload)
    if "error" in result:
        if verbose:
            print(f"  Warning: leads fetch failed: {result['error']}", file=sys.stderr)
        return {"data": [], "error": result["error"]}

    data = result if isinstance(result, list) else result.get("data", result.get("leads", []))
    if not isinstance(data, list):
        data = [data] if data else []

    if verbose:
        print(f"  Fetched {len(data)} leads", file=sys.stderr)
    return {"data": data}


def fetch_sales(api_key, days, verbose=False):
    """Fetch sales/revenue data from HYROS."""
    if verbose:
        print("  Fetching sales...", file=sys.stderr)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    payload = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    }

    result = api_request("sales", api_key, payload=payload)
    if "error" in result:
        if verbose:
            print(f"  Warning: sales fetch failed: {result['error']}", file=sys.stderr)
        return {"data": [], "error": result["error"]}

    data = result if isinstance(result, list) else result.get("data", result.get("sales", []))
    if not isinstance(data, list):
        data = [data] if data else []

    if verbose:
        print(f"  Fetched {len(data)} sales", file=sys.stderr)
    return {"data": data}


def fetch_events(api_key, days, verbose=False):
    """Fetch custom events from HYROS."""
    if verbose:
        print("  Fetching events...", file=sys.stderr)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    payload = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    }

    result = api_request("events", api_key, payload=payload)
    if "error" in result:
        if verbose:
            print(f"  Warning: events fetch failed: {result['error']}", file=sys.stderr)
        return {"data": [], "error": result["error"]}

    data = result if isinstance(result, list) else result.get("data", result.get("events", []))
    if not isinstance(data, list):
        data = [data] if data else []

    if verbose:
        print(f"  Fetched {len(data)} events", file=sys.stderr)
    return {"data": data}


# ---------------------------------------------------------------------------
# Derived Metrics
# ---------------------------------------------------------------------------

def _safe_float(val, default=0.0):
    """Safely convert a value to float."""
    try:
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def compute_derived(leads_data, sales_data, events_data):
    """Pre-compute all audit-relevant derived metrics from raw HYROS data."""
    derived = {}
    leads = leads_data.get("data", [])
    sales = sales_data.get("data", [])
    events = events_data.get("data", [])

    # --- Lead metrics ---
    derived["total_leads"] = len(leads)
    leads_by_source = defaultdict(int)
    for lead in leads:
        source = lead.get("source", lead.get("ad_source", "unknown"))
        if isinstance(source, list):
            for s in source:
                leads_by_source[str(s)] += 1
        else:
            leads_by_source[str(source)] += 1
    derived["leads_by_source"] = dict(leads_by_source)

    # --- Sales metrics ---
    derived["total_sales"] = len(sales)
    total_revenue = 0.0
    revenue_by_source = defaultdict(float)
    sales_by_source = defaultdict(int)
    sales_by_product = defaultdict(lambda: {"count": 0, "revenue": 0.0})

    for sale in sales:
        amount = _safe_float(sale.get("amount", sale.get("revenue", 0)))
        total_revenue += amount
        source = sale.get("source", sale.get("ad_source", "unknown"))
        if isinstance(source, list):
            for s in source:
                revenue_by_source[str(s)] += amount
                sales_by_source[str(s)] += 1
        else:
            revenue_by_source[str(source)] += amount
            sales_by_source[str(source)] += 1

        product = sale.get("product", sale.get("product_name", "unknown"))
        sales_by_product[str(product)]["count"] += 1
        sales_by_product[str(product)]["revenue"] += amount

    derived["total_revenue"] = round(total_revenue, 2)
    derived["revenue_by_source"] = {k: round(v, 2) for k, v in revenue_by_source.items()}
    derived["sales_by_source"] = dict(sales_by_source)
    derived["sales_by_product"] = {k: {"count": v["count"], "revenue": round(v["revenue"], 2)}
                                    for k, v in sales_by_product.items()}

    # --- Event metrics ---
    derived["total_events"] = len(events)
    events_by_name = defaultdict(int)
    for event in events:
        name = event.get("event", event.get("event_name", "unknown"))
        events_by_name[str(name)] += 1
    derived["events_by_name"] = dict(events_by_name)

    # --- Attribution by platform ---
    platform_map = {
        "google": ["google", "gclid", "google_ads", "adwords"],
        "meta": ["facebook", "fb", "instagram", "ig", "meta", "fbclid"],
        "linkedin": ["linkedin", "li"],
        "tiktok": ["tiktok", "tt", "ttclid"],
        "microsoft": ["bing", "microsoft", "msclkid"],
        "youtube": ["youtube", "yt"],
        "organic": ["organic", "direct", "none", "unknown"],
    }

    platform_attribution = {}
    for platform, keywords in platform_map.items():
        platform_leads = 0
        platform_sales = 0
        platform_revenue = 0.0
        for kw in keywords:
            platform_leads += leads_by_source.get(kw, 0)
            platform_sales += sales_by_source.get(kw, 0)
            platform_revenue += revenue_by_source.get(kw, 0)
        platform_attribution[platform] = {
            "leads": platform_leads,
            "sales": platform_sales,
            "revenue": round(platform_revenue, 2),
        }
    derived["platform_attribution"] = platform_attribution

    # --- True ROAS per source ---
    # Note: ROAS requires ad spend data which HYROS doesn't directly provide.
    # This will be compared against platform-reported spend externally.
    derived["revenue_attribution_available"] = total_revenue > 0
    derived["lead_to_sale_rate"] = (
        round(len(sales) / len(leads) * 100, 2) if leads else 0.0
    )

    # --- Refund tracking ---
    refunds = [s for s in sales if _safe_float(s.get("amount", s.get("revenue", 0))) < 0]
    derived["refund_count"] = len(refunds)
    derived["refund_amount"] = round(sum(_safe_float(s.get("amount", s.get("revenue", 0))) for s in refunds), 2)

    # --- Data quality signals ---
    derived["has_leads"] = len(leads) > 0
    derived["has_sales"] = len(sales) > 0
    derived["has_events"] = len(events) > 0
    derived["has_source_tagging"] = any(
        lead.get("source") or lead.get("ad_source") for lead in leads
    )
    derived["has_revenue_data"] = total_revenue > 0

    # --- Errors ---
    errors = []
    if leads_data.get("error"):
        errors.append(f"leads: {leads_data['error']}")
    if sales_data.get("error"):
        errors.append(f"sales: {sales_data['error']}")
    if events_data.get("error"):
        errors.append(f"events: {events_data['error']}")
    derived["errors"] = errors

    return derived


# ---------------------------------------------------------------------------
# Build Payload
# ---------------------------------------------------------------------------

def build_audit_payload(leads_data, sales_data, events_data, derived, days, api_key_prefix):
    """Build the structured JSON output for audit consumption."""
    return {
        "metadata": {
            "source": "hyros",
            "collection_timestamp": datetime.now().isoformat(),
            "date_range": {
                "days": days,
                "start": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
                "end": datetime.now().strftime("%Y-%m-%d"),
            },
            "api_key_prefix": api_key_prefix,
            "errors": derived.get("errors", []),
        },
        "leads": {
            "total": derived["total_leads"],
            "by_source": derived["leads_by_source"],
            "raw_sample": leads_data.get("data", [])[:10],  # First 10 for inspection
        },
        "sales": {
            "total": derived["total_sales"],
            "total_revenue": derived["total_revenue"],
            "by_source": derived["sales_by_source"],
            "revenue_by_source": derived["revenue_by_source"],
            "by_product": derived["sales_by_product"],
            "raw_sample": sales_data.get("data", [])[:10],
        },
        "events": {
            "total": derived["total_events"],
            "by_name": derived["events_by_name"],
            "raw_sample": events_data.get("data", [])[:10],
        },
        "attribution": {
            "platform_attribution": derived["platform_attribution"],
            "lead_to_sale_rate": derived["lead_to_sale_rate"],
            "refund_count": derived["refund_count"],
            "refund_amount": derived["refund_amount"],
        },
        "derived": derived,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fetch HYROS attribution data for ad audit analysis."
    )
    parser.add_argument("--api-key", help="HYROS API key (or use HYROS env var)")
    parser.add_argument("--env-file", help="Path to .env file containing HYROS key")
    parser.add_argument("--output", help="Write JSON output to file")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS,
                        help=f"Days of data to fetch (default: {DEFAULT_DAYS})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate API key and exit without fetching data")
    parser.add_argument("--verbose", action="store_true",
                        help="Print progress to stderr")
    parser.add_argument("--json", action="store_true",
                        help="Print JSON output to stdout")

    args = parser.parse_args()

    # Load API key
    api_key = load_api_key(args)
    api_key_prefix = api_key[:10] + "..." if len(api_key) > 10 else api_key

    if args.verbose:
        print(f"HYROS API key: {api_key_prefix}", file=sys.stderr)
        print(f"Date range: {args.days} days", file=sys.stderr)

    # Dry run: validate and exit
    if args.dry_run:
        print(f"API key loaded: {api_key_prefix}")
        valid, msg = validate_api_key(api_key)
        if valid:
            print(f"Validation: {msg}")
        else:
            print(f"Validation failed: {msg}", file=sys.stderr)
            sys.exit(1)
        return

    # Fetch data
    if args.verbose:
        print("Fetching HYROS attribution data...", file=sys.stderr)

    leads_data = fetch_leads(api_key, args.days, args.verbose)
    sales_data = fetch_sales(api_key, args.days, args.verbose)
    events_data = fetch_events(api_key, args.days, args.verbose)

    # Compute derived metrics
    if args.verbose:
        print("Computing derived metrics...", file=sys.stderr)

    derived = compute_derived(leads_data, sales_data, events_data)

    # Build output payload
    payload = build_audit_payload(
        leads_data, sales_data, events_data, derived, args.days, api_key_prefix
    )

    # Output
    json_str = json.dumps(payload, indent=2, default=str)

    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(json_str)
        if args.verbose:
            print(f"Output written to {args.output}", file=sys.stderr)

    if args.json or not args.output:
        print(json_str)

    # Summary
    if args.verbose:
        print(f"\nSummary:", file=sys.stderr)
        print(f"  Leads:   {derived['total_leads']}", file=sys.stderr)
        print(f"  Sales:   {derived['total_sales']}", file=sys.stderr)
        print(f"  Revenue: ${derived['total_revenue']:,.2f}", file=sys.stderr)
        print(f"  Events:  {derived['total_events']}", file=sys.stderr)
        if derived['errors']:
            print(f"  Errors:  {len(derived['errors'])}", file=sys.stderr)
            for e in derived['errors']:
                print(f"    - {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
