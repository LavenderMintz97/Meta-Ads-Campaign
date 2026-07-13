# Meta Ads Campaign Automation

A Codex-ready starter repo for creating **Facebook and Instagram content/ad draft automation**.

This project is designed to help with:

- Facebook post drafts
- Instagram caption drafts
- Facebook ad copy drafts
- Instagram ad copy drafts
- Content calendar planning
- Creative prompt generation
- Meta-style compliance review
- CSV / Google Sheets-ready exports

## Important Safety Rule

This repo is for **drafting, reviewing, and preparing** ads. It is **not** designed for blind auto-publishing.

Default mode:

```text
DRY_RUN=true
AUTO_PUBLISH=false
REQUIRE_HUMAN_APPROVAL=true
```

Codex must not publish, launch, pause, delete, or change live campaigns unless you explicitly build and approve a controlled workflow later.

---

## Folder Structure

```text
Meta-Ads-Campaign/
  AGENTS.md
  README.md
  .env.example
  prompts/
    content-calendar.md
    facebook-ad-copy.md
    instagram-caption.md
    compliance-review.md
  data/
    approved_ads.csv
    approved_ads.example.csv
    campaign_brief.example.csv
    meta_account.example.json
  outputs/
    .gitkeep
    meta_campaigns.csv
    meta_adsets.csv
    meta_ads.csv
    meta_insights.csv
    meta_upload_preview.csv
    meta_upload_log.csv
  src/
    __init__.py
    approval_guard.py
    compliance_check.py
    config.py
    export_csv.py
    meta_auth_check.py
    meta_campaign_reader.py
    meta_client.py
    meta_draft_uploader.py
    meta_insights_pull.py
    meta_ads_mvp.py
  tests/
    test_compliance_check.py
    test_compliance.py
    test_meta_safe_scaffold.py
```

## What Each File Does

| File | Purpose |
|---|---|
| `AGENTS.md` | Main Codex instruction file. Defines project rules, safety limits, and Meta-style policy guardrails. |
| `prompts/content-calendar.md` | Prompt template for generating Facebook and Instagram content calendars. |
| `prompts/facebook-ad-copy.md` | Prompt template for generating Facebook ad copy drafts. |
| `prompts/instagram-caption.md` | Prompt template for generating Instagram captions. |
| `prompts/compliance-review.md` | Prompt template for reviewing drafts before approval. |
| `.env.example` | Placeholder environment variables. Never put real secrets in this file. |
| `data/approved_ads.csv` | Approved ad input used by the guarded draft uploader. |
| `data/approved_ads.example.csv` | Example manually approved ads for dry-run upload validation only. |
| `data/campaign_brief.example.csv` | Example campaign input format for Codex or future scripts. |
| `data/meta_account.example.json` | Local fake Meta account snapshot used for dry-run CSV exports. |
| `outputs/` | Future generated drafts and compliance reports. |
| `outputs/meta_upload_preview.csv` | Dry-run payload preview for paused draft object creation. |
| `outputs/meta_upload_log.csv` | Upload or dry-run log with rollback notes. |
| `src/approval_guard.py` | Requires explicit human approval before upload-like workflows can continue. |
| `src/compliance_check.py` | Local policy pre-checks for generated drafts. |
| `src/config.py` | Central dry-run and safety settings. |
| `src/export_csv.py` | Stable CSV schemas and export helper. |
| `src/meta_auth_check.py` | Local-only Meta credential readiness check. |
| `src/meta_campaign_reader.py` | Exports local example campaign/ad set/ad CSVs without API calls. |
| `src/meta_client.py` | Dry-run Meta client placeholder that blocks write actions. |
| `src/meta_draft_uploader.py` | Dry-run approval validation path; it does not upload ads. |
| `src/meta_insights_pull.py` | Exports local example insights without API calls. |
| `src/meta_ads_mvp.py` | Safe Python MVP that generates draft CSVs and runs local compliance checks. |
| `tests/test_compliance_check.py` | Focused tests for restricted categories, claims, and personal-attribute checks. |
| `tests/test_compliance.py` | Tests for the compliance checker. |
| `tests/test_meta_safe_scaffold.py` | Tests for approval guardrails and dry-run Meta export scaffolding. |

