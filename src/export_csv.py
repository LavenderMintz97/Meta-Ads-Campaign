"""CSV schema and export helpers for draft-only Meta outputs."""

from __future__ import annotations

import csv
from pathlib import Path


BASE_OUTPUT_FIELDS = [
    "item_id",
    "campaign_name",
    "platform",
    "placement",
    "objective",
    "funnel_stage",
    "target_region",
    "audience_type",
    "primary_text",
    "caption",
    "headline",
    "description",
    "CTA",
    "creative_prompt",
    "landing_page",
    "compliance_status",
    "risk_level",
    "review_notes",
    "human_approval",
    "landing_page_checked",
    "approval_status",
    "human_approved",
    "can_publish_automatically",
    "dry_run",
]

FACEBOOK_FIELDS = BASE_OUTPUT_FIELDS
INSTAGRAM_FIELDS = BASE_OUTPUT_FIELDS + ["format", "hook", "hashtags"]
CALENDAR_FIELDS = BASE_OUTPUT_FIELDS + ["date", "content_pillar", "format", "hook", "visual_direction", "hashtags"]
COMPLIANCE_FIELDS = BASE_OUTPUT_FIELDS + [
    "issue_category",
    "issue_found",
    "severity",
    "explanation",
    "recommended_fix",
    "final_status",
    "can_export_to_approved_ads_sheet",
    "human_review_required",
]

META_CAMPAIGN_FIELDS = [
    "account_id",
    "campaign_id",
    "campaign_name",
    "objective",
    "status",
    "effective_status",
    "daily_budget",
    "lifetime_budget",
    "start_time",
    "stop_time",
    "source",
    "dry_run",
    "review_notes",
]

META_ADSET_FIELDS = [
    "account_id",
    "campaign_id",
    "adset_id",
    "adset_name",
    "optimization_goal",
    "billing_event",
    "status",
    "effective_status",
    "daily_budget",
    "target_region",
    "source",
    "dry_run",
    "review_notes",
]

META_AD_FIELDS = [
    "account_id",
    "campaign_id",
    "adset_id",
    "ad_id",
    "ad_name",
    "platform",
    "placement",
    "status",
    "effective_status",
    "primary_text",
    "headline",
    "description",
    "CTA",
    "landing_page",
    "source",
    "dry_run",
    "review_notes",
]

META_INSIGHTS_FIELDS = [
    "account_id",
    "date_start",
    "date_stop",
    "campaign_id",
    "campaign_name",
    "adset_id",
    "adset_name",
    "ad_id",
    "ad_name",
    "impressions",
    "reach",
    "clicks",
    "spend",
    "ctr",
    "cpc",
    "cpm",
    "frequency",
    "leads",
    "conversions",
    "source",
    "dry_run",
    "review_notes",
]

META_UPLOAD_PREVIEW_FIELDS = [
    "item_id",
    "object_type",
    "operation",
    "endpoint",
    "payload_json",
    "status",
    "dry_run",
    "review_notes",
]

META_UPLOAD_LOG_FIELDS = [
    "item_id",
    "object_type",
    "operation",
    "endpoint",
    "meta_id",
    "status",
    "dry_run",
    "rollback_notes",
    "error",
]


def row_with_defaults(row: dict[str, str], fields: list[str]) -> dict[str, str]:
    """Return a row with every requested CSV field present."""
    return {field: row.get(field, "") for field in fields}


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    """Write dictionaries to CSV with stable, explicit columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(row_with_defaults(row, fieldnames) for row in rows)
