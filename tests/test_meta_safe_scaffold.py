import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, patch

from src.approval_guard import check_row_approval
from src.config import Settings, load_settings, parse_dotenv
from src.export_csv import META_AD_FIELDS, META_ADSET_FIELDS, META_CAMPAIGN_FIELDS, META_INSIGHTS_FIELDS
from src.meta_campaign_reader import export_campaign_reader_outputs
from src.meta_auth_check import run_auth_check
from src.meta_client import ExpiredTokenError, MetaClient, MetaWriteSafetyError, PermissionMetaError, classify_meta_error
from src.meta_draft_uploader import build_dry_run_upload_plan, build_upload_payloads, run_upload
from src.meta_insights_pull import export_insights, insight_row


class MetaSafeScaffoldTests(unittest.TestCase):
    def test_approval_guard_blocks_unapproved_rows(self):
        decision = check_row_approval(
            {
                "item_id": "draft-1",
                "human_approval": "NO",
                "landing_page_checked": "YES",
                "compliance_status": "APPROVED_DRAFT",
                "risk_level": "LOW",
            }
        )

        self.assertFalse(decision.can_continue)

    def test_dry_run_upload_plan_never_marks_uploaded(self):
        plan = build_dry_run_upload_plan(
            [
                {
                    "item_id": "approved-example-001",
                    "campaign_name": "Sample",
                    "platform": "Facebook",
                    "compliance_status": "APPROVED_DRAFT",
                    "risk_level": "LOW",
                    "human_approval": "YES",
                    "landing_page_checked": "YES",
                }
            ]
        )

        self.assertEqual(len(plan), 4)
        self.assertEqual(plan[0]["operation"], "CREATE_PAUSED_DRAFT")
        self.assertEqual(plan[0]["status"], "PAUSED")
        self.assertEqual(plan[-1]["status"], "PAUSED")

    def test_upload_payloads_force_paused_campaign_adset_and_ad(self):
        settings = Settings(meta_ad_account_id="act_123", meta_page_id="page_123")
        payloads = build_upload_payloads(
            {
                "campaign_name": "Safe Campaign",
                "headline": "Safe Ad",
                "landing_page": "https://example.com",
                "primary_text": "Explore the offer.",
            },
            settings,
        )
        by_type = {payload["object_type"]: payload["payload"] for payload in payloads}

        self.assertEqual(by_type["campaign"]["status"], "PAUSED")
        self.assertEqual(by_type["ad_set"]["status"], "PAUSED")
        self.assertEqual(by_type["ad"]["status"], "PAUSED")

    def test_approval_guard_allows_medium_risk_approved_draft(self):
        decision = check_row_approval(
            {
                "compliance_status": "APPROVED_DRAFT",
                "risk_level": "MEDIUM",
                "human_approval": "YES",
                "landing_page_checked": "YES",
            }
        )

        self.assertTrue(decision.can_continue)

    def test_approval_guard_blocks_high_risk(self):
        decision = check_row_approval(
            {
                "compliance_status": "APPROVED_DRAFT",
                "risk_level": "HIGH",
                "human_approval": "YES",
                "landing_page_checked": "YES",
            }
        )

        self.assertFalse(decision.can_continue)
        self.assertIn("risk_level", decision.reason)

    def test_approval_guard_blocks_unchecked_landing_page(self):
        decision = check_row_approval(
            {
                "compliance_status": "APPROVED_DRAFT",
                "risk_level": "LOW",
                "human_approval": "YES",
                "landing_page_checked": "NO",
            }
        )

        self.assertFalse(decision.can_continue)
        self.assertIn("landing_page_checked", decision.reason)

    def test_approval_guard_blocks_non_approved_draft(self):
        decision = check_row_approval(
            {
                "compliance_status": "REVIEW_NEEDED",
                "risk_level": "LOW",
                "human_approval": "YES",
                "landing_page_checked": "YES",
            }
        )

        self.assertFalse(decision.can_continue)
        self.assertIn("compliance_status", decision.reason)

    def test_approval_guard_allows_explicit_dry_run_false_setting(self):
        settings = Settings(dry_run=False, dry_run_explicitly_set=True)
        decision = check_row_approval(
            {
                "compliance_status": "APPROVED_DRAFT",
                "risk_level": "LOW",
                "human_approval": "YES",
                "landing_page_checked": "YES",
            },
            settings,
        )

        self.assertTrue(decision.can_continue)

    def test_meta_client_blocks_write_actions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            client = MetaClient(load_settings(dotenv_path))

            with self.assertRaises(RuntimeError):
                client.post("/act_example/campaigns", {"name": "Blocked"})

    def test_meta_client_blocks_active_write_status(self):
        client = MetaClient(Settings(meta_access_token="token", meta_ad_account_id="act_123"))

        with self.assertRaises(MetaWriteSafetyError):
            client.post("/act_123/campaigns", {"name": "Unsafe", "status": "ACTIVE"})

    def test_run_upload_writes_preview_and_log_in_dry_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            approved_path = Path(temp_dir) / "approved_ads.csv"
            preview_path = Path(temp_dir) / "preview.csv"
            log_path = Path(temp_dir) / "log.csv"
            approved_path.write_text(
                "item_id,campaign_name,platform,landing_page,primary_text,headline,description,CTA,"
                "compliance_status,risk_level,human_approval,landing_page_checked\n"
                "row-1,Safe Campaign,Facebook,https://example.com,Explore this.,Headline,Description,LEARN_MORE,"
                "APPROVED_DRAFT,LOW,YES,YES\n",
                encoding="utf-8",
            )

            counts = run_upload(approved_path, preview_path, log_path, Settings(dry_run=True), print_payloads=False)

            self.assertEqual(counts["preview_rows"], 4)
            self.assertEqual(counts["log_rows"], 4)
            self.assertIn("CREATE_PAUSED_DRAFT", preview_path.read_text(encoding="utf-8"))
            self.assertIn("No rollback needed", log_path.read_text(encoding="utf-8"))

    def test_local_meta_exports_have_expected_headers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            output_dir = Path(temp_dir)
            with patch("src.config.DOTENV_PATH", dotenv_path):
                campaign_counts = export_campaign_reader_outputs(output_dir=output_dir)
                insight_counts = export_insights(output_dir=output_dir)

            self.assertEqual(campaign_counts["meta_campaigns"], 1)
            self.assertEqual(campaign_counts["meta_adsets"], 1)
            self.assertEqual(campaign_counts["meta_ads"], 1)
            self.assertEqual(insight_counts["meta_insights"], 1)

            expected = {
                "meta_campaigns.csv": META_CAMPAIGN_FIELDS,
                "meta_adsets.csv": META_ADSET_FIELDS,
                "meta_ads.csv": META_AD_FIELDS,
                "meta_insights.csv": META_INSIGHTS_FIELDS,
            }
            for filename, fields in expected.items():
                header = (output_dir / filename).read_text(encoding="utf-8").splitlines()[0].split(",")
                self.assertEqual(header, fields)

    def test_insight_row_extracts_leads_from_actions(self):
        row = insight_row(
            "act_123",
            {
                "campaign_id": "cmp_1",
                "actions": [
                    {"action_type": "link_click", "value": "3"},
                    {"action_type": "lead", "value": "2"},
                    {"action_type": "offsite_conversion.fb_pixel_lead", "value": "4"},
                ],
            },
            "meta_api_read",
            "Read-only test.",
        )

        self.assertEqual(row["leads"], "6")

    def test_insight_row_extracts_conversions_from_actions(self):
        row = insight_row(
            "act_123",
            {
                "actions": [
                    {"action_type": "purchase", "value": "1"},
                    {"action_type": "offsite_conversion.fb_pixel_purchase", "value": "2"},
                    {"action_type": "offsite_conversion.fb_pixel_lead", "value": "4"},
                ],
            },
            "meta_api_read",
            "Read-only test.",
        )

        self.assertEqual(row["conversions"], "3")

    def test_parse_dotenv_reads_credentials_from_file_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text(
                "META_ACCESS_TOKEN=file-token\nMETA_AD_ACCOUNT_ID=123\nDRY_RUN=true\n",
                encoding="utf-8",
            )

            values = parse_dotenv(dotenv_path)
            settings = load_settings(dotenv_path)

            self.assertEqual(values["META_ACCESS_TOKEN"], "file-token")
            self.assertEqual(settings.meta_ad_account_id, "123")
            self.assertTrue(settings.meta_credentials_present)

    def test_load_settings_reads_meta_page_id_from_dotenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text(
                "META_PAGE_ID=1368853385186271\nDRY_RUN=true\n",
                encoding="utf-8",
            )

            settings = load_settings(dotenv_path)

            self.assertEqual(settings.meta_page_id, "1368853385186271")
            self.assertTrue(settings.dry_run)

    def test_env_example_keeps_meta_page_id_placeholder_only(self):
        env_example = Path(__file__).resolve().parents[1] / ".env.example"
        content = env_example.read_text(encoding="utf-8")

        self.assertIn("META_PAGE_ID=\n", content)
        self.assertIn("META_ACCESS_TOKEN=\n", content)
        self.assertNotIn("1368853385186271", content)
        self.assertNotIn("META_ACCESS_TOKEN=EA", content)

    def test_auth_check_reports_missing_dotenv_credentials(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            with patch("src.config.DOTENV_PATH", dotenv_path):
                result = run_auth_check()

        self.assertEqual(result["read_check_status"], "skipped")
        self.assertEqual(result["meta_page_id_present"], "false")
        self.assertIn("Missing credentials", result["message"])

    def test_auth_check_reports_page_id_without_api_when_credentials_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text(
                "META_PAGE_ID=1368853385186271\nDRY_RUN=true\n",
                encoding="utf-8",
            )
            with patch("src.config.DOTENV_PATH", dotenv_path):
                result = run_auth_check()

        self.assertEqual(result["read_check_status"], "skipped")
        self.assertEqual(result["page_check_status"], "skipped")
        self.assertEqual(result["meta_page_id_present"], "true")
        self.assertEqual(result["meta_ad_account_id_present"], "false")
        self.assertIn("Missing credentials", result["message"])

    def test_auth_check_runs_read_only_page_check_when_page_id_is_configured(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text(
                "META_ACCESS_TOKEN=test-token\n"
                "META_AD_ACCOUNT_ID=act_123\n"
                "META_PAGE_ID=1368853385186271\n"
                "DRY_RUN=true\n",
                encoding="utf-8",
            )
            with patch("src.config.DOTENV_PATH", dotenv_path), patch("src.meta_auth_check.MetaClient.get") as get:
                get.side_effect = [
                    {"id": "user_1", "name": "Test User"},
                    {"id": "act_123", "name": "Test Account"},
                    {"id": "1368853385186271", "name": "Glow Grow Studio"},
                ]
                result = run_auth_check()

        self.assertEqual(result["read_check_status"], "passed")
        self.assertEqual(result["page_check_status"], "passed")
        self.assertEqual(result["meta_page_id_present"], "true")
        self.assertEqual(result["meta_page_read_id_present"], "true")
        get.assert_has_calls(
            [
                call("/me", {"fields": "id,name"}),
                call("/act_123", {"fields": "id,account_id,name,account_status"}),
                call("/1368853385186271", {"fields": "id,name"}),
            ]
        )

    def test_meta_error_classifies_expired_token(self):
        error = classify_meta_error(400, '{"error":{"message":"Session has expired","code":190}}')

        self.assertIsInstance(error, ExpiredTokenError)
        self.assertEqual(error.category, "expired_or_invalid_token")

    def test_meta_error_classifies_permission_error(self):
        error = classify_meta_error(403, '{"error":{"message":"Permissions error","code":200}}')

        self.assertIsInstance(error, PermissionMetaError)
        self.assertEqual(error.category, "permission_error")


if __name__ == "__main__":
    unittest.main()
