# NEXT STEPS: Meta Ads Automation Roadmap

This file explains what to do after the starter setup is already inside the repository.

The goal is to move from a safe local draft generator into a controlled Meta Ads Manager workflow without blind auto-publishing.

---

## Current Project Status

The repository is already prepared for:

- Facebook ad draft generation
- Instagram caption draft generation
- Content calendar planning
- Compliance review
- CSV exports
- Meta credential placeholders
- Human approval guard
- Read-only Meta reporting structure
- Dry-run upload preview structure

The project should continue to follow these defaults:

```text
DRY_RUN=true
AUTO_PUBLISH=false
REQUIRE_HUMAN_APPROVAL=true
```

Do not change these until the read-only sync, approval guard, and dry-run preview are tested.

If Meta still returns `read_check_status: failed`, read `META_API_TROUBLESHOOTING.md`. Do not let a Meta permission issue block the safe local drafting workflow.

---

## Phase 1: Run the Safe Local MVP

Purpose: make sure the project can generate draft assets without touching Meta Ads Manager.

### Command

```bash
python src/meta_ads_mvp.py
```

### Expected outputs

```text
outputs/facebook_ad_drafts.csv
outputs/instagram_caption_drafts.csv
outputs/content_calendar.csv
outputs/compliance_review.csv
```

### Success condition

The CSV files are generated, and every row is marked as needing human review unless it passes local compliance checks.

---

## Phase 2: Edit the Campaign Brief

Purpose: replace the sample campaign brief with a real campaign input.

Copy the example file:

```bash
cp data/campaign_brief.example.csv data/campaign_brief.csv
```

Edit:

```text
data/campaign_brief.csv
```

Recommended fields:

```text
campaign_name
brand_name
business_type
product_or_service
target_region
target_audience_context
campaign_objective
funnel_stage
offer
landing_page
tone_of_voice
proof_points
disclaimers
restricted_category_check
forbidden_words
desired_cta
```

For Founders Club Community, a safe starting brief could be:

```text
campaign_name: Founders Club Community Launch
brand_name: Founders Club Community
business_type: Wellness and community events
product_or_service: Badminton, HIIT, wellness check-ins, and community sessions
target_region: Malaysia / Penang
target_audience_context: People interested in social wellness, community activities, badminton, and beginner-friendly fitness
campaign_objective: Awareness or Messages
funnel_stage: Awareness
offer: Join the next community session
landing_page: https://glow-grow-studio.pages.dev/
tone_of_voice: Warm, friendly, encouraging, community-first
proof_points: Weekly movement sessions, friendly community, beginner-friendly environment
disclaimers: No medical or fitness result guarantees
restricted_category_check: No
forbidden_words: guaranteed, instant transformation, cure, lose weight fast
desired_cta: Send Message
```

---

## Phase 3: Run Compliance Review

Purpose: confirm generated drafts do not contain obvious policy risks.

Run:

```bash
python src/meta_ads_mvp.py --input data/campaign_brief.csv --output-dir outputs
```

Then open:

```text
outputs/compliance_review.csv
```

Review these columns:

```text
compliance_status
risk_level
review_notes
human_review_required
recommended_fix
```

Do not move any row forward if it is marked:

```text
REVIEW_NEEDED
POLICY_REVIEW_REQUIRED
BLOCKED
HIGH
BLOCKER
```

---

## Phase 4: Create Local .env File

Purpose: prepare Meta API credentials locally without committing secrets to GitHub.

Create local `.env`:

```bash
cp .env.example .env
```

Fill in the local `.env` only:

```text
DRY_RUN=true
AUTO_PUBLISH=false
REQUIRE_HUMAN_APPROVAL=true
META_ACCESS_TOKEN=your_meta_access_token
META_AD_ACCOUNT_ID=act_your_ad_account_id
META_PAGE_ID=1281187981739289
META_API_VERSION=v20.0
META_INSIGHTS_DATE_PRESET=last_30d
```

Important:

- Do not commit `.env`.
- Do not paste tokens into ChatGPT, Codex, Claude, GitHub issues, README, screenshots, or public docs.
- Use a test ad account first if available.

---

## Phase 5: Test Meta Credential Readiness

Purpose: check whether the token and ad account can be read.

Run:

```bash
python src/meta_auth_check.py
```

Possible results:

| Result | Meaning | Next Action |
|---|---|---|
| Success | Token and ad account can be read | Continue to Phase 6 |
| Missing token | `.env` is incomplete | Add local credentials |
| Expired token | Token no longer works | Generate a new token |
| Permission error | Meta rejected the ad account read request | Read `META_API_TROUBLESHOOTING.md` |
| Invalid ad account | Wrong `act_...` ID or no access | Confirm Ads Manager account ID |

Important: a brand-new ad account with no campaigns should return `data: []`. That is success. A `#200` or `403 Forbidden` response is a permission/asset assignment issue, not an empty-campaign issue.

Do not continue to real upload-like steps until this passes. You may still continue the local draft-generation workflow because it does not call Meta.

---

## Phase 6: Pull Read-Only Meta Data

Purpose: sync reporting and account data without creating ads.

Run:

