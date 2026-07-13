"""Central safety configuration for the Meta Ads MVP."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
DOTENV_PATH = ROOT_DIR / ".env"


def parse_dotenv(path: Path | None = None) -> dict[str, str]:
    """Read simple KEY=value pairs from .env without loading shell env vars."""
    path = path or DOTENV_PATH
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def config_bool(values: dict[str, str], name: str, default: bool) -> bool:
    """Read a boolean setting from parsed .env values."""
    value = values.get(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    dry_run: bool = True
    auto_publish: bool = False
    require_human_approval: bool = True
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_access_token: str = ""
    meta_ad_account_id: str = ""
    meta_page_id: str = ""
    meta_api_version: str = "v20.0"
    meta_graph_base_url: str = "https://graph.facebook.com"
    meta_request_timeout_seconds: int = 30
    meta_insights_date_preset: str = "last_30d"
    dotenv_path: Path = DOTENV_PATH
    dry_run_explicitly_set: bool = False

    @property
    def meta_credentials_present(self) -> bool:
        """Credentials are present only when the minimum read fields exist."""
        return bool(self.meta_access_token and self.meta_ad_account_id)


def load_settings(path: Path | None = None) -> Settings:
    """Load settings from .env only, never from committed source files."""
    values = parse_dotenv(path)
    return Settings(
        dry_run=config_bool(values, "DRY_RUN", True),
        auto_publish=config_bool(values, "AUTO_PUBLISH", False),
        require_human_approval=config_bool(values, "REQUIRE_HUMAN_APPROVAL", True),
        meta_app_id=values.get("META_APP_ID", ""),
        meta_app_secret=values.get("META_APP_SECRET", ""),
        meta_access_token=values.get("META_ACCESS_TOKEN", ""),
        meta_ad_account_id=values.get("META_AD_ACCOUNT_ID", ""),
        meta_page_id=values.get("META_PAGE_ID", ""),
        meta_api_version=values.get("META_API_VERSION", "v20.0"),
        meta_graph_base_url=values.get("META_GRAPH_BASE_URL", "https://graph.facebook.com"),
        meta_request_timeout_seconds=int(values.get("META_REQUEST_TIMEOUT_SECONDS", "30") or "30"),
        meta_insights_date_preset=values.get("META_INSIGHTS_DATE_PRESET", "last_30d"),
        dotenv_path=path or DOTENV_PATH,
        dry_run_explicitly_set="DRY_RUN" in values,
    )


def assert_safe_settings(settings: Settings) -> None:
    """Stop unsafe modes before any workflow can run."""
    if not settings.dry_run and not settings.dry_run_explicitly_set:
        raise RuntimeError("DRY_RUN=false is only allowed when explicitly set in .env.")
    if settings.auto_publish:
        raise RuntimeError("AUTO_PUBLISH=true is not allowed in this safe MVP.")
    if not settings.require_human_approval:
        raise RuntimeError("REQUIRE_HUMAN_APPROVAL=false is not allowed in this safe MVP.")