---

## Safe Python MVP

The MVP is dependency-free and uses only Python's standard library.

It does four things:

1. Reads `data/campaign_brief.example.csv`.
2. Generates Facebook ad drafts, Instagram caption drafts, and a 14-day content calendar.
3. Runs the local compliance pre-check inspired by `prompts/compliance-review.md`.
4. Exports CSV files into `outputs/`.

It does not call the Meta Ads API, does not create campaigns, and does not publish ads.

Every generated row includes:

- `approval_status=NEEDS_HUMAN_APPROVAL`
- `human_approved=false`
- `can_publish_automatically=false`

That means no draft is treated as finally approved until a person reviews it.

### Requirements

Install Python 3.10 or newer.

Check your version:

```bash
python --version
```

### Run the MVP

From the repo folder:

```bash
python src/meta_ads_mvp.py
```

The script defaults to:

```text
DRY_RUN=true
AUTO_PUBLISH=false
REQUIRE_HUMAN_APPROVAL=true
```

You can also pass a custom input file:

```bash
python src/meta_ads_mvp.py --input data/campaign_brief.example.csv --output-dir outputs
```

To choose the first day of the 14-day calendar:

```bash
python src/meta_ads_mvp.py --start-date 2026-07-12
```

### Output Files

Running the script creates:

```text
outputs/facebook_ad_drafts.csv
outputs/instagram_caption_drafts.csv
outputs/content_calendar.csv
outputs/compliance_review.csv
```

`outputs/compliance_review.csv` is the reviewer checklist. It includes the issue category, risk level, recommended fix, and whether human review is required.

All four output files include the core review/upload columns:

```text
campaign_name
platform
placement
objective
funnel_stage
target_region
audience_type
primary_text
caption
headline
description
CTA
creative_prompt
landing_page
compliance_status
risk_level
review_notes
```

The compliance report includes extra checklist columns such as `issue_category`, `recommended_fix`, `final_status`, and `human_review_required`.

### Run Tests

Use the built-in unittest runner:

```bash
python -m unittest discover -s tests
```

Run tests after changing compliance logic.

### Beginner Notes

- Edit `data/campaign_brief.example.csv` or copy it to a new CSV file for a real campaign.
- Keep `restricted_category_check=Yes` when the campaign may involve finance, health, supplements, politics, housing, jobs, dating, alcohol, gambling, or other sensitive categories.
- Do not add tokens, app secrets, ad account IDs, or customer lists to the repo.
- Treat `APPROVED_DRAFT` as "no local blocking issue found", not as permission to publish.
- Final approval and any upload to Meta must stay manual in this MVP.

### Meta Read-Only Reporting

The Meta reporting files support read-only pulls when `META_ACCESS_TOKEN` and `META_AD_ACCOUNT_ID` are configured in a local `.env` file. Credentials are read from `.env` only. If credentials are missing, reporting scripts fall back to `data/meta_account.example.json` so the example workflow still runs.

These scripts use GET requests only. They do not create, edit, pause, delete, upload, or publish anything.

Create your local `.env` file:

```bash
cp .env.example .env
```

Then fill in:

```text
DRY_RUN=true
AUTO_PUBLISH=false
REQUIRE_HUMAN_APPROVAL=true
META_ACCESS_TOKEN=your-read-token
META_AD_ACCOUNT_ID=act_your_ad_account_id
META_PAGE_ID=your_page_id_for_ad_creatives
META_API_VERSION=v20.0
META_INSIGHTS_DATE_PRESET=last_30d
```

`.env` is ignored by Git. Never commit Meta tokens, ad account IDs, customer lists, or real campaign exports.

Run local credential readiness checks:

```bash
python src/meta_auth_check.py
```

The auth check handles:

- missing token or ad account
- invalid ad account
- expired or invalid token
- permission errors

