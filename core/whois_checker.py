"""Get registration clues from RDAP, the modern replacement for WHOIS.

Old WHOIS servers often reject automated requests. RDAP returns the same useful
information as structured JSON, which is easier and more reliable to read.
"""
# json turns the text returned by an RDAP server into a normal Python dictionary.
import json
# datetime lets us calculate the age of a domain in days.
from datetime import datetime, timezone
from http.client import RemoteDisconnected
# urllib is included with Python. It makes the HTTPS request to the RDAP service.
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
# dnspython is also used here to check for an email (MX) record.
import dns.resolver
# Reuse the Unicode-to-ASCII helper instead of writing it a second time.
from core.dns_checker import to_idna

def has_mx_record(domain):
    """An MX record means the domain is set up to receive email."""
    try:
        # "MX" means mail exchange: a server that receives email for a domain.
        dns.resolver.resolve(to_idna(domain), "MX")
        return True
    except Exception:
        return False

def find_registration_date(rdap_data):
    """Find the date on which the RDAP server says the domain was registered."""
    for event in rdap_data.get("events", []):
        if event.get("eventAction") == "registration":
            return event.get("eventDate")
    return None


def find_registrar(rdap_data):
    """Find the registrar name inside RDAP's nested entity list."""
    for entity in rdap_data.get("entities", []):
        if "registrar" not in entity.get("roles", []):
            continue
        # vcardArray is the standard RDAP location for contact information.
        vcard = entity.get("vcardArray", [[], []])
        for field in vcard[1]:
            if field[0] == "fn":  # "fn" means formatted name.
                return field[3]
    return None


def rdap_urls(domain):
    """Return RDAP services to try, starting with official .com/.net services."""
    tld = domain.rsplit(".", 1)[-1].lower()
    # Verisign runs the official RDAP servers for .com and .net names.
    if tld == "com":
        return ["https://rdap.verisign.com/com/v1/domain/" + to_idna(domain),
                "https://rdap.org/domain/" + to_idna(domain)]
    if tld == "net":
        return ["https://rdap.verisign.com/net/v1/domain/" + to_idna(domain),
                "https://rdap.org/domain/" + to_idna(domain)]
    # rdap.org directs other extensions to their official RDAP registry.
    return ["https://rdap.org/domain/" + to_idna(domain)]


def fetch_whois(domain):
    """Get domain age and registrar using RDAP, plus its MX-record status."""
    # Begin with empty values. None means "the service did not provide this".
    info = {"age_in_days": None, "registrar": None, "has_mx": has_mx_record(domain),
            "rdap_available": False}

    # Try each service. If one server closes the connection, move to the next
    # service instead of ending the complete domain scan.
    for url in rdap_urls(domain):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 BeginnerPhishingDetector"})
            with urlopen(request, timeout=10) as response:
                rdap_data = json.load(response)
            date_text = find_registration_date(rdap_data)
            if date_text:
                # RDAP dates use a trailing Z for UTC. Python understands +00:00.
                created = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
                info["age_in_days"] = (datetime.now(timezone.utc) - created).days
            info["registrar"] = find_registrar(rdap_data)
            info["rdap_available"] = True
            break
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError,
                RemoteDisconnected, OSError):
            # Network services can rate-limit or close a connection. Try fallback.
            continue
    return info
