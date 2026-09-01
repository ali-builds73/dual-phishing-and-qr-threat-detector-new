"""Tests for the simple QR-domain pattern names shown in reports."""
import unittest

from core.qr_scanner import identify_pattern


class QrPatternTests(unittest.TestCase):
    def test_detects_single_letter_substitution(self):
        self.assertEqual(identify_pattern("exampl3.invalid", "example.com"), "substitution")

    def test_detects_tld_swap(self):
        self.assertEqual(identify_pattern("example.net", "example.com"), "tld_swap")

    def test_detects_fake_subdomain(self):
        self.assertEqual(identify_pattern("example.com.verify.invalid", "example.com"), "subdomain_squat")