Pull campaigns, ad sets, and ads into CSV files:

```bash
python src/meta_campaign_reader.py
```

Pull ad-level spend, impressions, clicks, CTR, CPC, and leads:

```bash
python src/meta_insights_pull.py
```

The insights export includes spend, impressions, clicks, CTR, CPC, CPM, reach, frequency, leads, and conversions when Meta returns them.

Validate approved ads without uploading:

```bash
python src/meta_draft_uploader.py
```

The uploader reads `data/approved_ads.csv`. With `DRY_RUN=true`, it only prints the payloads and writes:

```text
outputs/meta_upload_preview.csv
outputs/meta_upload_log.csv
```

The human approval gate stops unless every row has:

```text
compliance_status=APPROVED_DRAFT
risk_level=LOW or MEDIUM
human_approval=YES
landing_page_checked=YES
```

`DRY_RUN=false` is only allowed when it is explicitly changed in `.env`. Even then, this MVP still does not publish or upload live ads.

When `DRY_RUN=false`, the uploader can only create draft objects in `PAUSED` status:

```text
Campaign -> PAUSED
Ad Set -> PAUSED
Ad Creative -> created for the paused ad
Ad -> PAUSED
```

It does not build automatic publishing. `outputs/meta_upload_log.csv` includes rollback notes so any created paused draft objects can be reviewed and manually deleted in Meta Ads Manager if needed.

Read-only reporting settings:

```text
META_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=
META_API_VERSION=v20.0
META_INSIGHTS_DATE_PRESET=last_30d
```

---

## Recommended Codex First Prompt

Paste this into Codex after opening this repo:

```text
Read AGENTS.md and all files inside /prompts.

Build a safe MVP for Facebook and Instagram content/ad draft automation.

Requirements:
1. Read data/campaign_brief.example.csv.
2. Generate Facebook ad drafts.
3. Generate Instagram caption drafts.
4. Generate a 14-day content calendar.
5. Run compliance-review.md logic against every draft.
6. Export outputs to CSV files inside /outputs.
7. Use DRY_RUN=true by default.
8. Do not publish live ads.
9. Do not call Meta Ads API write actions.
10. Require human approval before anything is marked as approved.

Preferred stack: Python.
Add clear setup instructions and beginner-friendly comments.
```

---

## Suggested MVP Output Files

When Codex builds the first version, ask it to create:

```text
outputs/content_calendar.csv
outputs/facebook_ad_drafts.csv
outputs/instagram_caption_drafts.csv
outputs/compliance_review.csv
```

Each output should include:

- campaign_name
- platform
- placement
- objective
- funnel_stage
- target_region
- audience_type
- primary_text or caption
- headline
- description
- CTA
- creative_prompt
- landing_page
- compliance_status
- risk_level
- review_notes

---

## Recommended CSV Input Columns

The example campaign brief contains these columns:

```text
campaign_name,brand_name,business_type,product_or_service,target_region,target_audience_context,campaign_objective,funnel_stage,offer,landing_page,tone_of_voice,proof_points,disclaimers,restricted_category_check,forbidden_words,desired_cta
```

---

## Safe Workflow

Use this workflow first:

```text
Campaign Brief -> Codex Draft Generation -> Compliance Review -> Human Review -> Approved CSV -> Manual Upload
```

Do not start with:

```text
Campaign Brief -> AI -> Auto Publish
```

That is risky and not recommended.

---

## Future Features

After the safe MVP works, Codex can help add:

- Google Sheets export
- Meta Ads read-only reporting
- Content calendar scheduling table
- Creative prompt generator
- Landing page checklist
- Compliance rule tests
- Dashboard view
- Optional Meta API draft campaign preparation

Keep publishing manual until the review workflow is strong.

---

## Notes for Vanessa

This repo is a good portfolio project because it combines:

- SEO/content strategy
- Meta ads planning
- compliance thinking
- AI workflow design
- beginner-friendly automation
- CSV/reporting logic

Start with the content + ad drafting MVP first. Then improve reporting and workflow automation later.
