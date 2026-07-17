# Meta Page Integration Guide

This guide explains how to connect the project workflow to your Meta Page and Ads Manager setup.

Use this guide for:

```text
Page name: Founders Club Community
Meta Page ID: 1281187981739289
Website: https://glow-grow-studio.pages.dev/
```

The goal is to connect the Page identity to the automation workflow safely. This does **not** mean auto-publishing live ads.

Default safety settings must remain:

```text
DRY_RUN=true
AUTO_PUBLISH=false
REQUIRE_HUMAN_APPROVAL=true
```

---

## 1. Confirm the Meta Page exists and you have access

In Facebook / Meta Business Suite, confirm:

- You can switch into the Page profile: `Founders Club Community`.
- You have full Facebook access or task access for the Page.
- The Page ID is correct: `1281187981739289`.
- The Page is connected to the right Business Portfolio, if you use Business Manager.
- The Page can access the correct Ad Account.

Do not continue until you can manage the Page manually.

---

## 2. Connect Instagram to the Facebook Page

If you want Instagram ads or Instagram placement, connect a professional Instagram account to the Page.

Manual path in Facebook:

```text
Facebook Page profile
-> Settings & privacy
-> Settings
-> Permissions
-> Linked accounts
-> Instagram
-> Connect account
```

Manual path in Instagram:

```text
Instagram profile
-> Edit profile
-> Public business information
-> Page
-> Connect or choose Founders Club Community
```

Use a professional Instagram account, not a private personal account.

---

## 3. Prepare Meta Business / Ads Manager

Inside Meta Business Suite or Ads Manager, confirm:

- The Page is assigned to your Business Portfolio.
- The Instagram account is linked to the same business/page.
- The Ad Account exists and is active.
- The payment method is valid.
- You have advertising permissions.
- The website URL is correct:

```text
https://glow-grow-studio.pages.dev/
```

Recommended campaign objective for first test:

```text
Messages
```

or:

```text
Traffic
```

Avoid high-risk objectives or automated budget scaling until the workflow is tested.

---

## 4. Create local `.env` for Page connection

Copy the example environment file:

```bash
cp .env.example .env
```

Then add the real Page ID locally:

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
- Do not paste access tokens into ChatGPT, Codex, Claude, GitHub, screenshots, or README files.
- Do not store real tokens inside `.env.example`.
- Keep `DRY_RUN=true` until read-only sync and upload preview are tested.

---

## 5. Test Page and Ad Account readiness

Run:

```bash
python src/meta_auth_check.py
```

The script should confirm whether your token and ad account can be read.

Expected safe result:

```text
Meta credential readiness check passed.
```

If it fails, fix the Meta setup first:

| Error | Meaning | Fix |
|---|---|---|
| Missing token | `.env` is incomplete | Add token locally |
| Expired token | Token no longer works | Generate a new token |
| Permission error | Token lacks permissions | Check app permissions / business access |
| Invalid ad account | Wrong account ID | Confirm `act_...` ID in Ads Manager |
| Page error | Page ID/access issue | Confirm Page access and Page ID |

Do not continue to upload preview if auth fails.

---

## 6. Pull read-only Meta reporting first

Run campaign reader:

```bash
python src/meta_campaign_reader.py
```

Expected outputs:

```text
outputs/meta_campaigns.csv
outputs/meta_adsets.csv
outputs/meta_ads.csv
```

Run insights puller:

```bash
python src/meta_insights_pull.py
```

Expected output:

```text
outputs/meta_insights.csv
```

This confirms the project can read from Meta without creating or editing anything.

---

## 7. Generate Founders Club ad drafts locally

Edit or create:

```text
data/campaign_brief.csv
```

Suggested safe campaign brief:

```csv
campaign_name,brand_name,business_type,product_or_service,target_region,target_audience_context,campaign_objective,funnel_stage,offer,landing_page,tone_of_voice,proof_points,disclaimers,restricted_category_check,forbidden_words,desired_cta
Founders Club Community Launch,Founders Club Community,Wellness and community events,"Badminton, HIIT, wellness check-ins, and community sessions",Malaysia / Penang,"People interested in social wellness, community activities, badminton, and beginner-friendly fitness",Messages,Awareness,Join the next community session,https://glow-grow-studio.pages.dev/,Warm friendly encouraging community-first,"Weekly movement sessions, friendly community, beginner-friendly environment",No medical or fitness result guarantees,No,"guaranteed, instant transformation, cure, lose weight fast",Send Message
```

Then run:

```bash
python src/meta_ads_mvp.py --input data/campaign_brief.csv --output-dir outputs
```

Review:

```text
outputs/facebook_ad_drafts.csv
outputs/instagram_caption_drafts.csv
outputs/content_calendar.csv
outputs/compliance_review.csv
```

---

## 8. Manual approval before Meta upload preview

Do not send everything from the generated drafts into Meta.

First, manually choose the safest rows and copy them into:

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

If any of those are missing, `src/approval_guard.py` must block the workflow.

---

## 9. Run dry-run upload preview

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

This step should only show what would be sent to Meta. It should not create live ads.

---

## 10. Only later: paused draft creation

Only after all previous steps pass, you may consider controlled paused draft creation.

Allowed object statuses:

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

The first real Meta write should create **paused drafts only**, then you manually review them inside Meta Ads Manager.

---

## 11. Manual review inside Meta Ads Manager

Before publishing anything, manually check:

- Page identity: Founders Club Community
- Instagram account connection
- Campaign objective
- Ad account
- Budget
- Schedule
- Location targeting
- Placements
- Ad text
- Creative
- CTA
- Website URL
- Tracking
- Compliance notes

Only publish manually after review.

---

## 12. Codex prompt for Page integration

Use this in Codex after merging this guide:

```text
Read AGENTS.md, README.md, NEXT_STEPS.md, META_PAGE_INTEGRATION.md, .env.example, and /src.

Help me verify the Founders Club Community Meta Page integration safely.

Context:
- Meta Page ID: 1281187981739289
- Page name: Founders Club Community
- Website: https://glow-grow-studio.pages.dev/

Tasks:
1. Verify .env.example contains META_PAGE_ID placeholder only, not a real token.
2. Verify src/config.py reads META_PAGE_ID from local .env.
3. Verify src/meta_auth_check.py can report whether the Page ID and ad account are configured.
4. Verify read-only scripts do not create, edit, pause, delete, or publish anything.
5. Verify src/meta_draft_uploader.py stays in DRY_RUN=true by default.
6. Verify approval_guard.py blocks rows without human_approval=YES and landing_page_checked=YES.
7. Add tests if Page ID, approval guard, or dry-run safety is not covered.
8. Do not add auto-publishing.
9. Do not create ACTIVE campaigns.
10. Do not expose tokens or secrets.

After changes, summarize what command to run and what files are generated.
```

---

## Practical order

```text
1. Confirm Page access manually
2. Connect Instagram professional account to the Page
3. Confirm Ad Account access and payment method
4. Create local .env with META_PAGE_ID=1281187981739289
5. Run python src/meta_auth_check.py
6. Run read-only reporting scripts
7. Generate Founders Club draft ads locally
8. Review compliance CSV
9. Prepare approved_ads.csv manually
10. Run DRY_RUN upload preview
11. Manually review in Ads Manager
12. Only then consider paused draft creation
```
