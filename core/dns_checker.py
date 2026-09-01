"""Check which generated names currently have an IP address.

DNS is like the internet's phone book: it converts a name such as example.com
into an IP address. A domain with no A record is not an active web destination.
"""
# ThreadPoolExecutor lets several DNS checks happen at the same time. You do not
# need to understand threads yet; it simply makes a scan finish sooner.
from concurrent.futures import ThreadPoolExecutor, as_completed
# dnspython is the external library that performs DNS lookups.
import dns.exception
import dns.resolver
# These settings live in config.py so they are easy to change in one place.
from config import DEFAULT_MAX_WORKERS, DNS_TIMEOUT_SECONDS

def to_idna(domain):
    """DNS expects ASCII. This converts Unicode look-alikes to punycode."""
    return domain.encode("idna").decode("ascii")

def check_domain(variant):
    """Check one candidate and return the original dictionary with DNS facts."""
    # Make a resolver object. It knows which DNS server to ask.
    resolver = dns.resolver.Resolver(configure=True)
    resolver.timeout = DNS_TIMEOUT_SECONDS
    # Give one lookup at most the same short amount of time as its timeout.
    resolver.lifetime = DNS_TIMEOUT_SECONDS
    try:
        # "A" means: ask for the IPv4 address of this domain.
        answers = resolver.resolve(to_idna(variant["domain"]), "A")
        # Store the answer inside the same dictionary that came from generator.py.
        variant["registered"] = True
        variant["addresses"] = [str(answer) for answer in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        variant["registered"] = False
        variant["addresses"] = []
    except (dns.resolver.NoNameservers, dns.exception.Timeout, UnicodeError):
        # A timeout is not proof that a domain is bad. Treat it as unavailable.
        variant["registered"] = False
        variant["addresses"] = []
    return variant

def check_registered(variants, max_workers=DEFAULT_MAX_WORKERS):
    """Check many names at once, then return only names that resolved."""
    # Only names with an A record are kept in this list.
    live = []
    with ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
        # Start one check for every generated domain.
        futures = [executor.submit(check_domain, item) for item in variants]
        # Handle a result each time one check finishes.
        for future in as_completed(futures):
            result = future.result()
            if result["registered"]:
                live.append(result)
    return live
