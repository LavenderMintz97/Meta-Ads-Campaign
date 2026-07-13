"""Safe MVP runner for Facebook and Instagram draft automation.

The runner reads a campaign brief CSV, generates reviewable drafts, runs local
compliance checks, and exports CSV files. It does not call Meta APIs and cannot
publish live ads.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import date, timedelta
from pathlib import Path

try:
    from src.compliance_check import ReviewResult, compliance_review, is_restricted_category
    from src.export_csv import (
        BASE_OUTPUT_FIELDS,
        CALENDAR_FIELDS,
        COMPLIANCE_FIELDS,
        FACEBOOK_FIELDS,
        INSTAGRAM_FIELDS,
        row_with_defaults,
        write_csv,
    )
except ModuleNotFoundError:
    # Allows the beginner-friendly command `python src/meta_ads_mvp.py`.
    from compliance_check import ReviewResult, compliance_review, is_restricted_category
    from export_csv import (
        BASE_OUTPUT_FIELDS,
        CALENDAR_FIELDS,
        COMPLIANCE_FIELDS,
        FACEBOOK_FIELDS,
        INSTAGRAM_FIELDS,
        row_with_defaults,
        write_csv,
    )


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT_DIR / "data" / "campaign_brief.example.csv"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "outputs"
PROMPTS_DIR = ROOT_DIR / "prompts"

PROMPT_FILES = (
    "compliance-review.md",
    "content-calendar.md",
    "facebook-ad-copy.md",
    "instagram-caption.md",
)

SAFE_DEFAULTS = {
    "DRY_RUN": "true",
    "AUTO_PUBLISH": "false",
    "REQUIRE_HUMAN_APPROVAL": "true",
}


def as_bool(value: str | None, default: bool) -> bool:
    """Convert common environment variable strings into booleans."""
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_prompt_files() -> dict[str, str]:
    """Load required prompt docs so missing safety instructions fail early."""
    prompts: dict[str, str] = {}
    for filename in PROMPT_FILES:
        path = PROMPTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Required prompt file is missing: {path}")
        prompts[filename] = path.read_text(encoding="utf-8")
    return prompts


def read_campaign_briefs(input_path: Path) -> list[dict[str, str]]:
    """Read the campaign brief CSV into beginner-friendly dictionaries."""
    with input_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def slugify(value: str) -> str:
    """Create a stable ID-friendly version of a campaign name."""
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts) or "campaign"


def hashtags_for(brief: dict[str, str]) -> str:
    """Create safe, relevant hashtags from brand, niche, and region fields."""
    base_tags = [
        brief.get("brand_name", "Brand"),
        brief.get("business_type", "Community"),
        brief.get("target_region", "Local"),
        brief.get("product_or_service", "Guide"),
        "Community",
        "LearnMore",
        "HelpfulGuide",
    ]
    tags = []
    for item in base_tags:
        compact = "".join(char for char in item.title() if char.isalnum())
        if compact and f"#{compact}" not in tags:
            tags.append(f"#{compact}")
    return " ".join(tags[:8])


def soft_cta(brief: dict[str, str]) -> str:
    """Use the requested CTA if present, otherwise choose a safe default."""
    return brief.get("desired_cta", "").strip() or "Learn More"


def safe_campaign_angle(brief: dict[str, str]) -> str:
    """Build a neutral angle without direct personal-attribute callouts."""
    product = brief.get("product_or_service", "this offer")
    audience = brief.get("target_audience_context", "people interested in learning more")
    return f"{product} for {audience}"


def build_creative_prompt(brief: dict[str, str], format_hint: str) -> str:
    """Describe a simple creative asset for a human designer to review."""
    product = brief.get("product_or_service", "the offer")
    brand = brief.get("brand_name", "the brand")
    tone = brief.get("tone_of_voice", "friendly and professional")
    return (
        f"{format_hint} for {brand}: show {product} in a clear, authentic, "
        f"non-exaggerated style with a {tone} tone. Avoid staged endorsements, "
        "fabricated reviews, transformation comparisons, and pressure-based urgency."
    )


def apply_review(item: dict[str, str], review: ReviewResult) -> dict[str, str]:
    """Attach compliance and approval guardrail fields to an output row."""
    reviewed = dict(item)
    reviewed["compliance_status"] = review.final_status
    reviewed["risk_level"] = review.risk_level
    reviewed["review_notes"] = review.explanation
    reviewed["human_approval"] = "NO"
    reviewed["landing_page_checked"] = "NO"
    reviewed["approval_status"] = "NEEDS_HUMAN_APPROVAL"
    reviewed["human_approved"] = "false"
    reviewed["can_publish_automatically"] = "false"
    reviewed["dry_run"] = os.environ.get("DRY_RUN", SAFE_DEFAULTS["DRY_RUN"]).lower()
    return reviewed


def generate_facebook_ads(brief: dict[str, str]) -> list[dict[str, str]]:
    """Create 10 Facebook ad drafts or safe review placeholders."""
    campaign_id = slugify(brief.get("campaign_name", "campaign"))
    cta = soft_cta(brief)
    restricted = is_restricted_category(brief)
    rows = []
    for index in range(1, 11):
        item_id = f"{campaign_id}-fb-ad-{index:02d}"
        if restricted:
            primary_text = "Policy review is required before promotional Facebook ad copy is drafted."
            headline = "Policy Review Required"
            description = "Confirm category, disclaimers, landing page, and market rules before use."
        else:
            primary_text = (
                f"Explore {safe_campaign_angle(brief)}. "
                f"{brief.get('brand_name', 'Our team')} shares a "
                f"{brief.get('tone_of_voice', 'friendly and professional')} way to learn more about "
                f"{brief.get('offer', brief.get('product_or_service', 'this offer'))}."
            )
            headline = f"{brief.get('brand_name', 'Brand')} | {brief.get('product_or_service', 'Offer')}"
            description = "A clear, reviewable draft for people interested in learning more."
        rows.append(
            {
                "item_id": item_id,
                "campaign_name": brief.get("campaign_name", ""),
                "platform": "Facebook",
                "placement": "Feed",
                "objective": brief.get("campaign_objective", ""),
                "funnel_stage": brief.get("funnel_stage", ""),
                "target_region": brief.get("target_region", ""),
                "audience_type": brief.get("target_audience_context", ""),
                "primary_text": primary_text,
                "caption": "",
                "headline": headline,
                "description": description,
                "CTA": cta,
                "creative_prompt": build_creative_prompt(brief, "Facebook feed ad"),
                "landing_page": brief.get("landing_page", ""),
            }
        )
    return rows


def generate_instagram_captions(brief: dict[str, str]) -> list[dict[str, str]]:
    """Create 10 Instagram caption drafts or safe review placeholders."""
    campaign_id = slugify(brief.get("campaign_name", "campaign"))
    cta = soft_cta(brief)
    restricted = is_restricted_category(brief)
    tags = hashtags_for(brief)
    formats = ("Reel", "Carousel", "Static post", "Story", "Educational post")
    rows = []
    for index in range(1, 11):
        post_format = formats[(index - 1) % len(formats)]
        item_id = f"{campaign_id}-ig-caption-{index:02d}"
        if restricted:
            hook = "Policy review required"
            caption = "Do not publish this caption until category, disclaimers, and landing page checks are complete."
            headline = "Policy Review Required"
            description = "Confirm category, disclaimers, landing page, and market rules before use."
        else:
            hook = f"A beginner-friendly look at {brief.get('product_or_service', 'this topic')}"
            caption = (
                f"{hook}\n\n"
                f"{brief.get('brand_name', 'The brand')} is sharing a practical, clear starting point for "
                f"{brief.get('target_audience_context', 'people interested in learning more')}.\n\n"
                f"{cta}."
            )
            headline = f"{brief.get('brand_name', 'Brand')} | {brief.get('product_or_service', 'Offer')}"
            description = "A mobile-friendly caption draft for human review."
        rows.append(
            {
                "item_id": item_id,
                "campaign_name": brief.get("campaign_name", ""),
                "platform": "Instagram",
                "placement": post_format,
                "objective": brief.get("campaign_objective", ""),
                "funnel_stage": brief.get("funnel_stage", ""),
                "target_region": brief.get("target_region", ""),
                "audience_type": brief.get("target_audience_context", ""),
                "primary_text": "",
                "caption": caption,
                "headline": headline,
                "description": description,
                "CTA": cta,
                "creative_prompt": build_creative_prompt(brief, f"Instagram {post_format.lower()}"),
                "landing_page": brief.get("landing_page", ""),
                "format": post_format,
                "hook": hook,
                "hashtags": tags,
            }
        )
    return rows


def generate_content_calendar(brief: dict[str, str], start_date: date) -> list[dict[str, str]]:
    """Create a 14-day calendar with Facebook and Instagram rows for each day."""
    campaign_id = slugify(brief.get("campaign_name", "campaign"))
    pillars = ("Education", "Community", "Behind the scenes", "Offer context", "FAQ", "Trust and proof", "Lifestyle")
    rows = []
    for day_offset in range(14):
        planned_date = start_date + timedelta(days=day_offset)
        pillar = pillars[day_offset % len(pillars)]
        for platform in ("Facebook", "Instagram"):
            item_id = f"{campaign_id}-calendar-{day_offset + 1:02d}-{platform.lower()}"
            format_name = "Facebook post" if platform == "Facebook" else "Carousel"
            caption = (
                f"Explore {brief.get('product_or_service', 'this topic')} through a {pillar.lower()} angle. "
                f"Keep the message useful, transparent, and aligned with {brief.get('brand_name', 'the brand')}."
            )
            creative_prompt = build_creative_prompt(brief, format_name)
            rows.append(
                {
                    "item_id": item_id,
                    "campaign_name": brief.get("campaign_name", ""),
                    "platform": platform,
                    "placement": format_name,
                    "objective": brief.get("campaign_objective", ""),
                    "funnel_stage": brief.get("funnel_stage", ""),
                    "target_region": brief.get("target_region", ""),
                    "audience_type": brief.get("target_audience_context", ""),
                    "primary_text": caption if platform == "Facebook" else "",
                    "caption": caption,
                    "headline": f"{pillar} | {brief.get('brand_name', 'Brand')}",
                    "description": f"14-day calendar idea for {platform}.",
                    "CTA": soft_cta(brief),
                    "creative_prompt": creative_prompt,
                    "landing_page": brief.get("landing_page", ""),
                    "date": planned_date.isoformat(),
                    "content_pillar": pillar,
                    "format": format_name,
                    "hook": f"{pillar}: {brief.get('product_or_service', 'campaign update')}",
                    "visual_direction": creative_prompt,
                    "hashtags": hashtags_for(brief),
                }
            )
    return rows


def review_rows(rows: list[dict[str, str]], brief: dict[str, str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Review every draft row and build a separate compliance checklist."""
    reviewed_rows = []
    report_rows = []
    for row in rows:
        review = compliance_review(row, brief)
        reviewed_rows.append(apply_review(row, review))
        report_rows.append(
            row_with_defaults(
                {
                    **row,
                    "compliance_status": review.final_status,
                    "risk_level": review.risk_level,
                    "review_notes": review.explanation,
                    "human_approval": "NO",
                    "landing_page_checked": "NO",
                    "approval_status": "NEEDS_HUMAN_APPROVAL",
                    "human_approved": "false",
                    "can_publish_automatically": "false",
                    "dry_run": os.environ.get("DRY_RUN", SAFE_DEFAULTS["DRY_RUN"]).lower(),
                    "issue_category": review.issue_category,
                    "issue_found": review.issue_found,
                    "severity": review.severity,
                    "explanation": review.explanation,
                    "recommended_fix": review.recommended_fix,
                    "final_status": review.final_status,
                    "can_export_to_approved_ads_sheet": "false",
                    "human_review_required": "true",
                },
                COMPLIANCE_FIELDS,
            )
        )
    return reviewed_rows, report_rows


