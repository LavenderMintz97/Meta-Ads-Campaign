import unittest

from src.approval_guard import check_row_approval


APPROVED_ROW = {
    "compliance_status": "APPROVED_DRAFT",
    "risk_level": "LOW",
    "human_approval": "YES",
    "landing_page_checked": "YES",
}


class ApprovalGuardYesValueTests(unittest.TestCase):
    def test_human_approval_must_be_literal_yes(self):
        row = dict(APPROVED_ROW, human_approval="TRUE")

        decision = check_row_approval(row)

        self.assertFalse(decision.can_continue)
        self.assertEqual(decision.reason, "human_approval must be YES.")

    def test_landing_page_checked_must_be_literal_yes(self):
        row = dict(APPROVED_ROW, landing_page_checked="1")

        decision = check_row_approval(row)

        self.assertFalse(decision.can_continue)
        self.assertEqual(decision.reason, "landing_page_checked must be YES.")


if __name__ == "__main__":
    unittest.main()
