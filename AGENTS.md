# AGENTS.md

## Project Name
Meta Ads Campaign Automation

## Goal
Build a safe Codex-ready workspace for Facebook and Instagram content planning, ad copy drafting, caption generation, creative prompt drafting, compliance review, and export-ready campaign tables.

This repo is for **drafting and review**. It must not publish, launch, pause, delete, or modify live Meta campaigns unless Vanessa explicitly requests a live action and the workflow has human approval.

## Default Operating Mode

```text
DRY_RUN=true
AUTO_PUBLISH=false
REQUIRE_HUMAN_APPROVAL=true
```

## What Codex Can Do
- Generate Facebook post drafts.
- Generate Instagram caption drafts.
- Generate ad copy drafts.
- Generate content calendar ideas.
- Create creative/image/video prompt drafts.
- Run compliance review against the prompt rules.
- Export draft tables to CSV or Google Sheets-ready format.
- Prepare read-only reporting logic if API credentials are configured.

## What Codex Must Not Do by Default
- Do not auto-publish ads.
- Do not create live campaigns.
- Do not change budgets.
- Do not pause or delete campaigns.
- Do not edit targeting on live campaigns.
- Do not upload creatives to a live ad account.
- Do not store secrets in code.
- Do not commit `.env`, tokens, API keys, ad account IDs, customer lists, or private reports.
- Do not suggest bypassing Meta review.

## Meta-Style Policy Safety Rules
Generated content must avoid:
- Misleading claims.
- Exaggerated guarantees.
- Fake urgency or fake scarcity.
- Fake testimonials or fake reviews.
- Before/after claims without proof.
- Unrealistic income, health, beauty, body, or finance promises.
- Clickbait or shock tactics.
- Discriminatory targeting.
- Direct references to sensitive personal traits.
- Copy that implies the advertiser knows private information about the viewer.

Avoid direct personal-attribute copy such as:
- “Are you overweight?”
- “Struggling with debt?”
- “Are you depressed?”
- “Single and lonely?”
- “Do you have acne?”
- “Are you broke?”
- “People like you need this.”

Use neutral wording instead:
- “Explore simple budgeting tools.”
- “Discover skincare routine basics.”
- “Plan healthier habits with a supportive community.”
- “Compare solutions for your business growth.”
- “Helpful for people interested in…”

## Restricted or Sensitive Categories
If a brief involves a regulated, age-restricted, sensitive, or legally complex category, Codex must mark the item as `POLICY_REVIEW_REQUIRED` and generate a checklist instead of publish-ready ad copy.

Sensitive categories include:
- Financial products, loans, investment, crypto.
- Healthcare, medicine, supplements, weight loss, beauty claims with medical implications.
- Employment, housing, politics, social issues.
- Dating, alcohol, tobacco.
- Gambling, betting, casino, or similar restricted services.
- Adult content, weapons, surveillance tools, illegal goods or services.

## Gambling / Betting / Casino Rule
Do not generate promotional ad copy, targeting suggestions, conversion strategy, or ad automation flows for gambling, betting, casino, or similar restricted services.

Allowed:
- General compliance checklist.
- Neutral risk notes.
- Recommendation to consult platform policy and legal counsel.

Not allowed:
- Promotional casino ad copy.
- Gambling audience targeting.
- Betting-related campaign structure.
- Ways to bypass ad restrictions.
- Wording designed to evade review systems.

## Human Approval Workflow
Every generated asset must have a status field.

Allowed statuses:
- `DRAFT`
- `REVIEW_NEEDED`
- `POLICY_REVIEW_REQUIRED`
- `APPROVED`
- `REJECTED`
- `NEEDS_LANDING_PAGE_CHECK`
- `NEEDS_LEGAL_REVIEW`

Only `APPROVED` items can be exported to the final approved sheet. Even approved items must not be auto-published.

## Required Output Fields for Campaign Assets
- campaign_name
- platform
- placement
- objective
- funnel_stage
- target_region
- audience_type
- primary_text
- headline
- description
- CTA
- creative_prompt
- landing_page
- compliance_status
- risk_level
- review_notes

Risk levels:
- `LOW`
- `MEDIUM`
- `HIGH`
- `BLOCKED`

## Development Rules
Preferred stack:
- Python or Node.js.
- `.env` for credentials.
- `.env.example` for placeholder variables only.
- CSV or Google Sheets export.
- Dry-run mode.
- Logging without secrets.
- Tests for compliance checker.

When changing compliance logic, add or update tests.

## Codex Instructions
When working in this repo, Codex should:
1. Read `AGENTS.md` first.
2. Read all files in `/prompts`.
3. Ask for missing campaign details instead of guessing.
4. Generate drafts, not live ads.
5. Prefer safer language over aggressive conversion copy.
6. Clearly flag policy risk.
7. Never hide uncertainty.
8. Never suggest policy evasion.
9. Keep changes small and reviewable.
10. Keep `DRY_RUN=true` unless Vanessa explicitly changes it.
