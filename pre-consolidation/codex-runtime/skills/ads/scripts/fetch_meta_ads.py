#!/usr/bin/env python3
"""
Fetch Meta Ads account data via Marketing API for audit analysis.

Collects campaign structure, ad sets, ads, creatives, insights, audiences,
and pixel info. Outputs structured JSON with pre-computed derived metrics
for the 46-check Meta audit.

Usage:
    python fetch_meta_ads.py --token TOKEN
    python fetch_meta_ads.py --env-file /path/to/.env
    python fetch_meta_ads.py --token TOKEN --account act_123456 --days 30 --json
    python fetch_meta_ads.py --env-file .env --dry-run
    python fetch_meta_ads.py --env-file .env --output output/meta_audit_data.json
    python fetch_meta_ads.py --env-file .env --campaign 120210165422150366 --output output/campaign_audit.json
"""

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from urllib.parse import urlencode

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

API_VERSION = "v24.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
DEFAULT_DAYS = 30
MAX_PAGES = 50
RATE_LIMIT_PAUSE = 2  # seconds base for exponential backoff
REQUEST_TIMEOUT = 30


# ---------------------------------------------------------------------------
# API Request Helper
# ---------------------------------------------------------------------------

def api_request(url, token, params=None, retries=3):
    """Make a Graph API GET request with retry logic for rate limits.

    Returns the parsed JSON on success, or a dict with 'error' key on failure.
    """
    if params is None:
        params = {}
    params["access_token"] = token

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as exc:
            return {"error": f"Request failed: {exc}", "code": -1}

        if response.status_code == 200:
            return response.json()

        try:
            body = response.json()
        except ValueError:
            return {"error": f"HTTP {response.status_code}: non-JSON response", "code": response.status_code}

        error = body.get("error", {})
        code = error.get("code")

        if code == 80004:  # Rate limit
            wait = RATE_LIMIT_PAUSE * (2 ** attempt)
            print(f"  Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        elif code == 190:
            return {"error": "Access token expired or invalid. Generate a new token at https://developers.facebook.com/tools/explorer/", "code": 190}
        elif code == 200:
            return {"error": f"Missing permission: {error.get('message', 'unknown')}", "code": 200}
        elif code == 100:
            return {"error": f"Invalid parameter: {error.get('message', 'unknown')}", "code": 100}
        elif code == 10:
            return {"error": f"Permissions error: {error.get('message', 'unknown')}. Ensure ads_read and business_management are granted.", "code": 10}
        else:
            return {"error": error.get("message", f"Unknown error (code={code})"), "code": code}

    return {"error": "Rate limit exceeded after retries", "code": 80004}


def paginate(url, token, params=None, max_pages=MAX_PAGES):
    """Fetch all pages of a paginated Graph API response.

    Returns a list of all data items across pages.
    """
    all_data = []
    result = api_request(url, token, params=params)
    if "error" in result:
        return result

    all_data.extend(result.get("data", []))

    page = 1
    while page < max_pages:
        paging = result.get("paging", {})
        next_url = paging.get("next")
        if not next_url:
            break
        # next_url already contains the access_token
        try:
            response = requests.get(next_url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                break
            result = response.json()
            data = result.get("data", [])
            if not data:
                break
            all_data.extend(data)
            page += 1
        except requests.exceptions.RequestException:
            break

    return {"data": all_data}


# ---------------------------------------------------------------------------
# Token Management
# ---------------------------------------------------------------------------

def load_token(args):
    """Load access token from CLI arg, env file, or environment variable."""
    if args.token:
        return args.token

    if args.env_file:
        if load_dotenv:
            load_dotenv(args.env_file)
        else:
            # Manual .env parsing if python-dotenv not installed
            try:
                with open(args.env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, value = line.partition("=")
                            os.environ[key.strip()] = value.strip().strip("\"'")
            except FileNotFoundError:
                print(f"Error: .env file not found at {args.env_file}", file=sys.stderr)
                sys.exit(1)

    token = os.environ.get("META_ACCESS_TOKEN")
    if not token:
        print("Error: No access token provided.", file=sys.stderr)
        print("  Use --token TOKEN, --env-file /path/to/.env, or set META_ACCESS_TOKEN env var.", file=sys.stderr)
        sys.exit(1)
    return token


def validate_token(token):
    """Verify token is valid and has required permissions.

    Returns dict with user info and permissions, or error.
    """
    # Check token validity
    me = api_request(f"{BASE_URL}/me", token, params={"fields": "id,name"})
    if "error" in me:
        return me

    # Check permissions
    perms = api_request(f"{BASE_URL}/me/permissions", token)
    if "error" in perms:
        return perms

    granted = set()
    for p in perms.get("data", []):
        if p.get("status") == "granted":
            granted.add(p.get("permission"))

    missing = []
    for required in ["ads_read", "business_management"]:
        if required not in granted:
            missing.append(required)

    return {
        "user_id": me.get("id"),
        "user_name": me.get("name"),
        "granted_permissions": sorted(granted),
        "missing_permissions": missing,
    }


# ---------------------------------------------------------------------------
# Data Fetchers
# ---------------------------------------------------------------------------

def discover_ad_accounts(token):
    """Auto-detect ad accounts accessible with this token."""
    fields = "id,name,account_status,currency,business_name,amount_spent,balance"
    result = paginate(f"{BASE_URL}/me/adaccounts", token, params={"fields": fields})
    if "error" in result:
        return result
    return result.get("data", [])


def fetch_campaigns(token, account_id):
    """Fetch all campaigns with structure data."""
    fields = ",".join([
        "id", "name", "objective", "status", "configured_status",
        "daily_budget", "lifetime_budget", "budget_remaining",
        "buying_type", "special_ad_categories", "bid_strategy",
        "start_time", "stop_time", "created_time", "updated_time",
    ])
    result = paginate(f"{BASE_URL}/{account_id}/campaigns", token, params={"fields": fields, "limit": 100})
    if "error" in result:
        return result
    return result.get("data", [])


def fetch_adsets(token, account_id):
    """Fetch all ad sets with targeting, budget, learning phase."""
    fields = ",".join([
        "id", "name", "campaign_id", "status", "configured_status",
        "daily_budget", "lifetime_budget", "budget_remaining",
        "optimization_goal", "billing_event", "bid_strategy", "bid_amount",
        "targeting", "promoted_object",
        "learning_phase_info", "frequency_control_specs",
        "attribution_spec",
        "start_time", "end_time", "created_time", "updated_time",
    ])
    result = paginate(f"{BASE_URL}/{account_id}/adsets", token, params={"fields": fields, "limit": 100})
    if "error" in result:
        return result
    return result.get("data", [])


def fetch_ads(token, account_id):
    """Fetch all ads with creative references."""
    fields = ",".join([
        "id", "name", "adset_id", "campaign_id", "status", "configured_status",
        "creative{id,name,title,body,image_url,video_id,object_type,thumbnail_url,effective_object_story_id}",
        "created_time", "updated_time",
    ])
    result = paginate(f"{BASE_URL}/{account_id}/ads", token, params={"fields": fields, "limit": 50})
    if "error" in result:
        # Retry with minimal fields if payload too large
        fields_min = "id,name,adset_id,campaign_id,status,configured_status,creative{id,object_type,video_id,image_url},created_time"
        result = paginate(f"{BASE_URL}/{account_id}/ads", token, params={"fields": fields_min, "limit": 25})
        if "error" in result:
            return result
    return result.get("data", [])


def fetch_ad_creatives(token, account_id):
    """Fetch creative details for format analysis."""
    fields = ",".join([
        "id", "name", "title", "body", "image_url", "video_id",
        "object_type", "thumbnail_url", "effective_object_story_id",
        "asset_feed_spec", "object_story_spec",
    ])
    result = paginate(f"{BASE_URL}/{account_id}/adcreatives", token, params={"fields": fields, "limit": 50})
    if "error" in result:
        # Retry with minimal fields
        fields_min = "id,name,object_type,video_id,image_url,asset_feed_spec"
        result = paginate(f"{BASE_URL}/{account_id}/adcreatives", token, params={"fields": fields_min, "limit": 25})
        if "error" in result:
            return result
    return result.get("data", [])


def fetch_insights(token, account_id, days, level=None):
    """Fetch insights at account, campaign, or ad set level."""
    fields = ",".join([
        "impressions", "clicks", "spend", "ctr", "cpc", "cpm",
        "frequency", "reach", "actions", "action_values",
        "cost_per_action_type", "purchase_roas",
        "conversions", "conversion_values",
    ])
    params = {
        "fields": fields,
        "date_preset": f"last_{days}d" if days <= 90 else "maximum",
        "limit": 500,
    }
    if level:
        params["level"] = level
        # Add the level name and ID to fields for identification
        if level == "campaign":
            params["fields"] += ",campaign_id,campaign_name"
        elif level == "adset":
            params["fields"] += ",adset_id,adset_name"

    result = paginate(f"{BASE_URL}/{account_id}/insights", token, params=params)
    if "error" in result:
        return result
    return result.get("data", [])


def fetch_insights_timeseries(token, account_id, days=14):
    """Fetch daily ad-set-level CTR for fatigue detection."""
    params = {
        "fields": "adset_id,adset_name,ctr,impressions,clicks,spend,date_start,date_stop",
        "level": "adset",
        "time_increment": 1,
        "date_preset": f"last_{days}d",
        "limit": 1000,
    }
    result = paginate(f"{BASE_URL}/{account_id}/insights", token, params=params)
    if "error" in result:
        return result
    return result.get("data", [])


def fetch_ad_insights(token, account_id, days, campaign_id=None):
    """Fetch ad-level insights with quality rankings."""
    fields = ",".join([
        "ad_id", "ad_name", "adset_id", "adset_name",
        "campaign_id", "campaign_name",
        "impressions", "clicks", "spend", "ctr", "cpc", "cpm",
        "frequency", "reach", "actions", "action_values",
        "purchase_roas",
        "quality_ranking", "engagement_rate_ranking",
        "conversion_rate_ranking",
    ])
    params = {
        "fields": fields,
        "level": "ad",
        "date_preset": f"last_{days}d" if days <= 90 else "maximum",
        "limit": 500,
    }
    if campaign_id:
        params["filtering"] = json.dumps([{
            "field": "campaign.id",
            "operator": "EQUAL",
            "value": campaign_id,
        }])
    result = paginate(f"{BASE_URL}/{account_id}/insights", token, params=params)
    if "error" in result:
        return result
    return result.get("data", [])


def fetch_placement_breakdown(token, account_id, days, campaign_id=None):
    """Fetch placement-level performance breakdown."""
    fields = ",".join([
        "campaign_id", "campaign_name",
        "impressions", "clicks", "spend", "ctr", "cpc", "cpm",
        "actions", "action_values", "purchase_roas",
    ])
    params = {
        "fields": fields,
        "level": "campaign",
        "breakdowns": "publisher_platform,platform_position",
        "date_preset": f"last_{days}d" if days <= 90 else "maximum",
        "limit": 500,
    }
    if campaign_id:
        params["filtering"] = json.dumps([{
            "field": "campaign.id",
            "operator": "EQUAL",
            "value": campaign_id,
        }])
    result = paginate(f"{BASE_URL}/{account_id}/insights", token, params=params)
    if "error" in result:
        return result
    return result.get("data", [])


def fetch_demographic_breakdown(token, account_id, days, campaign_id=None):
    """Fetch age/gender performance breakdown."""
    fields = ",".join([
        "campaign_id", "campaign_name",
        "impressions", "clicks", "spend", "ctr",
        "actions", "action_values",
    ])
    params = {
        "fields": fields,
        "level": "campaign",
        "breakdowns": "age,gender",
        "date_preset": f"last_{days}d" if days <= 90 else "maximum",
        "limit": 500,
    }
    if campaign_id:
        params["filtering"] = json.dumps([{
            "field": "campaign.id",
            "operator": "EQUAL",
            "value": campaign_id,
        }])
    result = paginate(f"{BASE_URL}/{account_id}/insights", token, params=params)
    if "error" in result:
        return result
    return result.get("data", [])


def fetch_custom_audiences(token, account_id):
    """Fetch all custom audiences."""
    fields = ",".join([
        "id", "name", "subtype",
        "approximate_count_lower_bound", "approximate_count_upper_bound",
        "data_source", "delivery_status", "operation_status",
        "time_created", "time_updated",
    ])
    result = paginate(f"{BASE_URL}/{account_id}/customaudiences", token, params={"fields": fields, "limit": 100})
    if "error" in result:
        # Retry with minimal fields
        fields_min = "id,name,subtype,delivery_status,time_created,time_updated"
        result = paginate(f"{BASE_URL}/{account_id}/customaudiences", token, params={"fields": fields_min, "limit": 100})
        if "error" in result:
            return result
    return result.get("data", [])


def fetch_pixels(token, account_id):
    """Fetch pixel info for Chrome automation."""
    fields = "id,name,is_unavailable,last_fired_time"
    result = api_request(f"{BASE_URL}/{account_id}/adspixels", token, params={"fields": fields})
    if "error" in result:
        return result
    return result.get("data", [])


# ---------------------------------------------------------------------------
# Derived Metrics
# ---------------------------------------------------------------------------

def compute_derived(campaigns, adsets, ads, creatives, insights_account,
                    insights_campaign, insights_adset, timeseries,
                    custom_audiences, ad_insights=None, placement_breakdown=None,
                    demographic_breakdown=None, campaign_id=None):
    """Pre-compute audit-relevant metrics from raw API data."""
    # Filter to single campaign if specified
    if campaign_id:
        campaigns = [c for c in campaigns if c.get("id") == campaign_id]
        adsets = [a for a in adsets if a.get("campaign_id") == campaign_id]
        ads = [a for a in ads if a.get("campaign_id") == campaign_id]

    derived = {}

    # Active counts
    active_campaigns = [c for c in campaigns if c.get("status") == "ACTIVE"]
    active_adsets = [a for a in adsets if a.get("status") == "ACTIVE"]
    active_ads = [a for a in ads if a.get("status") == "ACTIVE"]

    derived["total_active_campaigns"] = len(active_campaigns)
    derived["total_active_adsets"] = len(active_adsets)
    derived["total_active_ads"] = len(active_ads)
    derived["total_campaigns"] = len(campaigns)
    derived["total_adsets"] = len(adsets)
    derived["total_ads"] = len(ads)

    # Campaign objectives breakdown
    objective_counts = Counter(c.get("objective", "UNKNOWN") for c in active_campaigns)
    derived["campaigns_by_objective"] = dict(objective_counts)

    # Special ad categories
    special_cats = set()
    for c in campaigns:
        for cat in c.get("special_ad_categories", []):
            special_cats.add(cat)
    derived["special_ad_categories"] = sorted(special_cats)

    # Creative format counts
    format_counts = Counter()
    for ad in ads:
        creative = ad.get("creative", {})
        obj_type = creative.get("object_type", "UNKNOWN")
        if creative.get("video_id"):
            format_counts["video"] += 1
        elif "carousel" in obj_type.lower() if obj_type else False:
            format_counts["carousel"] += 1
        elif creative.get("image_url"):
            format_counts["image"] += 1
        else:
            format_counts["other"] += 1

    # Also check asset_feed_spec for carousels in creatives
    for cr in creatives:
        afs = cr.get("asset_feed_spec")
        if afs and isinstance(afs, dict):
            bodies = afs.get("bodies", [])
            images = afs.get("images", [])
            if len(images) > 1:
                format_counts["carousel"] += 1

    derived["creative_format_counts"] = dict(format_counts)
    derived["creative_format_unique"] = len([k for k, v in format_counts.items() if v > 0 and k != "other"])

    # Creatives per ad set
    adset_creative_count = Counter()
    for ad in active_ads:
        adset_id = ad.get("adset_id")
        if adset_id:
            adset_creative_count[adset_id] += 1
    derived["creatives_per_adset"] = dict(adset_creative_count)
    counts = list(adset_creative_count.values())
    derived["avg_creatives_per_adset"] = round(sum(counts) / len(counts), 1) if counts else 0
    derived["min_creatives_per_adset"] = min(counts) if counts else 0

    # Learning phase status
    learning_limited = 0
    learning_active = 0
    for adset in active_adsets:
        lpi = adset.get("learning_phase_info", {})
        if isinstance(lpi, dict):
            status = lpi.get("status", "")
            if status == "LEARNING_LIMITED":
                learning_limited += 1
            elif status == "LEARNING":
                learning_active += 1

    derived["adsets_learning_limited"] = learning_limited
    derived["adsets_learning_active"] = learning_active
    total_active = len(active_adsets)
    derived["adsets_in_learning_limited_pct"] = round(
        (learning_limited / total_active * 100) if total_active > 0 else 0, 1
    )

    # CBO vs ABO analysis
    cbo_campaigns = []
    abo_campaigns = []
    for c in active_campaigns:
        has_campaign_budget = bool(c.get("daily_budget") or c.get("lifetime_budget"))
        if has_campaign_budget:
            cbo_campaigns.append(c.get("id"))
        else:
            abo_campaigns.append(c.get("id"))
    derived["cbo_campaign_count"] = len(cbo_campaigns)
    derived["abo_campaign_count"] = len(abo_campaigns)

    # Frequency analysis from ad set insights
    frequencies = []
    for insight in (insights_adset if isinstance(insights_adset, list) else []):
        freq = insight.get("frequency")
        if freq:
            try:
                frequencies.append(float(freq))
            except (ValueError, TypeError):
                pass

    derived["avg_frequency_overall"] = round(sum(frequencies) / len(frequencies), 2) if frequencies else 0

    # Account-level frequency from account insights
    if isinstance(insights_account, list) and insights_account:
        acct = insights_account[0] if insights_account else {}
        derived["account_frequency"] = _safe_float(acct.get("frequency"))
        derived["account_ctr"] = _safe_float(acct.get("ctr"))
        derived["account_cpc"] = _safe_float(acct.get("cpc"))
        derived["account_cpm"] = _safe_float(acct.get("cpm"))
        derived["account_spend"] = _safe_float(acct.get("spend"))
        derived["account_impressions"] = _safe_int(acct.get("impressions"))
        derived["account_reach"] = _safe_int(acct.get("reach"))

        # Extract ROAS
        roas_list = acct.get("purchase_roas", [])
        if roas_list and isinstance(roas_list, list):
            derived["account_roas"] = _safe_float(roas_list[0].get("value")) if roas_list else None
        else:
            derived["account_roas"] = None

        # Extract CPA from cost_per_action_type
        cpa_list = acct.get("cost_per_action_type", [])
        derived["account_cpa"] = _extract_cpa(cpa_list)
    else:
        derived["account_frequency"] = 0
        derived["account_ctr"] = 0
        derived["account_cpc"] = 0
        derived["account_cpm"] = 0
        derived["account_spend"] = 0
        derived["account_impressions"] = 0
        derived["account_reach"] = 0
        derived["account_roas"] = None
        derived["account_cpa"] = None

    # Creative fatigue detection from timeseries
    derived["fatigue_alerts"] = _detect_fatigue(timeseries)

    # Audience types
    audience_types = Counter()
    for aud in (custom_audiences if isinstance(custom_audiences, list) else []):
        subtype = aud.get("subtype", "UNKNOWN")
        audience_types[subtype] += 1
    derived["audience_types"] = dict(audience_types)
    derived["total_custom_audiences"] = len(custom_audiences) if isinstance(custom_audiences, list) else 0

    # Ad-level quality rankings
    if ad_insights and isinstance(ad_insights, list):
        quality_data = []
        for ai in ad_insights:
            qr = ai.get("quality_ranking")
            er = ai.get("engagement_rate_ranking")
            cr = ai.get("conversion_rate_ranking")
            if qr or er or cr:
                quality_data.append({
                    "ad_id": ai.get("ad_id"),
                    "ad_name": ai.get("ad_name"),
                    "quality_ranking": qr,
                    "engagement_rate_ranking": er,
                    "conversion_rate_ranking": cr,
                    "spend": _safe_float(ai.get("spend")),
                    "ctr": _safe_float(ai.get("ctr")),
                })
        derived["ad_quality_rankings"] = quality_data
        # Count below-average rankings
        below_avg_quality = sum(1 for q in quality_data if q.get("quality_ranking") in ("BELOW_AVERAGE_10", "BELOW_AVERAGE_20", "BELOW_AVERAGE_35"))
        below_avg_engagement = sum(1 for q in quality_data if q.get("engagement_rate_ranking") in ("BELOW_AVERAGE_10", "BELOW_AVERAGE_20", "BELOW_AVERAGE_35"))
        below_avg_conversion = sum(1 for q in quality_data if q.get("conversion_rate_ranking") in ("BELOW_AVERAGE_10", "BELOW_AVERAGE_20", "BELOW_AVERAGE_35"))
        derived["below_avg_quality_count"] = below_avg_quality
        derived["below_avg_engagement_count"] = below_avg_engagement
        derived["below_avg_conversion_count"] = below_avg_conversion

    # Placement performance summary
    if placement_breakdown and isinstance(placement_breakdown, list):
        placement_summary = []
        for row in placement_breakdown:
            placement_summary.append({
                "publisher_platform": row.get("publisher_platform"),
                "platform_position": row.get("platform_position"),
                "spend": _safe_float(row.get("spend")),
                "impressions": _safe_int(row.get("impressions")),
                "clicks": _safe_int(row.get("clicks")),
                "ctr": _safe_float(row.get("ctr")),
            })
        # Sort by spend descending
        placement_summary.sort(key=lambda x: x["spend"], reverse=True)
        derived["placement_performance"] = placement_summary

    # Demographic performance summary
    if demographic_breakdown and isinstance(demographic_breakdown, list):
        demo_summary = []
        for row in demographic_breakdown:
            demo_summary.append({
                "age": row.get("age"),
                "gender": row.get("gender"),
                "spend": _safe_float(row.get("spend")),
                "impressions": _safe_int(row.get("impressions")),
                "clicks": _safe_int(row.get("clicks")),
                "ctr": _safe_float(row.get("ctr")),
            })
        demo_summary.sort(key=lambda x: x["spend"], reverse=True)
        derived["demographic_performance"] = demo_summary

    # Budget adequacy (requires CPA estimate)
    derived["budget_analysis"] = _analyze_budgets(active_adsets, derived.get("account_cpa"))

    # Attribution settings
    attribution_configs = Counter()
    for adset in active_adsets:
        attr = adset.get("attribution_spec", [])
        if isinstance(attr, list) and attr:
            key = json.dumps(attr, sort_keys=True)
            attribution_configs[key] += 1
        else:
            attribution_configs["not_configured"] += 1
    derived["attribution_configs"] = dict(attribution_configs)

    # UTM parameter check (from ads tracking_specs)
    ads_with_utms = 0
    ads_without_utms = 0
    for ad in active_ads:
        creative = ad.get("creative", {})
        story_id = creative.get("effective_object_story_id", "")
        # Check URL parameters in ad data - simplified check
        tracking = ad.get("tracking_specs", [])
        if tracking:
            ads_with_utms += 1
        else:
            ads_without_utms += 1
    derived["ads_with_tracking"] = ads_with_utms
    derived["ads_without_tracking"] = ads_without_utms

    return derived


def _safe_float(val):
    """Safely convert to float."""
    if val is None:
        return 0.0
    try:
        return round(float(val), 4)
    except (ValueError, TypeError):
        return 0.0


def _safe_int(val):
    """Safely convert to int."""
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def _extract_cpa(cpa_list):
    """Extract most relevant CPA from cost_per_action_type list."""
    if not isinstance(cpa_list, list):
        return None
    # Priority: purchase > lead > complete_registration > link_click
    priority = ["offsite_conversion.fb_pixel_purchase", "offsite_conversion.fb_pixel_lead",
                 "offsite_conversion.fb_pixel_complete_registration", "lead",
                 "purchase", "link_click"]
    cpa_map = {}
    for item in cpa_list:
        action_type = item.get("action_type", "")
        value = item.get("value")
        if value:
            cpa_map[action_type] = _safe_float(value)

    for key in priority:
        if key in cpa_map:
            return cpa_map[key]

    # Return first available
    if cpa_map:
        return list(cpa_map.values())[0]
    return None


def _detect_fatigue(timeseries):
    """Detect creative fatigue: CTR drop >20% over 14 days."""
    alerts = []
    if not isinstance(timeseries, list) or not timeseries:
        return alerts

    # Group by adset_id
    by_adset = defaultdict(list)
    for row in timeseries:
        adset_id = row.get("adset_id")
        if adset_id:
            by_adset[adset_id].append(row)

    for adset_id, rows in by_adset.items():
        # Sort by date
        rows.sort(key=lambda r: r.get("date_start", ""))
        if len(rows) < 4:  # Need enough data points
            continue

        ctrs = []
        for r in rows:
            ctr = r.get("ctr")
            if ctr:
                try:
                    ctrs.append(float(ctr))
                except (ValueError, TypeError):
                    pass

        if len(ctrs) < 4:
            continue

        # Compare first half avg to second half avg
        mid = len(ctrs) // 2
        first_half = sum(ctrs[:mid]) / mid
        second_half = sum(ctrs[mid:]) / (len(ctrs) - mid)

        if first_half > 0:
            drop_pct = ((first_half - second_half) / first_half) * 100
            if drop_pct > 20:
                adset_name = rows[0].get("adset_name", adset_id)
                alerts.append({
                    "adset_id": adset_id,
                    "adset_name": adset_name,
                    "ctr_drop_pct": round(drop_pct, 1),
                    "ctr_first_half": round(first_half, 4),
                    "ctr_second_half": round(second_half, 4),
                })

    return alerts


def _analyze_budgets(active_adsets, account_cpa):
    """Analyze budget adequacy per ad set."""
    analysis = {
        "adequate": 0,      # >=5x CPA
        "marginal": 0,      # 2-5x CPA
        "insufficient": 0,  # <2x CPA
        "no_cpa_data": 0,
        "details": [],
    }

    if not account_cpa or account_cpa <= 0:
        analysis["no_cpa_data"] = len(active_adsets)
        return analysis

    for adset in active_adsets:
        daily_budget = adset.get("daily_budget")
        if daily_budget:
            try:
                # Budget is in cents
                budget = float(daily_budget) / 100
            except (ValueError, TypeError):
                continue

            ratio = budget / account_cpa
            detail = {
                "adset_id": adset.get("id"),
                "adset_name": adset.get("name"),
                "daily_budget": budget,
                "cpa": account_cpa,
                "ratio": round(ratio, 1),
            }

            if ratio >= 5:
                analysis["adequate"] += 1
                detail["status"] = "PASS"
            elif ratio >= 2:
                analysis["marginal"] += 1
                detail["status"] = "WARNING"
            else:
                analysis["insufficient"] += 1
                detail["status"] = "FAIL"

            analysis["details"].append(detail)

    return analysis


# ---------------------------------------------------------------------------
# Build Payload
# ---------------------------------------------------------------------------

def build_audit_payload(account_info, campaigns, adsets, ads, creatives,
                        insights_account, insights_campaign, insights_adset,
                        timeseries, custom_audiences, pixels, derived,
                        ad_insights=None, placement_breakdown=None,
                        demographic_breakdown=None):
    """Consolidate all data into audit-ready JSON structure."""
    return {
        "metadata": {
            "account_id": account_info.get("id", ""),
            "account_name": account_info.get("name", ""),
            "currency": account_info.get("currency", "USD"),
            "business_name": account_info.get("business_name", ""),
            "collection_timestamp": datetime.utcnow().isoformat() + "Z",
            "date_range": {
                "days": DEFAULT_DAYS,
            },
            "api_version": API_VERSION,
            "pixel_ids": [p.get("id") for p in (pixels if isinstance(pixels, list) else [])],
            "pixel_names": [p.get("name") for p in (pixels if isinstance(pixels, list) else [])],
            "errors": [],
        },
        "campaigns": campaigns if isinstance(campaigns, list) else [],
        "adsets": adsets if isinstance(adsets, list) else [],
        "ads": ads if isinstance(ads, list) else [],
        "creatives": creatives if isinstance(creatives, list) else [],
        "custom_audiences": custom_audiences if isinstance(custom_audiences, list) else [],
        "pixels": pixels if isinstance(pixels, list) else [],
        "insights": {
            "account_level": insights_account if isinstance(insights_account, list) else [],
            "campaign_level": insights_campaign if isinstance(insights_campaign, list) else [],
            "adset_level": insights_adset if isinstance(insights_adset, list) else [],
            "ad_level": ad_insights if isinstance(ad_insights, list) else [],
            "adset_timeseries": timeseries if isinstance(timeseries, list) else [],
            "placement_breakdown": placement_breakdown if isinstance(placement_breakdown, list) else [],
            "demographic_breakdown": demographic_breakdown if isinstance(demographic_breakdown, list) else [],
        },
        "derived": derived,
        "chrome_required": {
            "emq_scores": None,
            "pixel_health": None,
            "capi_status": None,
            "dedup_rate": None,
            "aem_configured": None,
            "domain_verified": None,
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Meta Ads account data via Marketing API for audit analysis"
    )
    parser.add_argument("--token", "-t", help="Meta access token")
    parser.add_argument("--env-file", "-e", help="Path to .env file with META_ACCESS_TOKEN")
    parser.add_argument("--account", "-a", help="Ad account ID (e.g. act_123456). Auto-detected if omitted.")
    parser.add_argument("--days", "-d", type=int, default=DEFAULT_DAYS, help=f"Days of data to fetch (default: {DEFAULT_DAYS})")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON to stdout")
    parser.add_argument("--campaign", "-c", help="Filter to specific campaign ID")
    parser.add_argument("--dry-run", action="store_true", help="Validate token and list accounts only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print progress to stderr")

    args = parser.parse_args()

    # Load and validate token
    token = load_token(args)

    if args.verbose:
        print("Validating token...", file=sys.stderr)

    validation = validate_token(token)
    if "error" in validation:
        print(f"Error: {validation['error']}", file=sys.stderr)
        sys.exit(1)

    if validation.get("missing_permissions"):
        print(f"Warning: Missing permissions: {', '.join(validation['missing_permissions'])}", file=sys.stderr)
        print("  Grant these at: https://developers.facebook.com/tools/explorer/", file=sys.stderr)

    if args.verbose:
        print(f"  Authenticated as: {validation.get('user_name')} ({validation.get('user_id')})", file=sys.stderr)
        print(f"  Permissions: {', '.join(validation.get('granted_permissions', []))}", file=sys.stderr)

    # Discover ad accounts
    if args.verbose:
        print("Discovering ad accounts...", file=sys.stderr)

    accounts = discover_ad_accounts(token)
    if isinstance(accounts, dict) and "error" in accounts:
        print(f"Error discovering accounts: {accounts['error']}", file=sys.stderr)
        sys.exit(1)

    if not accounts:
        print("Error: No ad accounts found for this token.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n=== Dry Run: Token Valid ===")
        print(f"User: {validation.get('user_name')} ({validation.get('user_id')})")
        print(f"Permissions: {', '.join(validation.get('granted_permissions', []))}")
        if validation.get("missing_permissions"):
            print(f"MISSING: {', '.join(validation['missing_permissions'])}")
        print(f"\nAd Accounts ({len(accounts)}):")
        for acct in accounts:
            status_map = {1: "ACTIVE", 2: "DISABLED", 3: "UNSETTLED", 7: "PENDING_RISK_REVIEW"}
            status = status_map.get(acct.get("account_status"), str(acct.get("account_status")))
            spent = float(acct.get("amount_spent", 0)) / 100
            print(f"  {acct.get('id')} — {acct.get('name', 'Unnamed')} [{status}] (${spent:,.2f} spent)")
        sys.exit(0)

    # Select account
    account_id = args.account
    if not account_id:
        if len(accounts) == 1:
            account_id = accounts[0].get("id")
            if args.verbose:
                print(f"  Auto-selected: {account_id} ({accounts[0].get('name', 'Unnamed')})", file=sys.stderr)
        else:
            print(f"Multiple ad accounts found ({len(accounts)}). Specify one with --account:", file=sys.stderr)
            for acct in accounts:
                print(f"  {acct.get('id')} — {acct.get('name', 'Unnamed')}", file=sys.stderr)
            sys.exit(1)

    # Find account info
    account_info = next((a for a in accounts if a.get("id") == account_id), {"id": account_id})

    # Fetch all data
    errors = []

    def fetch_with_error(name, func, *a, **kw):
        if args.verbose:
            print(f"Fetching {name}...", file=sys.stderr)
        result = func(*a, **kw)
        if isinstance(result, dict) and "error" in result:
            errors.append({"source": name, "error": result["error"]})
            if args.verbose:
                print(f"  Error: {result['error']}", file=sys.stderr)
            return []
        if args.verbose:
            count = len(result) if isinstance(result, list) else "ok"
            print(f"  {name}: {count} items", file=sys.stderr)
        return result

    campaign_filter = args.campaign

    campaigns = fetch_with_error("campaigns", fetch_campaigns, token, account_id)
    adsets = fetch_with_error("adsets", fetch_adsets, token, account_id)
    ads = fetch_with_error("ads", fetch_ads, token, account_id)
    creatives = fetch_with_error("creatives", fetch_ad_creatives, token, account_id)
    insights_account = fetch_with_error("account insights", fetch_insights, token, account_id, args.days)
    insights_campaign = fetch_with_error("campaign insights", fetch_insights, token, account_id, args.days, level="campaign")
    insights_adset = fetch_with_error("adset insights", fetch_insights, token, account_id, args.days, level="adset")
    ad_insights = fetch_with_error("ad insights", fetch_ad_insights, token, account_id, args.days, campaign_filter)
    timeseries = fetch_with_error("adset timeseries", fetch_insights_timeseries, token, account_id)
    placement_breakdown = fetch_with_error("placement breakdown", fetch_placement_breakdown, token, account_id, args.days, campaign_filter)
    demographic_breakdown = fetch_with_error("demographic breakdown", fetch_demographic_breakdown, token, account_id, args.days, campaign_filter)
    custom_audiences = fetch_with_error("custom audiences", fetch_custom_audiences, token, account_id)
    pixels = fetch_with_error("pixels", fetch_pixels, token, account_id)

    # Compute derived metrics
    if args.verbose:
        print("Computing derived metrics...", file=sys.stderr)

    derived = compute_derived(
        campaigns, adsets, ads, creatives,
        insights_account, insights_campaign, insights_adset,
        timeseries, custom_audiences,
        ad_insights=ad_insights,
        placement_breakdown=placement_breakdown,
        demographic_breakdown=demographic_breakdown,
        campaign_id=campaign_filter,
    )

    # Build payload
    payload = build_audit_payload(
        account_info, campaigns, adsets, ads, creatives,
        insights_account, insights_campaign, insights_adset,
        timeseries, custom_audiences, pixels, derived,
        ad_insights=ad_insights,
        placement_breakdown=placement_breakdown,
        demographic_breakdown=demographic_breakdown,
    )
    payload["metadata"]["errors"] = errors
    payload["metadata"]["date_range"]["days"] = args.days
    if campaign_filter:
        payload["metadata"]["campaign_filter"] = campaign_filter

    # Output
    json_str = json.dumps(payload, indent=2, default=str)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"Data saved to {args.output}", file=sys.stderr)
        print(f"\nSummary:", file=sys.stderr)
    elif args.json:
        print(json_str)
        sys.exit(0)
    else:
        print(json_str)
        sys.exit(0)

    # Print summary
    print(f"  Account: {account_info.get('name', 'Unnamed')} ({account_id})", file=sys.stderr)
    print(f"  Campaigns: {derived.get('total_active_campaigns', 0)} active / {derived.get('total_campaigns', 0)} total", file=sys.stderr)
    print(f"  Ad Sets: {derived.get('total_active_adsets', 0)} active / {derived.get('total_adsets', 0)} total", file=sys.stderr)
    print(f"  Ads: {derived.get('total_active_ads', 0)} active / {derived.get('total_ads', 0)} total", file=sys.stderr)
    print(f"  Custom Audiences: {derived.get('total_custom_audiences', 0)}", file=sys.stderr)
    print(f"  Creative Formats: {derived.get('creative_format_counts', {})}", file=sys.stderr)
    print(f"  Learning Limited: {derived.get('adsets_in_learning_limited_pct', 0)}%", file=sys.stderr)
    if derived.get("fatigue_alerts"):
        print(f"  Fatigue Alerts: {len(derived['fatigue_alerts'])} ad sets", file=sys.stderr)
    if errors:
        print(f"  Errors: {len(errors)}", file=sys.stderr)
        for e in errors:
            print(f"    - {e['source']}: {e['error']}", file=sys.stderr)


if __name__ == "__main__":
    main()
