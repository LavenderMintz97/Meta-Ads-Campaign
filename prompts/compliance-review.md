# Prompt: Meta Ads Compliance Review

## Purpose
Review Facebook and Instagram ad/content drafts before they are approved for upload, scheduling, or manual publishing.

This prompt does not replace Meta review, legal review, or professional compliance advice. It is a pre-screening checklist.

## Input Required
Review the following fields:

- brand_name
- platform
- placement
- campaign_objective
- target_region
- audience_context
- primary_text
- headline
- description
- caption
- CTA
- creative_prompt
- landing_page
- offer
- proof_points
- disclaimers
- category
- restricted_category_check

## Review Categories

### 1. Personal Attributes
Flag if the copy directly or indirectly implies the viewer has a sensitive trait.

High-risk examples:
- "Are you overweight?"
- "Do you have debt?"
- "Are you depressed?"
- "Are you single?"
- "Your skin is bad."
- "You are unemployed."
- "You suffer from..."

Safe alternatives:
- "Explore tools for budgeting."
- "Learn skincare routine basics."
- "Join a supportive community."
- "Discover beginner-friendly resources."

Status:
- If direct personal-attribute callout exists: `REVIEW_NEEDED`
- If sensitive and exploitative: `BLOCKED`

---

### 2. Misleading Claims
Flag:
- guaranteed results
- instant outcomes
- unrealistic transformation
- income promises
- medical claims without proof
- "clinically proven" without evidence
- "risk-free" without terms
- fake testimonials
- fake authority

Status:
- Unsupported claim: `REVIEW_NEEDED`
- Deceptive claim: `BLOCKED`

---

### 3. Restricted / Sensitive Category
Check if the ad involves:

- financial products
- investment
- crypto
- healthcare
- medicine
- supplements
- employment
- housing
- political or social issues
- dating
- alcohol
- gambling or betting
- adult content
- weapons
- surveillance
- illegal goods or services

If yes, mark:
`POLICY_REVIEW_REQUIRED`

Do not approve without:
- market confirmation
- policy confirmation
- legal/compliance review where needed
- landing page review
- required disclaimers
- advertiser verification where applicable

---

### 4. Landing Page Quality
Check:

- page loads
- mobile-friendly
- offer matches ad
- no misleading redirects
- pricing is clear
- business identity is clear
- contact details exist
- privacy policy exists where needed
- terms/refund policy exists where relevant
- no hidden subscription
- no exaggerated claims

If unknown:
`NEEDS_LANDING_PAGE_CHECK`

---

### 5. Creative Review
Flag if creative prompt includes:

- fake celebrity endorsement
- fake review screenshot
- fake news layout
- unrealistic before/after
- body shame
- fear-based image
- misleading UI
- copyrighted characters
- brand logo misuse
- exaggerated money/health result

Status:
- minor risk: `REVIEW_NEEDED`
- deceptive or harmful: `BLOCKED`

---

### 6. Targeting Review
Flag targeting if it uses:

- race
- ethnicity
- religion
- health condition
- political affiliation
- sexual orientation
- disability
- financial hardship
- exact individual targeting
- exclusionary targeting for protected categories

Safe targeting should be based on:
- broad interests
- location
- language
- engagement audiences
- website visitors, if consent-compliant
- lookalikes, if allowed and compliant
- content context

Status:
- sensitive targeting: `POLICY_REVIEW_REQUIRED`
- discriminatory targeting: `BLOCKED`

---

## Output Format

Return this table:

| item_id | issue_category | issue_found | severity | explanation | recommended_fix | final_status |
|---|---|---|---|---|---|---|

Severity:
- LOW
- MEDIUM
- HIGH
- BLOCKER

Final status:
- APPROVED_DRAFT
- REVIEW_NEEDED
- POLICY_REVIEW_REQUIRED
- NEEDS_LANDING_PAGE_CHECK
- BLOCKED

## Final Summary Format

After the table, add:

```text
Overall Status:
Risk Level:
Can Export to Approved Ads Sheet?: Yes/No
Can Publish Automatically?: No
Human Review Required?: Yes/No
Key Fixes Needed:
```

## Approval Logic

Approve only if:

- no personal attribute issue
- no misleading claim
- no unsupported guarantee
- no sensitive category uncertainty
- landing page is aligned
- CTA is accurate
- creative is not deceptive
- required disclaimers are present
- no discriminatory targeting
- no platform evasion intent

Even when approved, final output must remain:
`APPROVED_DRAFT`

Never mark anything as:
`AUTO_PUBLISH_READY`

## Final Instruction
Be strict. It is better to delay an ad for review than to publish unsafe, misleading, or policy-risk content.
