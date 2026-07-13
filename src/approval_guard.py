"""Human approval gate for any upload-like workflow.

Anything that fails these checks must stop before a Meta write action can be
considered. This module does not upload or publish anything.
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    from src.config import Settings, load_settings
except ModuleNotFoundError:
    from config import Settings, load_settings


ALLOWED_RISK_LEVELS = {"LOW", "MEDIUM"}
REQUIRED_COMPLIANCE_STATUS = "APPROVED_DRAFT"
YES_VALUES = {"YES", "Y", "TRUE", "1"}


@dataclass
class ApprovalDecision:
    can_continue: bool
    reason: str


def is_yes(value: str) -> bool:
    """Return True only for explicit yes-style approval values."""
    return str(value).strip().upper() in YES_VALUES


def check_row_approval(row: dict[str, str], settings: Settings | None = None) -> ApprovalDecision:
    """Require compliance, risk, human approval, and landing page checks."""
    settings = settings or load_settings()
    compliance_status = row.get("compliance_status", "").strip().upper()
    risk_level = row.get("risk_level", "").strip().upper()
    human_approval = row.get("human_approval", "").strip()
    landing_page_checked = row.get("landing_page_checked", "").strip()

    if compliance_status != REQUIRED_COMPLIANCE_STATUS:
        return ApprovalDecision(False, "compliance_status must be APPROVED_DRAFT.")
    if risk_level not in ALLOWED_RISK_LEVELS:
        return ApprovalDecision(False, "risk_level must be LOW or MEDIUM.")
    if not is_yes(human_approval):
        return ApprovalDecision(False, "human_approval must be YES.")
    if not is_yes(landing_page_checked):
        return ApprovalDecision(False, "landing_page_checked must be YES.")
    if not settings.dry_run and not settings.dry_run_explicitly_set:
        return ApprovalDecision(
            False,
            "DRY_RUN=false is blocked by the approval gate unless the user explicitly changes the release workflow.",
        )
    return ApprovalDecision(True, "Human approval gate passed.")


def require_all_rows_approved(rows: list[dict[str, str]], settings: Settings | None = None) -> None:
    """Raise a clear error if any row fails the human approval gate."""
    settings = settings or load_settings()
    for index, row in enumerate(rows, start=1):
        decision = check_row_approval(row, settings)
        if not decision.can_continue:
            item_id = row.get("item_id", f"row {index}")
            raise RuntimeError(f"{item_id}: {decision.reason}")
