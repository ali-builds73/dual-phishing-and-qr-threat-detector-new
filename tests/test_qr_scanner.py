import unittest
from core.qr_scanner import extract_url_and_domain

# These tests only inspect text. They do not need a real image or internet access.
class QrScannerTests(unittest.TestCase):
    def test_extracts_https_domain(self):
        url, domain = extract_url_and_domain("https://login.example.com/path?q=1")
        self.assertEqual(url, "https://login.example.com/path?q=1")
        self.assertEqual(domain, "login.example.com")

    def test_does_not_treat_plain_text_as_url(self):
        self.assertEqual(extract_url_and_domain("Wi-Fi password: demo"), (None, None))
