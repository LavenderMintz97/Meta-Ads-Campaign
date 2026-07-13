"""Pull Meta ad-level insights into outputs/meta_insights.csv.

With credentials configured, this module uses the read-only insights endpoint.
Without credentials, it falls back to local example data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from src.config import OUTPUTS_DIR, assert_safe_settings, load_settings
    from src.export_csv import META_INSIGHTS_FIELDS, write_csv
    from src.meta_campaign_reader import DEFAULT_ACCOUNT_FILE, normalize_account_id, read_account_snapshot
    from src.meta_client import MetaClient
except ModuleNotFoundError:
    from config import OUTPUTS_DIR, assert_safe_settings, load_settings
    from export_csv import META_INSIGHTS_FIELDS, write_csv
    from meta_campaign_reader import DEFAULT_ACCOUNT_FILE, normalize_account_id, read_account_snapshot
    from meta_client import MetaClient


INSIGHTS_FIELDS = (
    "date_start,date_stop,campaign_id,campaign_name,adset_id,adset_name,"
    "ad_id,ad_name,impressions,reach,frequency,clicks,spend,ctr,cpc,cpm,actions"
)


def action_value(actions: list[dict[str, Any]] | None, action_names: tuple[str, ...]) -> str:
    """Sum matching action values, such as lead events."""
    total = 0.0
    for action in actions or []:
        action_type = str(action.get("action_type", "")).lower()
        if any(name in action_type for name in action_names):
            try:
                total += float(action.get("value", 0))
            except (TypeError, ValueError):
                continue
    if total.is_integer():
        return str(int(total))
    return str(total)


def conversion_value(actions: list[dict[str, Any]] | None) -> str:
    """Sum conversion-like actions when Meta returns them."""
    conversion_terms = ("offsite_conversion", "onsite_conversion", "conversion", "purchase", "complete_registration")
    lead_terms = ("lead",)
    total = 0.0
    for action in actions or []:
        action_type = str(action.get("action_type", "")).lower()
        if any(term in action_type for term in conversion_terms) and not any(term in action_type for term in lead_terms):
            try:
                total += float(action.get("value", 0))
            except (TypeError, ValueError):
                continue
    if total.is_integer():
        return str(int(total))
    return str(total)


def insight_row(account_id: str, insight: dict[str, Any], source: str, notes: str) -> dict[str, str]:
    """Map one insight object to the insights CSV schema."""
    return {
        "account_id": account_id,
        "date_start": insight.get("date_start", ""),
        "date_stop": insight.get("date_stop", ""),
        "campaign_id": insight.get("campaign_id", ""),
        "campaign_name": insight.get("campaign_name", ""),
        "adset_id": insight.get("adset_id", ""),
        "adset_name": insight.get("adset_name", ""),
        "ad_id": insight.get("ad_id", ""),
        "ad_name": insight.get("ad_name", ""),
        "impressions": insight.get("impressions", ""),
        "reach": insight.get("reach", ""),
        "clicks": insight.get("clicks", ""),
        "spend": insight.get("spend", ""),
        "ctr": insight.get("ctr", ""),
        "cpc": insight.get("cpc", ""),
        "cpm": insight.get("cpm", ""),
        "frequency": insight.get("frequency", ""),
        "leads": insight.get("leads") or action_value(insight.get("actions"), ("lead",)),
        "conversions": insight.get("conversions") or conversion_value(insight.get("actions")),
        "source": source,
        "dry_run": "true",
        "review_notes": notes,
    }


def pull_insights(client: MetaClient, account_id: str, date_preset: str) -> list[dict[str, Any]]:
    """Pull ad-level insights with spend, impressions, clicks, CTR, CPC, and leads."""
    return client.get_all(
        f"/{normalize_account_id(account_id)}/insights",
        {
            "fields": INSIGHTS_FIELDS,
            "level": "ad",
            "date_preset": date_preset,
            "limit": "500",
        },
    )


def flatten_insights(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    """Convert local example insight rows into the output schema."""
    account_id = str(snapshot.get("account_id", ""))
    notes = "Example data only. No Meta API request was made."
    return [insight_row(account_id, insight, "local_example", notes) for insight in snapshot.get("insights", [])]


def export_insights(
    account_file: Path = DEFAULT_ACCOUNT_FILE,
    output_dir: Path = OUTPUTS_DIR,
) -> dict[str, int]:
    """Write a read-only or local dry-run insights export."""
    settings = load_settings()
    assert_safe_settings(settings)
    if settings.meta_credentials_present:
        account_id = normalize_account_id(settings.meta_ad_account_id)
        notes = "Read-only Meta API insights pull. No write action was called."
        rows = [
            insight_row(account_id, insight, "meta_api_read", notes)
            for insight in pull_insights(MetaClient(settings), settings.meta_ad_account_id, settings.meta_insights_date_preset)
        ]
    else:
        rows = flatten_insights(read_account_snapshot(account_file))

    write_csv(output_dir / "meta_insights.csv", rows, META_INSIGHTS_FIELDS)
    return {"meta_insights": len(rows)}


def main() -> None:
    counts = export_insights()
    for name, count in counts.items():
        print(f"{name}: {count} rows")
    print("Insights export complete. No Meta API write action was called.")


if __name__ == "__main__":
    main()
