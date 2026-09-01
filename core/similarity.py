"""Small helpers for comparing two domain names."""
# SequenceMatcher is included with Python, so it needs no extra installation.
from difflib import SequenceMatcher

def similarity_score(first_domain, second_domain):
    """Return 0 to 1. 1 means the strings are exactly the same."""
    # Case should not affect a domain comparison, so make both names lowercase.
    first_domain = first_domain.lower()
    second_domain = second_domain.lower()
    # ratio() returns a decimal from 0.0 (very different) to 1.0 (the same).
    return SequenceMatcher(None, first_domain, second_domain).ratio()
