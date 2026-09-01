# Dual Phishing and QR Threat Detector

A beginner-friendly command-line project that checks two common phishing risks:

- **Domain scan:** creates common look-alike versions of a trusted domain, checks which names have an IP address, then gives each live result a simple score.
- **QR scan:** reads a QR-code image, finds the web address inside it, and compares that address with a trusted brand domain.

The tool does not open decoded URLs or generated domains. A verdict is an explainable triage signal, **not evidence that a domain is malicious**. Confirm findings through your organisation's approved threat-intelligence and incident-response process.

## Features

- Omission, repetition, transposition, keyboard-adjacent, homoglyph/IDN, TLD, hyphenation, combosquat, subdomain-squat, and bit-flip candidates
- IDNA/punycode-safe concurrent DNS checks
- Best-effort RDAP registration age, registrar, and MX enrichment
- Simple text-similarity scoring with an explanation of every score
- QR decoding without visiting its destination
- Console, JSON, and CSV reports

## Setup

Use Python 3.10 or newer.

On Debian/Ubuntu, install the virtual-environment support first if it is not
already present:

```bash
sudo apt install python3-venv
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`pyzbar` also needs the system ZBar library. On Debian/Ubuntu use `sudo apt install libzbar0`; on macOS use `brew install zbar`.

## Usage

```bash
# Inspect registered look-alikes of a trusted domain.
python main.py --domain example.com --verbose

# Export findings.
python main.py --domain example.com --format csv --output reports/output/example.csv
python main.py --domain example.com --format json --output reports/output/example.json --skip-whois

# Inspect a QR image against a known trusted brand.
python main.py --qr-image samples/code.png --brand example.com
```

`--skip-whois` avoids registration-data requests. `--max-workers` controls concurrent DNS/WHOIS requests.

## Safe classroom QR demonstration

Create the included sample QR image, then scan it. The image contains a fake
`.invalid` URL, so it is safe for a presentation and does not lead to a real site.

```bash
python samples/create_demo_qr.py
python main.py --qr-image samples/demo_qr.png --brand example.com --skip-whois --verbose
```

Create your own QR image, then scan and check it against a brand:

```bash
python samples/create_demo_qr.py --url "https://exampl3.invalid/login" --output samples/my_qr.png
python main.py --qr-image samples/my_qr.png --brand example.com --skip-whois --verbose
```

Six ready-made, safe QR examples are in `samples/`. See `samples/README.md` for
the file names and the pattern each one demonstrates.

## Read the code in this order

1. Start with `main.py`. It only decides whether you are scanning a domain or a QR image.
2. Read `core/generator.py` to see the small loops that make look-alike domains.
3. Read `core/dns_checker.py` to see how a generated name is checked.
4. Read `core/risk_scorer.py` to see exactly how points and labels are assigned.

The program uses normal Python lists and dictionaries. Each file has comments above the important steps, so you can change one part and see what it does.

## Layout

```text
main.py                   CLI orchestration
config.py                 Thresholds, weights, and data lists
core/generator.py         Look-alike candidate generation
core/homoglyphs.py        Unicode confusable mappings
core/dns_checker.py       Concurrent IDNA-aware DNS checks
core/whois_checker.py     Best-effort WHOIS and MX enrichment
core/similarity.py        Visual normalisation and edit-distance scoring
core/risk_scorer.py       Shared explainable decision engine
core/qr_scanner.py        Local QR decoding and URL extraction
reports/report_writer.py  Console, JSON, and CSV formatting
tests/                    Offline unit tests
```

## Tests

Tests are offline: they do not make DNS, WHOIS, or HTTP requests.

```bash
python -m unittest discover -s tests -v
```
