"""Settings used by the program.

Change values here when you want to adjust what the program creates or how it
labels a result. Keeping these values in one file makes the other files easier
to read.
"""

DNS_TIMEOUT_SECONDS = 2
DEFAULT_MAX_WORKERS = 20
# RDAP is slower than DNS. Eight requests at once is fast without being excessive.
MAX_RDAP_WORKERS = 8

# Each key maps to nearby keys on a regular QWERTY keyboard.
KEYBOARD_NEIGHBOURS = {
    "a": "qwsz", "b": "vghn", "c": "xdfv", "d": "ersfcx", "e": "rdsw", "f": "rtgdvc",
    "g": "tyfhvb", "h": "yugjbn", "i": "uokj", "j": "uikhmn", "k": "ijolm", "l": "kop",
    "m": "njk", "n": "bhjm", "o": "iplk", "p": "ol", "q": "wa", "r": "etfd", "s": "wedxza",
    "t": "rygf", "u": "yihj", "v": "cfgb", "w": "qase", "x": "zsdc", "y": "tugh", "z": "asx",
}
# Top-level domains to try when making simple TLD-swap examples.
COMMON_TLDS = ("com", "net", "org", "co", "io", "info", "biz", "app", "xyz")
# Extra words often added to login-looking URLs.
COMBO_WORDS = ("secure", "login", "verify", "account", "support", "auth", "update")
# These hosts demonstrate that the final domain name—not the first words—is important.
SQUAT_DOMAINS = ("verify-account.xyz", "secure-login.top", "account-check.info")

# A higher number means that kind of look-alike deserves more attention.
CATEGORY_POINTS = {
    "homoglyph": 25, "bitflip": 18, "subdomain_squat": 18, "omission": 15,
    "repetition": 15, "transposition": 15, "substitution": 14, "hyphenation": 10,
    "tld_swap": 8, "combosquat": 8, "unknown": 0,
}
