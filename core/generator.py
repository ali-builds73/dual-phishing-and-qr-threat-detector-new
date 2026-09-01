"""Create simple domain look-alikes for defensive checks."""

from config import COMBO_WORDS, COMMON_TLDS, KEYBOARD_NEIGHBOURS, SQUAT_DOMAINS
from core.homoglyphs import HOMOGLYPHS

def normalise_domain(domain):
    """Remove a URL prefix/path, then return a clean lowercase domain."""
    domain = domain.strip().lower()
    domain = domain.replace("https://", "").replace("http://", "")
    domain = domain.split("/")[0].rstrip(".")
    if "." not in domain or " " in domain:
        raise ValueError("Please enter a domain like example.com")
    return domain

def add_variant(variants, domain, kind):
    """Add a result once. A dictionary makes duplicate removal easy."""
    if domain not in variants:
        variants[domain] = {"domain": domain, "type": kind}

def generate_all_variants(domain):
    """Return a list of possible look-alike domains and their type."""
    domain = normalise_domain(domain)
    name, tld = domain.rsplit(".", 1)
    variants = {}

    # Remove one character: paypal -> paypl
    for i in range(len(name)):
        if len(name) > 1:
            add_variant(variants, name[:i] + name[i + 1:] + "." + tld, "omission")

    # Repeat one character: paypal -> paypall
    for i in range(len(name)):
        add_variant(variants, name[:i] + name[i] + name[i:] + "." + tld, "repetition")

    # Swap neighbours: paypal -> payapl
    for i in range(len(name) - 1):
        swapped = name[:i] + name[i + 1] + name[i] + name[i + 2:]
        add_variant(variants, swapped + "." + tld, "transposition")

    # Replace a key with a nearby QWERTY key.
    for i, letter in enumerate(name):
        for nearby_key in KEYBOARD_NEIGHBOURS.get(letter, ""):
            changed = name[:i] + nearby_key + name[i + 1:]
            add_variant(variants, changed + "." + tld, "substitution")

    # Replace one letter with a character that can look the same.
    for i, letter in enumerate(name):
        if letter in HOMOGLYPHS:
            changed = name[:i] + HOMOGLYPHS[letter] + name[i + 1:]
            add_variant(variants, changed + "." + tld, "homoglyph")

    # Try the same name with other common top-level domains.
    for new_tld in COMMON_TLDS:
        if new_tld != tld:
            add_variant(variants, name + "." + new_tld, "tld_swap")

    # Put a hyphen between two letters.
    for i in range(1, len(name)):
        add_variant(variants, name[:i] + "-" + name[i:] + "." + tld, "hyphenation")

    # Add words that are often used in deceptive login links.
    for word in COMBO_WORDS:
        add_variant(variants, name + "-" + word + "." + tld, "combosquat")
        add_variant(variants, word + "-" + name + "." + tld, "combosquat")

    # The trusted name appears first, but the final domain is the real owner.
    for fake_host in SQUAT_DOMAINS:
        add_variant(variants, domain + "." + fake_host, "subdomain_squat")

    # Flip one bit in each character. Keep only normal domain characters.
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
    for i, letter in enumerate(name):
        for bit in range(8):
            changed_letter = chr(ord(letter) ^ (1 << bit))
            if changed_letter in allowed:
                changed = name[:i] + changed_letter + name[i + 1:]
                add_variant(variants, changed + "." + tld, "bitflip")

    return list(variants.values())
