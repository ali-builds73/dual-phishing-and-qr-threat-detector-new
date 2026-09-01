"""Start the beginner-friendly phishing and QR detector from the terminal."""
import argparse
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import one small job from each file. main.py only connects those jobs together.
from config import DEFAULT_MAX_WORKERS, MAX_RDAP_WORKERS
from core.dns_checker import check_domain, check_registered
from core.generator import generate_all_variants, normalise_domain
from core.qr_scanner import decode_qr_image, identify_pattern
from core.risk_scorer import score_domain
from core.whois_checker import fetch_whois
from reports.report_writer import console_report, write_csv, write_json

def get_arguments():
    """Read the command the user typed in the terminal."""
    # argparse creates the --domain, --qr-image, and other terminal options.
    parser = argparse.ArgumentParser(
        description="Defensively identify suspicious look-alike domains and QR destinations.",
        epilog="A score prioritizes review; it is not proof that a domain is malicious.",
    )
    # The user must choose one starting point: a domain OR a QR-code image.
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--domain", help="Trusted domain to inspect, e.g. example.com")
    source.add_argument("--qr-image", type=Path, help="Image containing one or more QR codes")
    parser.add_argument("--brand", help="Trusted brand domain required for --qr-image")
    parser.add_argument("--format", choices=("console", "json", "csv"), default="console")
    parser.add_argument("--output", type=Path, help="Required for JSON and CSV reports")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS, help="Concurrent DNS/WHOIS workers")
    parser.add_argument("--skip-whois", action="store_true", help="Do not request registration metadata")
    parser.add_argument("--verbose", action="store_true", help="Show processing counts")
    return parser.parse_args()

def turn_domains_into_results(domains, brand, skip_whois):
    """Add optional WHOIS facts and calculate a final score for each domain."""
    registration_info = {}

    if not skip_whois:
        # RDAP is a network request. Run a few requests together so a scan with
        # many live candidates does not take one long wait per domain.
        with ThreadPoolExecutor(max_workers=MAX_RDAP_WORKERS) as executor:
            jobs = {executor.submit(fetch_whois, item["domain"]): item["domain"] for item in domains}
            for job in as_completed(jobs):
                domain = jobs[job]
                registration_info[domain] = job.result()

    results = []
    for item in domains:
        # Use an empty dictionary when RDAP was skipped or had no available data.
        whois_info = registration_info.get(item["domain"], {})
        result = score_domain(item["domain"], brand, item["type"], item["registered"],
                              item["addresses"], whois_info)
        result["decoded_url"] = item.get("decoded_url")
        results.append(result)
    return results

def scan_domain(domain, args):
    """Pipeline A: create look-alikes, find live ones, and score them."""
    brand = normalise_domain(domain)
    candidates = generate_all_variants(brand)
    live = check_registered(candidates, args.max_workers)
    if args.verbose:
        print(f"Generated {len(candidates)} possible look-alikes.")
        print(f"Found {len(live)} with an A record.")
    return turn_domains_into_results(live, brand, args.skip_whois)

def scan_qr(image_path, args):
    """Pipeline B: read a QR image, then compare its web domain to a brand."""
    payloads = decode_qr_image(image_path)
    web_payloads = [payload for payload in payloads if payload["domain"]]
    if not web_payloads:
        raw_values = ", ".join(repr(payload["raw_value"]) for payload in payloads) or "none"
        raise ValueError(f"No HTTP(S) URL was found in the QR image (decoded values: {raw_values}).")
    if not args.brand:
        raise ValueError("--brand is required with --qr-image so the URL can be compared to a trusted domain.")
    brand = normalise_domain(args.brand)
    checked_domains = []
    for payload in web_payloads:
        # Name the QR's look-alike pattern before checking whether it is live.
        pattern = identify_pattern(payload["domain"], brand)
        checked = check_domain({"domain": payload["domain"], "type": pattern})
        # Keep the decoded URL so the report shows what was inside the QR code.
        checked["decoded_url"] = payload["url"]
        checked_domains.append(checked)
    if args.verbose:
        print(f"Decoded {len(payloads)} QR value(s).")
    return turn_domains_into_results(checked_domains, brand, args.skip_whois)

def main():
    # Step 1: read what the user typed.
    args = get_arguments()
    if args.format != "console" and not args.output:
        raise ValueError("--output is required for JSON and CSV reports.")
    if args.max_workers < 1:
        raise ValueError("--max-workers must be at least 1.")
    # Step 2: run exactly one of the two project pipelines.
    results = scan_domain(args.domain, args) if args.domain else scan_qr(args.qr_image, args)
    # Step 3: show the results on screen or save them in the requested format.
    if args.format == "console":
        console_report(results)
    elif args.format == "json":
        write_json(results, args.output)
        print(f"Wrote JSON report to {args.output}")
    else:
        write_csv(results, args.output)
        print(f"Wrote CSV report to {args.output}")
    return 0

if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2)
