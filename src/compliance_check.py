"""Local compliance checks for safe Meta draft automation.

This module is intentionally conservative. It only pre-screens draft text for
human review; it does not replace Meta review, legal review, or policy advice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


SENSITIVE_CATEGORY_WORDS = (
    "financial",
    "loan",
    "investment",
    "crypto",
    "healthcare",
    "medicine",
    "supplement",
    "employment",
    "housing",
    "politic",
    "social issue",
    "dating",
    "alcohol",
    "gambling",
    "betting",
    "casino",
    "adult",
    "weapon",
    "surveillance",
)

BLOCKED_CATEGORY_WORDS = ("gambling", "betting", "casino", "adult", "weapon", "illegal")

PERSONAL_ATTRIBUTE_PHRASES = (
    "are you overweight",
    "do you have debt",
    "are you depressed",
    "are you single",
    "your skin is bad",
    "you are unemployed",
    "you suffer from",
    "are you broke",
    "people like you",
    "you need this because",
)

MISLEADING_CLAIM_WORDS = (
    "guaranteed",
    "instant",
    "miracle",
    "overnight",
    "risk-free",
    "100% proven",
    "clinically proven",
    "limited spots",
    "only chance",
    "fake testimonial",
)

DISCRIMINATORY_TARGETING_WORDS = (
    "race",
    "ethnicity",
    "religion",
    "health condition",
    "political affiliation",
    "sexual orientation",
    "disability",
    "financial hardship",
)


@dataclass
class ReviewResult:
    issue_category: str
    issue_found: str
    severity: str
    explanation: str
    recommended_fix: str
    final_status: str
    risk_level: str


def normalize_list(value: str) -> list[str]:
    """Split comma-separated values while ignoring blanks."""
    return [item.strip() for item in value.split(",") if item.strip()]


def contains_any(text: str, phrases: Iterable[str]) -> list[str]:
    """Return every phrase found inside text, case-insensitively."""
    lower_text = text.lower()
    return [phrase for phrase in phrases if phrase in lower_text]


def brief_text(brief: dict[str, str]) -> str:
    """Combine campaign brief values for simple category checks."""
    return " ".join(value for value in brief.values() if value)


def is_restricted_category(brief: dict[str, str]) -> bool:
    """Detect regulated, age-restricted, sensitive, or legally complex briefs."""
    explicit_check = brief.get("restricted_category_check", "").strip().lower()
    if explicit_check and explicit_check not in {"no", "none", "n/a", "na", "false"}:
        return True
    return bool(contains_any(brief_text(brief), SENSITIVE_CATEGORY_WORDS))


def is_blocked_category(brief: dict[str, str]) -> bool:
    """Detect categories where promotional draft copy should not be generated."""
    return bool(contains_any(brief_text(brief), BLOCKED_CATEGORY_WORDS))


def restricted_review(brief: dict[str, str]) -> ReviewResult:
    """Return strict review results for restricted or blocked categories."""
    if is_blocked_category(brief):
        return ReviewResult(
            issue_category="Restricted Category",
            issue_found="Blocked or highly restricted category detected",
            severity="BLOCKER",
            explanation="The brief appears to involve gambling, adult, weapon, illegal, or similarly blocked content.",
            recommended_fix="Do not create promotional copy. Prepare only a neutral compliance checklist.",
            final_status="BLOCKED",
            risk_level="BLOCKED",
        )
    return ReviewResult(
        issue_category="Restricted Category",
        issue_found="Sensitive category detected or not ruled out",
        severity="HIGH",
        explanation="The brief may involve a regulated or sensitive category that needs policy and legal review.",
        recommended_fix="Confirm market rules, required disclaimers, advertiser verification, and landing page compliance.",
        final_status="POLICY_REVIEW_REQUIRED",
        risk_level="HIGH",
    )


def compliance_review(item: dict[str, str], brief: dict[str, str]) -> ReviewResult:
    """Apply the local compliance-review.md logic to one draft item."""
    if is_restricted_category(brief):
        return restricted_review(brief)

    searchable_fields = [
        item.get("primary_text", ""),
        item.get("headline", ""),
        item.get("description", ""),
        item.get("caption", ""),
        item.get("hook", ""),
        item.get("creative_prompt", ""),
        brief.get("target_audience_context", ""),
        brief.get("offer", ""),
        brief.get("proof_points", ""),
    ]
    searchable_text = " ".join(searchable_fields)

    personal_hits = contains_any(searchable_text, PERSONAL_ATTRIBUTE_PHRASES)
    if personal_hits:
        return ReviewResult(
            issue_category="Personal Attributes",
            issue_found=", ".join(personal_hits),
            severity="HIGH",
            explanation="The copy may imply the viewer has a sensitive personal trait.",
            recommended_fix="Rewrite with neutral wording such as 'Explore' or 'Helpful for people interested in'.",
            final_status="REVIEW_NEEDED",
            risk_level="HIGH",
        )

    claim_hits = contains_any(searchable_text, MISLEADING_CLAIM_WORDS)
    forbidden_hits = contains_any(
        searchable_text,
        [word.lower() for word in normalize_list(brief.get("forbidden_words", ""))],
    )
    if claim_hits or forbidden_hits:
        found = claim_hits + forbidden_hits
        return ReviewResult(
            issue_category="Misleading Claims",
            issue_found=", ".join(sorted(set(found))),
            severity="MEDIUM",
            explanation="The draft contains wording that may overpromise or conflict with the campaign brief.",
            recommended_fix="Remove guarantees, fake urgency, and unsupported claims.",
            final_status="REVIEW_NEEDED",
            risk_level="MEDIUM",
        )

    targeting_hits = contains_any(brief.get("target_audience_context", ""), DISCRIMINATORY_TARGETING_WORDS)
    if targeting_hits:
        return ReviewResult(
            issue_category="Targeting Review",
            issue_found=", ".join(targeting_hits),
            severity="HIGH",
            explanation="The audience context may include sensitive or discriminatory targeting.",
            recommended_fix="Use broad interests, geography, language, or consent-compliant engagement audiences.",
            final_status="POLICY_REVIEW_REQUIRED",
            risk_level="HIGH",
        )

    landing_page = brief.get("landing_page", "")
    if not landing_page.startswith(("http://", "https://")):
        return ReviewResult(
            issue_category="Landing Page Quality",
            issue_found="Landing page is missing or not a URL",
            severity="MEDIUM",
            explanation="The landing page cannot be checked from the brief.",
            recommended_fix="Add a complete landing page URL and verify that the offer matches the ad.",
            final_status="NEEDS_LANDING_PAGE_CHECK",
            risk_level="MEDIUM",
        )

    return ReviewResult(
        issue_category="No blocking issue found",
        issue_found="None",
        severity="LOW",
        explanation="No local pre-check issue was detected, but human review is still required.",
        recommended_fix="Human reviewer should confirm landing page, claims, CTA, and final suitability.",
        final_status="APPROVED_DRAFT",
        risk_level="LOW",
    )
