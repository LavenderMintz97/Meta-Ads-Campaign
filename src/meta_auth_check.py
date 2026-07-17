"""Check whether Meta credentials are configured for read-only pulls."""

from __future__ import annotations

try:
    from src.config import assert_safe_settings, load_settings
    from src.meta_campaign_reader import normalize_account_id
    from src.meta_client import MetaApiError, MetaClient, MissingMetaCredentialsError
except ModuleNotFoundError:
    from config import assert_safe_settings, load_settings
    from meta_campaign_reader import normalize_account_id
    from meta_client import MetaApiError, MetaClient, MissingMetaCredentialsError


def run_auth_check() -> dict[str, str]:
    """Return credential readiness and optionally run read-only Graph checks."""
    settings = load_settings()
    assert_safe_settings(settings)
    result = {
        "dry_run": str(settings.dry_run).lower(),
        "meta_credentials_present": str(settings.meta_credentials_present).lower(),
        "meta_ad_account_id_present": str(bool(settings.meta_ad_account_id)).lower(),
        "meta_page_id_present": str(bool(settings.meta_page_id)).lower(),
        "meta_access_token_present": str(bool(settings.meta_access_token)).lower(),
        "read_check_status": "skipped",
        "page_check_status": "skipped",
        "message": "Missing credentials. No Meta API request was made.",
    }
    if not settings.meta_credentials_present:
        return result

    client = MetaClient(settings)
    try:
        response = client.get("/me", {"fields": "id,name"})
        account_response = client.get(
            f"/{normalize_account_id(settings.meta_ad_account_id)}",
            {"fields": "id,account_id,name,account_status"},
        )
        page_response = None
        if settings.meta_page_id:
            page_response = client.get(
                f"/{settings.meta_page_id}",
                {"fields": "id,name"},
            )
    except MissingMetaCredentialsError as error:
        result["read_check_status"] = "failed"
        result["error_category"] = error.category
        result["message"] = str(error)
        return result
    except MetaApiError as error:
        result["read_check_status"] = "failed"
        result["error_category"] = error.category
        result["message"] = str(error)
        return result

    result["read_check_status"] = "passed"
    result["meta_user_id_present"] = str(bool(response.get("id"))).lower()
    result["ad_account_id_present"] = str(bool(account_response.get("id"))).lower()
    if page_response is not None:
        result["page_check_status"] = "passed"
        result["meta_page_read_id_present"] = str(bool(page_response.get("id"))).lower()
        result["meta_page_name_present"] = str(bool(page_response.get("name"))).lower()
        result["message"] = (
            "Read-only Meta token, ad account, and Page checks passed. "
            "No write action was called."
        )
    else:
        result["message"] = (
            "Read-only Meta token and ad account checks passed. "
            "META_PAGE_ID is not configured, so the Page check was skipped. "
            "No write action was called."
        )
    return result


def main() -> None:
    for key, value in run_auth_check().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
