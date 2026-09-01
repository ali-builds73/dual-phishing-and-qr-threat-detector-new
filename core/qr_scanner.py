"""Decode a QR image without opening the URL found inside it.

The program reads the QR code's text only. It never opens the URL in a browser.
"""
# Path makes it easy to check whether the image file really exists.
from pathlib import Path
# urlparse separates a URL into parts such as scheme, hostname, and path.
from urllib.parse import urlparse

def extract_url_and_domain(value):
    """Return the full URL and domain, or (None, None) for normal text."""
    # Remove accidental spaces before checking the QR-code text.
    candidate = value.strip()
    parsed = urlparse(candidate)
    # Ignore Wi-Fi passwords, phone numbers, and other QR contents. We only scan web URLs.
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return None, None
    return candidate, parsed.hostname.rstrip(".").lower()


def identify_pattern(decoded_domain, trusted_brand):
    """Name the spelling pattern between a QR domain and a trusted brand."""
    brand_name, brand_tld = trusted_brand.rsplit(".", 1)
    domain_name, domain_tld = decoded_domain.rsplit(".", 1)
    if decoded_domain.startswith(trusted_brand + "."):
        return "subdomain_squat"
    if domain_name == brand_name and domain_tld != brand_tld:
        return "tld_swap"
    if domain_name.replace("-", "") == brand_name and "-" in domain_name:
        return "hyphenation"
    if brand_name in domain_name and domain_name != brand_name:
        return "combosquat"
    if len(domain_name) == len(brand_name):
        different_letters = sum(a != b for a, b in zip(domain_name, brand_name))
        if different_letters == 1:
            return "homoglyph" if not domain_name.isascii() else "substitution"
    if len(domain_name) == len(brand_name) - 1:
        return "omission"
    if len(domain_name) == len(brand_name) + 1:
        return "repetition"
    for index in range(len(brand_name) - 1):
        swapped = brand_name[:index] + brand_name[index + 1] + brand_name[index] + brand_name[index + 2:]
        if domain_name == swapped:
            return "transposition"
    return "unknown"

def decode_qr_image(image_path):
    """Read each QR code in an image and return easy-to-read dictionaries."""
    # Convert a text path into a Path object and make sure it points to a file.
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"QR image not found: {path}")
    try:
        # Pillow opens the image; pyzbar finds QR codes in it.
        from PIL import Image
        from pyzbar.pyzbar import ZBarSymbol, decode
    except ImportError as error:
        raise RuntimeError("QR decoding needs Pillow, pyzbar, and the system zbar shared library.") from error
    # Open the image only while it is being decoded, then close it automatically.
    with Image.open(path) as image:
        symbols = decode(image, symbols=[ZBarSymbol.QRCODE])
    payloads = []
    # One picture can contain several QR codes, so use a loop.
    for symbol in symbols:
        raw = symbol.data.decode("utf-8", errors="replace")
        url, domain = extract_url_and_domain(raw)
        # A dictionary is a simple way to keep all three related pieces of data.
        payloads.append({"raw_value": raw, "url": url, "domain": domain})
    return payloads
