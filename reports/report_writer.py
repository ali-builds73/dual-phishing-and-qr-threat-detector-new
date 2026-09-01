"""Show scan results in the terminal or save them to a file.

This file changes how results look. It does not make any security decisions.
"""
# csv and json are built into Python and create common report file formats.
import csv
import json
# Path lets us create the output folder when it does not exist yet.
from pathlib import Path

def sort_results(results):
    """Put high-scoring results first so they are easiest to review."""
    return sorted(results, key=lambda result: result["score"], reverse=True)

def console_report(results):
    """Print one simple section for every result."""
    results = sort_results(results)
    if not results:
        print("No generated domains currently have an A record.")
        return
    for result in results:
        # Print the important facts one result at a time for easy reading.
        print("-" * 60)
        print(f"Domain:   {result['domain']}")
        print(f"Verdict:  {result['verdict']} ({result['score']}/100)")
        print(f"Similar:  {result['similarity']:.0%}")
        print(f"Type:     {result['type']}")
        if result["decoded_url"]:
            print(f"QR URL:   {result['decoded_url']}")
        print(f"DNS A record: {'Yes' if result['registered'] else 'No'}")
        # These lines appear only when the optional RDAP lookup returned data.
        if result["age_in_days"] is not None:
            print(f"Age:      {result['age_in_days']} days")
        if result["registrar"]:
            print(f"Registrar: {result['registrar']}")
        if not result["rdap_available"]:
            print("RDAP:     Registration details were unavailable for this domain")
        for reason in result["reasons"]:
            print(f"  - {reason}")

def write_json(results, destination):
    """Save the full result dictionaries in a JSON file."""
    # Make folders such as reports/output automatically when needed.
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(sort_results(results), indent=2) + "\n", encoding="utf-8")

def write_csv(results, destination):
    """Save a spreadsheet-friendly CSV file."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    # These are the column names that will appear in Excel or Google Sheets.
    fields = ("domain", "brand", "type", "score", "verdict", "similarity", "decoded_url", "registered", "addresses", "age_in_days", "registrar", "rdap_available", "reasons")
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sort_results(results):
            # Copy the dictionary so we do not change the original scan result.
            row = row.copy()
            # CSV cells need text, so turn lists into one semicolon-separated string.
            for name in ("addresses", "reasons"):
                row[name] = "; ".join(row[name])
            writer.writerow(row)
