import unittest
from core.generator import generate_all_variants, normalise_domain

# Tests are small automatic checks. They help confirm that later changes do not
# accidentally break beginner examples in generator.py.
class GeneratorTests(unittest.TestCase):
    def test_normalise_domain_removes_scheme_and_path(self):
        self.assertEqual(normalise_domain("https://Example.COM/login"), "example.com")

    def test_all_major_variant_categories_are_present(self):
        # The project brief asks for every one of these generation categories.
        variants = generate_all_variants("paypal.com")
        categories = {variant["type"] for variant in variants}
        expected = {"omission", "repetition", "transposition", "substitution", "homoglyph", "tld_swap", "hyphenation", "combosquat", "subdomain_squat", "bitflip"}
        self.assertTrue(expected.issubset(categories))
        self.assertTrue(any(variant["domain"] == "paypl.com" for variant in variants))

    def test_invalid_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            normalise_domain("not a domain")
