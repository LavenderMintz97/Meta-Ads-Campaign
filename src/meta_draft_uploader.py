"""Strictly guarded Meta draft uploader.

Default behavior is DRY_RUN=true: build paused Campaign -> Ad Set -> Ad Creative
-> Ad payloads, print them, and save preview/log CSV files. When DRY_RUN=false
is explicitly set in `.env`, this module can create only PAUSED objects.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

try:
    from src.approval_guard import check_row_approval
    from src.config import DATA_DIR, OUTPUTS_DIR, Settings, assert_safe_settings, load_settings
    from src.export_csv import META_UPLOAD_LOG_FIELDS, META_UPLOAD_PREVIEW_FIELDS, write_csv
    from src.meta_campaign_reader import normalize_account_id
    from src.meta_client import MetaClient
except ModuleNotFoundError:
    from approval_guard import check_row_approval
    from config import DATA_DIR, OUTPUTS_DIR, Settings, assert_safe_settings, load_settings
    from export_csv import META_UPLOAD_LOG_FIELDS, META_UPLOAD_PREVIEW_FIELDS, write_csv
    from meta_campaign_reader import normalize_account_id
    from meta_client import MetaClient


DEFAULT_APPROVED_ADS_FILE = DATA_DIR / "approved_ads.csv"
DEFAULT_PREVIEW_FILE = OUTPUTS_DIR / "meta_upload_preview.csv"
DEFAULT_LOG_FILE = OUTPUTS_DIR / "meta_upload_log.csv"
PAUSED = "PAUSED"


def read_approved_ads(path: Path = DEFAULT_APPROVED_ADS_FILE) -> list[dict[str, str]]:
    """Read approved ads from CSV."""
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def json_compact(value: Any) -> str:
    """Serialize nested payload values for preview and Graph API form posts."""
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def normalize_cta(value: str) -> str:
    """Convert a friendly CTA label into Meta's enum-like format."""
    clean = str(value or "LEARN_MORE").strip().upper().replace(" ", "_")
    return clean or "LEARN_MORE"


def campaign_payload(row: dict[str, str]) -> dict[str, Any]:
    """Build a paused campaign payload."""
    return {
        "name": row.get("campaign_name", "Draft Campaign"),
        "objective": row.get("meta_objective") or "OUTCOME_TRAFFIC",
        "status": PAUSED,
        "special_ad_categories": json_compact([]),
    }


def adset_payload(row: dict[str, str], campaign_id: str) -> dict[str, Any]:
    """Build a paused ad set payload."""
    targeting_json = row.get("targeting_json") or json_compact({"geo_locations": {"countries": ["MY"]}})
    return {
        "name": row.get("adset_name") or f"{row.get('campaign_name', 'Draft Campaign')} Ad Set",
        "campaign_id": campaign_id,
        "billing_event": row.get("billing_event") or "IMPRESSIONS",
        "optimization_goal": row.get("optimization_goal") or "LINK_CLICKS",
        "daily_budget": row.get("daily_budget") or "1000",
        "targeting": targeting_json,
        "status": PAUSED,
    }


def creative_payload(row: dict[str, str], page_id: str) -> dict[str, Any]:
    """Build an ad creative payload for a link-style draft ad."""
    story_spec = {
        "page_id": page_id,
        "link_data": {
            "message": row.get("primary_text") or row.get("caption") or "",
            "link": row.get("landing_page", ""),
            "name": row.get("headline", ""),
            "description": row.get("description", ""),
            "call_to_action": {
                "type": normalize_cta(row.get("CTA", "")),
                "value": {"link": row.get("landing_page", "")},
            },
        },
    }
    return {
        "name": row.get("creative_name") or f"{row.get('campaign_name', 'Draft Campaign')} Creative",
        "object_story_spec": json_compact(story_spec),
    }


def ad_payload(row: dict[str, str], adset_id: str, creative_id: str) -> dict[str, Any]:
    """Build a paused ad payload."""
    return {
        "name": row.get("ad_name") or row.get("headline") or f"{row.get('campaign_name', 'Draft Campaign')} Ad",
        "adset_id": adset_id,
        "creative": json_compact({"creative_id": creative_id}),
        "status": PAUSED,
    }


def build_upload_payloads(row: dict[str, str], settings: Settings) -> list[dict[str, Any]]:
    """Build the safe Campaign -> Ad Set -> Ad Creative -> Ad payload sequence."""
    account_id = normalize_account_id(settings.meta_ad_account_id or "act_DRY_RUN_ACCOUNT")
    page_id = settings.meta_page_id or "PAGE_ID_REQUIRED_FOR_LIVE_UPLOAD"
    return [
        {
            "object_type": "campaign",
            "endpoint": f"/{account_id}/campaigns",
            "payload": campaign_payload(row),
        },
        {
            "object_type": "ad_set",
            "endpoint": f"/{account_id}/adsets",
            "payload": adset_payload(row, "{{campaign_id}}"),
        },
        {
            "object_type": "ad_creative",
            "endpoint": f"/{account_id}/adcreatives",
            "payload": creative_payload(row, page_id),
        },
        {
            "object_type": "ad",
            "endpoint": f"/{account_id}/ads",
            "payload": ad_payload(row, "{{adset_id}}", "{{creative_id}}"),
        },
    ]


