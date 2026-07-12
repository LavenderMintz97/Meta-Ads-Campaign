# Prompt: Facebook Ad Copy Generator

## Purpose
Generate safe Facebook ad copy drafts for human review.

## Input Required
Before generating, check for:

- brand_name
- product_or_service
- campaign_objective
- target_region
- target_audience_context
- funnel_stage
- offer
- landing_page
- proof_points
- disclaimers
- restricted_category_check
- tone_of_voice
- desired CTA
- forbidden_claims
- competitor_reference, optional

## Facebook Ad Copy Principles
Facebook ad copy can be slightly longer than Instagram ad copy.
It should explain:
- what the offer is
- who it may be useful for
- why it matters
- what action to take next

## Policy-Safe Copy Rules

### Do not use personal-attribute targeting language
Avoid:
- "Are you broke?"
- "Are you overweight?"
- "Do you suffer from..."
- "Are you lonely?"
- "Your skin is terrible."
- "You have bad credit."
- "You are struggling with..."

Use:
- "Explore a simple way to..."
- "A practical option for people interested in..."
- "Designed to support..."
- "Helpful for anyone looking to..."
- "Learn how to..."

### Do not overpromise
Avoid:
- guaranteed results
- instant transformation
- unrealistic income
- unrealistic health or beauty outcomes
- "risk-free" unless legally true
- "100% proven" unless supported
- fake scarcity

### Do not create deceptive framing
Avoid:
- fake news style
- fake government endorsement
- fake celebrity endorsement
- hidden subscription
- unclear pricing
- misleading landing page claims

## Required Output
Generate 10 Facebook ad copy variations.

Use this table:

| variation | funnel_stage | primary_text | headline | description | CTA | creative_direction | compliance_status | risk_level | review_notes |
|---:|---|---|---|---|---|---|---|---|---|

## Funnel Stage Definitions

### Awareness
Goal:
- introduce brand
- educate
- build recognition

Copy style:
- soft
- informative
- curiosity-led

### Consideration
Goal:
- explain benefits
- answer objections
- encourage message / landing page visit

Copy style:
- useful
- trust-building
- clearer CTA

### Conversion
Goal:
- encourage sign-up, inquiry, booking, purchase, or lead

Copy style:
- direct but not aggressive
- transparent offer
- no false urgency

## CTA Options
Use only suitable CTAs:
- Learn More
- Send Message
- Sign Up
- Book Now
- Contact Us
- Get Quote
- Subscribe
- Download
- Register

## Restricted Category Handling
If the product or service is sensitive or regulated, do not generate normal ad copy.

Instead, output:

```text
POLICY_REVIEW_REQUIRED
Reason:
Required checks:
Suggested safer angle:
Landing page requirements:
Disclaimers needed:
```

Sensitive categories include:
- financial services
- healthcare
- medicine
- supplements
- employment
- housing
- politics
- social issues
- crypto
- dating
- weight loss
- alcohol
- gambling or betting
- adult content
- weapons
- surveillance
- illegal or restricted goods

## Final Safety Check
Before final output, check each variation for:

1. Personal attribute violation
2. Unsupported claim
3. Sensitive category issue
4. Landing page mismatch risk
5. Misleading CTA
6. Unrealistic result
7. Missing disclaimer
8. Excessive urgency
9. Discriminatory wording
10. Brand safety risk

If any problem exists, mark:
`REVIEW_NEEDED` or `POLICY_REVIEW_REQUIRED`.
