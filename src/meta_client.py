"""Read-only Meta Marketing API client.

The client supports GET requests for reporting and account reads. Write methods
remain blocked so this project cannot publish, edit, pause, or delete ads.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from src.config import Settings
except ModuleNotFoundError:
    from config import Settings


class MetaApiError(RuntimeError):
    """Raised when a read-only Meta API request fails."""

    def __init__(
        self,
        message: str,
        *,
        category: str = "meta_api_error",
        http_status: int | None = None,
        code: int | None = None,
        subcode: int | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.http_status = http_status
        self.code = code
        self.subcode = subcode


class MissingMetaCredentialsError(MetaApiError):
    """Raised when .env lacks the required read-only Meta settings."""


class InvalidAdAccountError(MetaApiError):
    """Raised when the configured ad account cannot be read."""


class ExpiredTokenError(MetaApiError):
    """Raised when Meta reports an expired or invalid token."""


class PermissionMetaError(MetaApiError):
    """Raised when Meta reports missing permissions."""


class MetaWriteSafetyError(MetaApiError):
    """Raised before an unsafe write request can leave the machine."""


def classify_meta_error(http_status: int, body: str) -> MetaApiError:
    """Convert a Graph API error body into a useful local exception."""
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return MetaApiError(
            f"Meta API GET failed with HTTP {http_status}: {body}",
            http_status=http_status,
        )

    error = payload.get("error", {})
    message = error.get("message", body)
    code = error.get("code")
    subcode = error.get("error_subcode")
    lowered = str(message).lower()

    if code == 190 or "expired" in lowered or "access token" in lowered:
        return ExpiredTokenError(
            f"Meta token error: {message}",
            category="expired_or_invalid_token",
            http_status=http_status,
            code=code,
            subcode=subcode,
        )
    if code in {10, 200, 294} or "permission" in lowered or "permissions" in lowered:
        return PermissionMetaError(
            f"Meta permission error: {message}",
            category="permission_error",
            http_status=http_status,
            code=code,
            subcode=subcode,
        )
    if code in {100, 1908030} or "object does not exist" in lowered or "unsupported get request" in lowered:
        return InvalidAdAccountError(
            f"Meta ad account error: {message}",
            category="invalid_ad_account",
            http_status=http_status,
            code=code,
            subcode=subcode,
        )
    return MetaApiError(
        f"Meta API GET failed with HTTP {http_status}: {message}",
        http_status=http_status,
        code=code,
        subcode=subcode,
    )


@dataclass
class MetaClient:
    settings: Settings

    def _endpoint_url(self, endpoint: str) -> str:
        """Build a versioned Graph API URL from an endpoint path."""
        clean_endpoint = endpoint.lstrip("/")
        return f"{self.settings.meta_graph_base_url.rstrip('/')}/{self.settings.meta_api_version}/{clean_endpoint}"

    def _request_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        include_token: bool = True,
        method: str = "GET",
    ) -> dict[str, Any]:
        """Execute one Graph API request and return JSON without logging secrets."""
        request_params = dict(params or {})
        if include_token:
            request_params["access_token"] = self.settings.meta_access_token
        encoded_params = urlencode(request_params, doseq=True)
        request_data = None
        if method == "GET" and request_params:
            separator = "&" if "?" in url else "?"
            full_url = f"{url}{separator}{encoded_params}"
        else:
            full_url = url
        if method == "POST":
            request_data = encoded_params.encode("utf-8")
        request = Request(full_url, data=request_data, method=method)

        try:
            with urlopen(request, timeout=self.settings.meta_request_timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as error:
            message = error.read().decode("utf-8", errors="replace")
            raise classify_meta_error(error.code, message) from error
        except URLError as error:
            raise MetaApiError(f"Meta API GET failed: {error.reason}") from error

        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise MetaApiError("Meta API returned invalid JSON.") from error

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run one read-only Graph API GET request."""
        if not self.settings.meta_credentials_present:
            raise MissingMetaCredentialsError(
                "Missing META_ACCESS_TOKEN or META_AD_ACCOUNT_ID in .env.",
                category="missing_credentials",
            )
        return self._request_json(self._endpoint_url(endpoint), params)

    def get_all(self, endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run a paginated read-only GET request and return all data rows."""
        first_page = self.get(endpoint, params)
        rows = list(first_page.get("data", []))
        next_url = first_page.get("paging", {}).get("next")

        while next_url:
            page = self._request_json(next_url, include_token=False)
            rows.extend(page.get("data", []))
            next_url = page.get("paging", {}).get("next")

        return rows

    def post(self, endpoint: str, payload: dict[str, object] | None = None) -> dict[str, object]:
        """Create only paused draft objects through allowed endpoints."""
        payload = dict(payload or {})
        endpoint_lower = endpoint.lower()
        allowed_endpoint = any(
            endpoint_lower.endswith(suffix)
            for suffix in ("/campaigns", "/adsets", "/adcreatives", "/ads")
        )
        if not allowed_endpoint:
            raise MetaWriteSafetyError(
                f"Write endpoint is not allowed: {endpoint}",
                category="unsafe_write_endpoint",
            )
        status = str(payload.get("status", "PAUSED")).upper()
        if endpoint_lower.endswith(("/campaigns", "/adsets", "/ads")) and status != "PAUSED":
            raise MetaWriteSafetyError(
                "Campaign, ad set, and ad writes must use status=PAUSED.",
                category="unsafe_write_status",
            )
        if not self.settings.meta_credentials_present:
            raise MissingMetaCredentialsError(
                "Missing META_ACCESS_TOKEN or META_AD_ACCOUNT_ID in .env.",
                category="missing_credentials",
            )
        return self._request_json(self._endpoint_url(endpoint), payload, method="POST")