def preview_rows_for(row: dict[str, str], settings: Settings) -> list[dict[str, str]]:
    """Convert payloads to preview CSV rows."""
    rows = []
    for payload_spec in build_upload_payloads(row, settings):
        rows.append(
            {
                "item_id": row.get("item_id", ""),
                "object_type": payload_spec["object_type"],
                "operation": "CREATE_PAUSED_DRAFT",
                "endpoint": payload_spec["endpoint"],
                "payload_json": json_compact(payload_spec["payload"]),
                "status": PAUSED if payload_spec["object_type"] != "ad_creative" else "NO_STATUS_FIELD",
                "dry_run": str(settings.dry_run).lower(),
                "review_notes": "Preview only. No Meta API write action was called.",
            }
        )
    return rows


def dry_run_log_rows(preview_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Build upload log rows for dry-run mode."""
    return [
        {
            "item_id": row["item_id"],
            "object_type": row["object_type"],
            "operation": row["operation"],
            "endpoint": row["endpoint"],
            "meta_id": "",
            "status": "DRY_RUN_PREVIEW",
            "dry_run": row["dry_run"],
            "rollback_notes": "No rollback needed. No Meta object was created.",
            "error": "",
        }
        for row in preview_rows
    ]


def assert_live_upload_ready(settings: Settings) -> None:
    """Require explicit live-upload prerequisites before any POST request."""
    if settings.dry_run:
        return
    if not settings.dry_run_explicitly_set:
        raise RuntimeError("DRY_RUN=false must be explicitly set in .env.")
    if not settings.meta_credentials_present:
        raise RuntimeError("META_ACCESS_TOKEN and META_AD_ACCOUNT_ID are required for DRY_RUN=false.")
    if not settings.meta_page_id:
        raise RuntimeError("META_PAGE_ID is required to create ad creatives with DRY_RUN=false.")


def create_paused_objects(row: dict[str, str], settings: Settings, client: MetaClient) -> list[dict[str, str]]:
    """Create only PAUSED objects and return upload log rows."""
    created: dict[str, str] = {}
    log_rows: list[dict[str, str]] = []
    payloads = build_upload_payloads(row, settings)

    try:
        for spec in payloads:
            payload = dict(spec["payload"])
            if spec["object_type"] == "ad_set":
                payload["campaign_id"] = created["campaign"]
            if spec["object_type"] == "ad":
                payload["adset_id"] = created["ad_set"]
                payload["creative"] = json_compact({"creative_id": created["ad_creative"]})

            response = client.post(spec["endpoint"], payload)
            meta_id = str(response.get("id", ""))
            created[spec["object_type"]] = meta_id
            log_rows.append(
                {
                    "item_id": row.get("item_id", ""),
                    "object_type": spec["object_type"],
                    "operation": "CREATE_PAUSED_DRAFT",
                    "endpoint": spec["endpoint"],
                    "meta_id": meta_id,
                    "status": "CREATED_PAUSED",
                    "dry_run": "false",
                    "rollback_notes": "Created in PAUSED status. If needed, manually delete this draft object in Meta Ads Manager.",
                    "error": "",
                }
            )
    except Exception as error:
        log_rows.append(
            {
                "item_id": row.get("item_id", ""),
                "object_type": "upload_flow",
                "operation": "CREATE_PAUSED_DRAFT",
                "endpoint": "",
                "meta_id": "",
                "status": "STOPPED_WITH_ERROR",
                "dry_run": "false",
                "rollback_notes": f"Previously created paused objects, if any: {json_compact(created)}. Review and delete manually in Meta Ads Manager.",
                "error": str(error),
            }
        )
        raise
    return log_rows


def build_dry_run_upload_plan(rows: list[dict[str, str]], settings: Settings | None = None) -> list[dict[str, str]]:
    """Compatibility helper that returns preview rows without uploading."""
    settings = settings or load_settings()
    preview_rows: list[dict[str, str]] = []
    for row in rows:
        decision = check_row_approval(row, settings)
        if not decision.can_continue:
            raise RuntimeError(f"{row.get('item_id', 'row')}: {decision.reason}")
        preview_rows.extend(preview_rows_for(row, settings))
    return preview_rows


def run_upload(
    path: Path = DEFAULT_APPROVED_ADS_FILE,
    preview_file: Path = DEFAULT_PREVIEW_FILE,
    log_file: Path = DEFAULT_LOG_FILE,
    settings: Settings | None = None,
    print_payloads: bool = True,
) -> dict[str, int]:
    """Validate approved ads and either preview or create paused draft objects."""
    settings = settings or load_settings()
    assert_safe_settings(settings)
    assert_live_upload_ready(settings)
    rows = read_approved_ads(path)

    preview_rows: list[dict[str, str]] = []
    log_rows: list[dict[str, str]] = []
    client = MetaClient(settings)
    for row in rows:
        decision = check_row_approval(row, settings)
        if not decision.can_continue:
            raise RuntimeError(f"{row.get('item_id', 'row')}: {decision.reason}")

        row_preview = preview_rows_for(row, settings)
        preview_rows.extend(row_preview)
        if settings.dry_run:
            if print_payloads:
                for preview in row_preview:
                    print(preview["payload_json"])
            log_rows.extend(dry_run_log_rows(row_preview))
        else:
            log_rows.extend(create_paused_objects(row, settings, client))

    write_csv(preview_file, preview_rows, META_UPLOAD_PREVIEW_FIELDS)
    write_csv(log_file, log_rows, META_UPLOAD_LOG_FIELDS)
    return {"preview_rows": len(preview_rows), "log_rows": len(log_rows)}


def main() -> None:
    counts = run_upload()
    print(f"meta_upload_preview: {counts['preview_rows']} rows")
    print(f"meta_upload_log: {counts['log_rows']} rows")
    print("Upload workflow complete. Active ads were not published.")


if __name__ == "__main__":
    main()
