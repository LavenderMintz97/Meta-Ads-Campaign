"""Pull Meta campaigns, ad sets, and ads into CSV files.

With credentials configured, this module uses read-only Marketing API GET
requests. Without credentials, it falls back to `data/meta_account.example.json`
so the workflow stays runnable and safe for beginners.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from src.config import DATA_DIR, OUTPUTS_DIR, assert_safe_settings, load_settings
    from src.export_csv import META_AD_FIELDS, META_ADSET_FIELDS, META_CAMPAIGN_FIELDS, write_csv
    from src.meta_client import MetaClient
except ModuleNotFoundError:
    from config import DATA_DIR, OUTPUTS_DIR, assert_safe_settings, load_settings
    from export_csv import META_AD_FIELDS, META_ADSET_FIELDS, META_CAMPAIGN_FIELDS, write_csv
    from meta_client import MetaClient


DEFAULT_ACCOUNT_FILE = DATA_DIR / "meta_account.example.json"

CAMPAIGN_FIELDS = "id,name,objective,status,effective_status,daily_budget,lifetime_budget,start_time,stop_time"
ADSET_FIELDS = "id,name,campaign_id,optimization_goal,billing_event,status,effective_status,daily_budget,targeting"
AD_FIELDS = "id,name,campaign_id,adset_id,status,effective_status,creative{id,object_story_spec}"


def normalize_account_id(account_id: str) -> str:
    """Ensure the account ID is in Meta's act_<ID> format."""
    clean = account_id.strip()
    if not clean:
        return clean
    return clean if clean.startswith("act_") else f"act_{clean}"


