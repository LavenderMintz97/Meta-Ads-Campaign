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
    campaign_brief.example.csv
  outputs/
    .gitkeep
  src/
    .gitkeep
  tests/
    .gitkeep
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
| `data/campaign_brief.example.csv` | Example campaign input format for Codex or future scripts. |
| `outputs/` | Future generated drafts and compliance reports. |
| `src/` | Future automation scripts. |
| `tests/` | Future compliance checker tests. |

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
Campaign Brief → Codex Draft Generation → Compliance Review → Human Review → Approved CSV → Manual Upload
```

Do not start with:

```text
Campaign Brief → AI → Auto Publish
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
