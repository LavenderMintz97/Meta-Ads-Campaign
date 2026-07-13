import unittest

from src.compliance_check import compliance_review, is_restricted_category


SAFE_BRIEF = {
    "campaign_name": "Safe Community Campaign",
    "brand_name": "Example Brand",
    "business_type": "Community",
    "product_or_service": "Weekly wellness community event",
    "target_region": "Malaysia",
    "target_audience_context": "People interested in beginner-friendly wellness events",
    "campaign_objective": "Awareness",
    "funnel_stage": "Awareness",
    "offer": "Join next community session",
    "landing_page": "https://example.com",
    "tone_of_voice": "friendly and professional",
    "proof_points": "Beginner-friendly, supportive group",
    "disclaimers": "No guaranteed health results",
    "restricted_category_check": "No",
    "forbidden_words": "guaranteed, instant, miracle",
    "desired_cta": "Learn More",
}


class ComplianceCheckTests(unittest.TestCase):
    def test_safe_item_remains_approved_draft_not_final_approved(self):
        review = compliance_review(
            {
                "primary_text": "Explore beginner-friendly wellness community events.",
                "headline": "Join a Supportive Session",
                "description": "Learn more about the next community activity.",
                "creative_prompt": "Authentic community event image.",
            },
            SAFE_BRIEF,
        )

        self.assertEqual(review.final_status, "APPROVED_DRAFT")
        self.assertEqual(review.risk_level, "LOW")

    def test_personal_attribute_copy_needs_review(self):
        review = compliance_review(
            {
                "primary_text": "Are you overweight? Join this session today.",
                "headline": "Wellness Session",
            },
            SAFE_BRIEF,
        )

        self.assertEqual(review.final_status, "REVIEW_NEEDED")
        self.assertEqual(review.risk_level, "HIGH")

    def test_forbidden_claim_needs_review(self):
        review = compliance_review(
            {
                "primary_text": "Get instant results with this miracle session.",
                "headline": "Wellness Session",
            },
            SAFE_BRIEF,
        )

        self.assertEqual(review.final_status, "REVIEW_NEEDED")
        self.assertEqual(review.issue_category, "Misleading Claims")

    def test_sensitive_category_requires_policy_review(self):
        brief = dict(SAFE_BRIEF)
        brief["product_or_service"] = "Financial planning consultation"
        brief["restricted_category_check"] = "Yes"

        self.assertTrue(is_restricted_category(brief))

        review = compliance_review({"primary_text": "Explore planning options."}, brief)

        self.assertEqual(review.final_status, "POLICY_REVIEW_REQUIRED")
        self.assertEqual(review.risk_level, "HIGH")

    def test_gambling_category_is_blocked(self):
        brief = dict(SAFE_BRIEF)
        brief["product_or_service"] = "Casino bonus"
        brief["restricted_category_check"] = "Yes"

        review = compliance_review({"primary_text": "Explore the offer."}, brief)

        self.assertEqual(review.final_status, "BLOCKED")
        self.assertEqual(review.risk_level, "BLOCKED")


if __name__ == "__main__":
    unittest.main()