def read_account_snapshot(path: Path = DEFAULT_ACCOUNT_FILE) -> dict[str, Any]:
    """Load a local example account snapshot."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def extract_creative_text(creative: dict[str, Any]) -> dict[str, str]:
    """Pull useful copy fields from a Meta creative object when present."""
    story = creative.get("object_story_spec", {}) if isinstance(creative, dict) else {}
    link_data = story.get("link_data", {}) if isinstance(story, dict) else {}
    video_data = story.get("video_data", {}) if isinstance(story, dict) else {}
    photo_data = story.get("photo_data", {}) if isinstance(story, dict) else {}
    call_to_action = link_data.get("call_to_action") or video_data.get("call_to_action") or {}
    cta_value = call_to_action.get("type", "") if isinstance(call_to_action, dict) else ""

    return {
        "primary_text": link_data.get("message") or video_data.get("message") or photo_data.get("caption") or "",
        "headline": link_data.get("name") or video_data.get("title") or "",
        "description": link_data.get("description") or video_data.get("description") or "",
        "CTA": cta_value,
        "landing_page": link_data.get("link") or video_data.get("call_to_action", {}).get("value", {}).get("link", ""),
    }


def targeting_region(adset: dict[str, Any]) -> str:
    """Summarize broad target regions without exporting customer lists."""
    targeting = adset.get("targeting", {})
    geo_locations = targeting.get("geo_locations", {}) if isinstance(targeting, dict) else {}
    countries = geo_locations.get("countries", []) if isinstance(geo_locations, dict) else []
    regions = geo_locations.get("regions", []) if isinstance(geo_locations, dict) else []
    region_names = [region.get("name", "") for region in regions if isinstance(region, dict)]
    return ", ".join([*countries, *[name for name in region_names if name]])


def pull_campaigns(client: MetaClient, account_id: str) -> list[dict[str, Any]]:
    """Pull campaigns from a Meta ad account with a read-only GET request."""
    return client.get_all(
        f"/{normalize_account_id(account_id)}/campaigns",
        {"fields": CAMPAIGN_FIELDS, "limit": "100"},
    )


def pull_adsets(client: MetaClient, account_id: str) -> list[dict[str, Any]]:
    """Pull ad sets from a Meta ad account with a read-only GET request."""
    return client.get_all(
        f"/{normalize_account_id(account_id)}/adsets",
        {"fields": ADSET_FIELDS, "limit": "100"},
    )


def pull_ads(client: MetaClient, account_id: str) -> list[dict[str, Any]]:
    """Pull ads from a Meta ad account with a read-only GET request."""
    return client.get_all(
        f"/{normalize_account_id(account_id)}/ads",
        {"fields": AD_FIELDS, "limit": "100"},
    )


def flatten_campaigns(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    """Convert local campaign examples into campaign CSV rows."""
    account_id = str(snapshot.get("account_id", ""))
    rows = []
    for campaign in snapshot.get("campaigns", []):
        rows.append(campaign_row(account_id, campaign, "local_example", "Example data only. No Meta API request was made."))
    return rows


def campaign_row(account_id: str, campaign: dict[str, Any], source: str, notes: str) -> dict[str, str]:
    """Map one campaign object to the campaign CSV schema."""
    return {
        "account_id": account_id,
        "campaign_id": campaign.get("campaign_id") or campaign.get("id", ""),
        "campaign_name": campaign.get("campaign_name") or campaign.get("name", ""),
        "objective": campaign.get("objective", ""),
        "status": campaign.get("status", ""),
        "effective_status": campaign.get("effective_status", ""),
        "daily_budget": campaign.get("daily_budget", ""),
        "lifetime_budget": campaign.get("lifetime_budget", ""),
        "start_time": campaign.get("start_time", ""),
        "stop_time": campaign.get("stop_time", ""),
        "source": source,
        "dry_run": "true",
        "review_notes": notes,
    }


def flatten_adsets(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    """Convert local ad set examples into ad set CSV rows."""
    account_id = str(snapshot.get("account_id", ""))
    rows = []
    for campaign in snapshot.get("campaigns", []):
        for adset in campaign.get("adsets", []):
            rows.append(
                adset_row(
                    account_id,
                    adset,
                    campaign.get("campaign_id", ""),
                    "local_example",
                    "Example data only. No Meta API request was made.",
                )
            )
    return rows


def adset_row(
    account_id: str,
    adset: dict[str, Any],
    fallback_campaign_id: str,
    source: str,
    notes: str,
) -> dict[str, str]:
    """Map one ad set object to the ad set CSV schema."""
    return {
        "account_id": account_id,
        "campaign_id": adset.get("campaign_id") or fallback_campaign_id,
        "adset_id": adset.get("adset_id") or adset.get("id", ""),
        "adset_name": adset.get("adset_name") or adset.get("name", ""),
        "optimization_goal": adset.get("optimization_goal", ""),
        "billing_event": adset.get("billing_event", ""),
        "status": adset.get("status", ""),
        "effective_status": adset.get("effective_status", ""),
        "daily_budget": adset.get("daily_budget", ""),
        "target_region": adset.get("target_region") or targeting_region(adset),
        "source": source,
        "dry_run": "true",
        "review_notes": notes,
    }


def flatten_ads(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    """Convert local ad examples into ad CSV rows."""
    account_id = str(snapshot.get("account_id", ""))
    rows = []
    for campaign in snapshot.get("campaigns", []):
        for adset in campaign.get("adsets", []):
            for ad in adset.get("ads", []):
                rows.append(
                    ad_row(
                        account_id,
                        ad,
                        campaign.get("campaign_id", ""),
                        adset.get("adset_id", ""),
                        "local_example",
                        "Example data only. No Meta API request was made.",
                    )
                )
    return rows


def ad_row(
    account_id: str,
    ad: dict[str, Any],
    fallback_campaign_id: str,
    fallback_adset_id: str,
    source: str,
    notes: str,
) -> dict[str, str]:
    """Map one ad object to the ad CSV schema."""
    creative_text = extract_creative_text(ad.get("creative", {}))
    return {
        "account_id": account_id,
        "campaign_id": ad.get("campaign_id") or fallback_campaign_id,
        "adset_id": ad.get("adset_id") or fallback_adset_id,
        "ad_id": ad.get("ad_id") or ad.get("id", ""),
        "ad_name": ad.get("ad_name") or ad.get("name", ""),
        "platform": ad.get("platform", ""),
        "placement": ad.get("placement", ""),
        "status": ad.get("status", ""),
        "effective_status": ad.get("effective_status", ""),
        "primary_text": ad.get("primary_text") or creative_text["primary_text"],
        "headline": ad.get("headline") or creative_text["headline"],
        "description": ad.get("description") or creative_text["description"],
        "CTA": ad.get("CTA") or creative_text["CTA"],
        "landing_page": ad.get("landing_page") or creative_text["landing_page"],
        "source": source,
        "dry_run": "true",
        "review_notes": notes,
    }


def live_reader_rows(client: MetaClient, account_id: str) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Pull live read-only data and map it to CSV rows."""
    normalized_account_id = normalize_account_id(account_id)
    notes = "Read-only Meta API pull. No write action was called."
    campaigns = [campaign_row(normalized_account_id, row, "meta_api_read", notes) for row in pull_campaigns(client, account_id)]
    adsets = [adset_row(normalized_account_id, row, "", "meta_api_read", notes) for row in pull_adsets(client, account_id)]
    ads = [ad_row(normalized_account_id, row, "", "", "meta_api_read", notes) for row in pull_ads(client, account_id)]
    return campaigns, adsets, ads


def local_reader_rows(account_file: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Read local example data and map it to CSV rows."""
    snapshot = read_account_snapshot(account_file)
    return flatten_campaigns(snapshot), flatten_adsets(snapshot), flatten_ads(snapshot)


def export_campaign_reader_outputs(
    account_file: Path = DEFAULT_ACCOUNT_FILE,
    output_dir: Path = OUTPUTS_DIR,
) -> dict[str, int]:
    """Write campaign, ad set, and ad exports for review."""
    settings = load_settings()
    assert_safe_settings(settings)
    if settings.meta_credentials_present:
        campaigns, adsets, ads = live_reader_rows(MetaClient(settings), settings.meta_ad_account_id)
    else:
        campaigns, adsets, ads = local_reader_rows(account_file)

    write_csv(output_dir / "meta_campaigns.csv", campaigns, META_CAMPAIGN_FIELDS)
    write_csv(output_dir / "meta_adsets.csv", adsets, META_ADSET_FIELDS)
    write_csv(output_dir / "meta_ads.csv", ads, META_AD_FIELDS)
    return {"meta_campaigns": len(campaigns), "meta_adsets": len(adsets), "meta_ads": len(ads)}


def main() -> None:
    counts = export_campaign_reader_outputs()
    for name, count in counts.items():
        print(f"{name}: {count} rows")
    print("Campaign/ad set/ad export complete. No Meta API write action was called.")


if __name__ == "__main__":
    main()
