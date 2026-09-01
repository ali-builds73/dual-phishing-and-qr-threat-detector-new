"""Turn simple facts about a domain into an easy-to-explain risk result."""
from config import CATEGORY_POINTS
from core.similarity import similarity_score

def get_label(score):
    """Translate a number into a simple word for the report."""
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"

def score_domain(domain, brand, kind, registered, addresses=None, whois_info=None):
    """Create one result dictionary and explain how its score was calculated."""
    addresses = addresses or []
    whois_info = whois_info or {}
    similarity = similarity_score(domain, brand)

    # Similar names start with more points. The other checks add points below.
    score = round(similarity * 40)
    reasons = [f"Name similarity to {brand}: {similarity:.0%}"]
    points = CATEGORY_POINTS.get(kind, 0)
    score += points
    reasons.append(f"Look-alike type: {kind.replace('_', ' ')} (+{points})")

    if registered:
        score += 20
        reasons.append("The domain has an A record (+20)")
    else:
        # An inactive domain is not a live website right now.
        score = min(score, 34)
        reasons.append("No A record found (not treated as an active website)")
    if whois_info.get("age_in_days") is not None and whois_info["age_in_days"] < 30:
        score += 15
        reasons.append("The domain is less than 30 days old (+15)")
    if whois_info.get("has_mx"):
        score += 5
        reasons.append("The domain has email (MX) records (+5)")

    score = min(score, 100)
    return {
        "domain": domain, "brand": brand, "type": kind, "registered": registered,
        "addresses": addresses, "similarity": round(similarity, 2), "score": score,
        "verdict": get_label(score), "age_in_days": whois_info.get("age_in_days"),
        "registrar": whois_info.get("registrar"),
        "rdap_available": whois_info.get("rdap_available", False), "decoded_url": None,
        "reasons": reasons,
    }
