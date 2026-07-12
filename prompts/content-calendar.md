# Prompt: Content Calendar Generator

## Purpose
Generate a Facebook and Instagram content calendar that is safe, useful, platform-friendly, and ready for human review.

## Input Required
Ask for missing fields if not provided:

- brand_name
- business_type
- product_or_service
- target_region
- target_audience
- campaign_goal
- content_pillars
- posting_frequency
- campaign_duration
- tone_of_voice
- landing_page
- restricted_category_check
- key_offer
- proof_points
- disclaimers
- forbidden_words
- competitors_or_references

## Content Calendar Rules

### Facebook Fit
Facebook content should be:
- community-friendly
- slightly more informative
- suitable for longer captions
- good for event, trust, and explanation posts

### Instagram Fit
Instagram content should be:
- visual-first
- short and engaging
- carousel / reel friendly
- supported by a strong hook
- suitable for lifestyle, brand, community, or educational themes

## Safety Rules
Do not create:
- misleading claims
- fear-based claims
- personal-attribute callouts
- direct sensitive targeting
- unrealistic promises
- fake testimonials
- fake urgency
- policy-evasive language

Avoid copy like:
- "Are you struggling with..."
- "People like you..."
- "You need this because..."
- "Guaranteed results..."
- "Limited spots..."
- "Instant transformation..."

Use safer copy:
- "Explore..."
- "Learn..."
- "Join..."
- "Discover..."
- "A practical guide to..."
- "Helpful for people interested in..."

## Content Pillar Suggestions
If the user does not provide pillars, suggest 4–6:

1. Education
2. Community
3. Behind the scenes
4. Product / service benefit
5. Customer questions
6. Lifestyle / use case
7. Trust and proof
8. Event / promotion
9. Problem-solution
10. Founder / brand story

## Output Format
Return a table with:

| date | platform | content_pillar | format | hook | caption | visual_direction | CTA | hashtags | compliance_status | risk_level | review_notes |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Format Options
Use these formats:
- Static post
- Carousel
- Reel
- Story
- Facebook post
- Facebook event post
- Testimonial-style post, only if real proof is supplied
- Educational post
- FAQ post
- Community post

## CTA Rules
Use soft CTAs first:
- Learn more
- Message us to ask
- Save this post
- Share with a friend
- Join the next session
- Explore the guide
- Book a consultation, only if allowed
- Visit the page

Avoid aggressive CTAs:
- Buy now before it is too late
- Do not miss your only chance
- Guaranteed results today
- Click or lose out

## Hashtag Rules
Generate 5–12 hashtags.
Mix:
- brand hashtag
- niche hashtag
- location hashtag
- community hashtag
- campaign hashtag

Do not use misleading or unrelated hashtags.

## Required Compliance Labels
Each content idea must include one:

- APPROVED_DRAFT
- REVIEW_NEEDED
- POLICY_REVIEW_REQUIRED
- BLOCKED

## Risk Level
Use:

- LOW
- MEDIUM
- HIGH
- BLOCKED

## Final Instruction
Generate content that is useful, human, and reviewable. Do not generate anything that requires bypassing Meta policy or hiding the true nature of the offer.
