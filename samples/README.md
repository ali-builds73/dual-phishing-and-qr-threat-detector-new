# QR sample images

These images are safe demonstrations. Each QR code contains a `.invalid` URL,
which cannot lead to a real public website.

| Image file | Pattern the scanner should report |
| --- | --- |
| `qr_substitution.png` | substitution |
| `qr_tld_swap.png` | tld_swap |
| `qr_hyphenation.png` | hyphenation |
| `qr_combosquat.png` | combosquat |
| `qr_subdomain_squat.png` | subdomain_squat |
| `qr_transposition.png` | transposition |

Scan any image with this command:

```bash
python main.py --qr-image samples/qr_substitution.png --brand example.com --skip-whois --verbose
```

Replace `qr_substitution.png` with the sample you want to scan.