```bash
python src/meta_campaign_reader.py
```

Expected outputs:

```text
outputs/meta_campaigns.csv
outputs/meta_adsets.csv
outputs/meta_ads.csv
```

Then run:

```bash
python src/meta_insights_pull.py
```

Expected output:

```text
outputs/meta_insights.csv
```

Success condition:

- Campaign/ad/ad set data can be exported.
- Insights data can be exported.
- No campaign, ad set, ad, budget, status, or creative is changed.

If this fails because the Meta ad account has no campaign access yet, pause this phase and continue with local draft generation only.

---

## Phase 7: Prepare Approved Ads CSV

Purpose: manually approve only safe rows before any upload preview.

Create or edit:

```text
data/approved_ads.csv
```

Every row must include:

```text
compliance_status=APPROVED_DRAFT
risk_level=LOW or MEDIUM
human_approval=YES
landing_page_checked=YES
```

Recommended extra columns:

```text
item_id
campaign_name
platform
placement
objective
funnel_stage
target_region
audience_type
primary_text
headline
description
CTA
creative_prompt
landing_page
compliance_status
risk_level
human_approval
landing_page_checked
review_notes
```

Do not put real customer lists, private audience files, or tokens into CSV files.

---

## Phase 8: Run Dry-Run Upload Preview

Purpose: check what would be sent to Meta before allowing any real write action.

Keep this in `.env`:

```text
DRY_RUN=true
```

Run:

```bash
python src/meta_draft_uploader.py
```

Expected outputs:

```text
outputs/meta_upload_preview.csv
outputs/meta_upload_log.csv
```

Success condition:

- The script validates approval guard rules.
- It produces a payload preview.
- It does not create anything inside Meta Ads Manager.

If approval guard fails, fix the CSV manually. Do not bypass the guard.

---

## Phase 9: Optional Paused Draft Creation

Only attempt this after Phases 1–8 pass.

Before enabling any write-like action:

1. Confirm you are using the correct ad account.
2. Confirm the landing page is working.
3. Confirm the copy is reviewed.
4. Confirm the campaign objective and placements.
5. Confirm every object will be created as `PAUSED`.
6. Confirm rollback notes are written.

Allowed statuses:

```text
Campaign: PAUSED
Ad Set: PAUSED
Ad: PAUSED
```

Blocked:

```text
Campaign: ACTIVE
Ad Set: ACTIVE
Ad: ACTIVE
Auto-publishing
Auto-budget changes
Policy bypassing
```

---

## Phase 10: Manual Review in Meta Ads Manager

After paused draft objects exist, review inside Meta Ads Manager manually.

Check:

- campaign objective
- audience
- location
- age settings
- placements
- budget
- schedule
- creative
- page identity
- Instagram placement
- landing page
- tracking
- disclaimers

Only publish manually when you are confident.

---

## Recommended Codex Prompt for the Next Work Session

Use this prompt in Codex:

```text
Read AGENTS.md, README.md, NEXT_STEPS.md, META_API_TROUBLESHOOTING.md, .env.example, and all files in /prompts and /src.

Continue the Meta Ads automation project safely.

Your task:
1. Verify the local MVP can run with python src/meta_ads_mvp.py.
2. Verify compliance_review.csv is created.
3. Verify src/approval_guard.py blocks unsafe rows.
4. Verify Meta read-only scripts use GET only.
5. Verify src/meta_draft_uploader.py stays in DRY_RUN=true by default.
6. Add or improve tests for approval_guard.py and meta_client.py.
7. Do not publish live ads.
8. Do not create ACTIVE campaigns.
9. Do not expose credentials.
10. Update README only if instructions are missing or unclear.

If Meta returns read_check_status: failed, do not keep regenerating tokens blindly. Follow META_API_TROUBLESHOOTING.md and continue local draft generation while Meta asset access is being resolved.

After changes, summarize:
- what was changed
- what command to run
- what files are generated
- what still requires manual review
```

---

## Recommended Claude Code Prompt

```text
Read CLAUDE.md if available, then read AGENTS.md, README.md, NEXT_STEPS.md, META_API_TROUBLESHOOTING.md, and /src.

Audit this repo for Meta Ads automation safety.

Check:
1. No secrets are committed.
2. .env is ignored.
3. API writes are blocked unless approval guard passes.
4. DRY_RUN=true remains default.
5. Read-only reporting scripts only perform GET requests.
6. Draft creation, if present, creates PAUSED objects only.
7. Tests cover unsafe status, missing approval, high risk, and missing landing page check.

Do not add live publishing.
Do not add auto-budget changes.
Return a checklist of risks and fixes.
```

---

## Practical Order for Vanessa

Use this order:

```text
1. Run local MVP
2. Edit campaign brief for Founders Club Community
3. Generate draft CSVs
4. Review compliance CSV
5. Create local .env
6. Test auth
7. If auth/read check fails, follow META_API_TROUBLESHOOTING.md
8. Pull read-only Meta reports only after read check passes
9. Prepare approved_ads.csv
10. Run dry-run upload preview
11. Manually review before any paused draft creation
```

This is the safest path from Codex drafting to Meta Ads Manager automation.