def generate_all_outputs(input_path: Path, output_dir: Path, start_date: date) -> dict[str, int]:
    """Generate the first safe MVP output CSV files."""
    load_prompt_files()

    briefs = read_campaign_briefs(input_path)
    all_facebook: list[dict[str, str]] = []
    all_instagram: list[dict[str, str]] = []
    all_calendar: list[dict[str, str]] = []
    all_reviews: list[dict[str, str]] = []

    for brief in briefs:
        facebook_rows, facebook_reviews = review_rows(generate_facebook_ads(brief), brief)
        instagram_rows, instagram_reviews = review_rows(generate_instagram_captions(brief), brief)
        calendar_rows, calendar_reviews = review_rows(generate_content_calendar(brief, start_date), brief)

        all_facebook.extend(facebook_rows)
        all_instagram.extend(instagram_rows)
        all_calendar.extend(calendar_rows)
        all_reviews.extend(facebook_reviews + instagram_reviews + calendar_reviews)

    write_csv(output_dir / "facebook_ad_drafts.csv", all_facebook, FACEBOOK_FIELDS)
    write_csv(output_dir / "instagram_caption_drafts.csv", all_instagram, INSTAGRAM_FIELDS)
    write_csv(output_dir / "content_calendar.csv", all_calendar, CALENDAR_FIELDS)
    write_csv(output_dir / "compliance_review.csv", all_reviews, COMPLIANCE_FIELDS)

    return {
        "facebook_ad_drafts": len(all_facebook),
        "instagram_caption_drafts": len(all_instagram),
        "content_calendar": len(all_calendar),
        "compliance_review": len(all_reviews),
    }


