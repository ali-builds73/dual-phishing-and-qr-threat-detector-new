import unittest
from core.risk_scorer import score_domain

# The scorer can be tested with made-up facts, so it never contacts the internet.
class RiskScorerTests(unittest.TestCase):
    def test_homoglyph_of_a_live_new_domain_is_high_priority(self):
        result = score_domain("pаypal.com", "paypal.com", "homoglyph", True, ["192.0.2.10"], {"age_in_days": 2, "has_mx": True})
        self.assertGreaterEqual(result["score"], 80)
        self.assertEqual(result["verdict"], "Critical")

    def test_unregistered_candidate_has_lower_exposure_score(self):
        result = score_domain("paypl.com", "paypal.com", "omission", False)
        self.assertLess(result["score"], 80)
        self.assertFalse(result["registered"])