def configure_safety_environment() -> None:
    """Set safe defaults unless a caller already provided environment values."""
    for key, value in SAFE_DEFAULTS.items():
        os.environ.setdefault(key, value)


def assert_no_live_write_mode() -> None:
    """Stop immediately if someone tries to enable auto-publishing."""
    auto_publish = as_bool(os.environ.get("AUTO_PUBLISH"), default=False)
    require_human_approval = as_bool(os.environ.get("REQUIRE_HUMAN_APPROVAL"), default=True)
    if auto_publish:
        raise RuntimeError("AUTO_PUBLISH=true is not allowed in this MVP.")
    if not require_human_approval:
        raise RuntimeError("REQUIRE_HUMAN_APPROVAL=false is not allowed in this MVP.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate safe Meta content and ad draft CSV files.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to campaign brief CSV.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Folder for output CSV files.")
    parser.add_argument("--start-date", default=date.today().isoformat(), help="Calendar start date in YYYY-MM-DD format.")
    return parser.parse_args()


def main() -> None:
    configure_safety_environment()
    assert_no_live_write_mode()
    args = parse_args()
    row_counts = generate_all_outputs(args.input, args.output_dir, date.fromisoformat(args.start_date))

    print("Safe MVP completed in draft-only mode.")
    print(f"DRY_RUN={os.environ.get('DRY_RUN')}")
    print("No Meta Ads API write actions were called.")
    for name, count in row_counts.items():
        print(f"{name}: {count} rows")


if __name__ == "__main__":
    main()
