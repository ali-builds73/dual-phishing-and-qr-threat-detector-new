"""Create safe QR-code images for a classroom demonstration.

The URL uses the reserved .invalid top-level domain. It cannot point to a real
website, and the main program will only read the QR code; it will not open it.
"""

import argparse
from pathlib import Path

# This is deliberately a fake login-looking URL. It is close to example.com,
# but .invalid is reserved for examples and cannot resolve on the public internet.
DEMO_URL = "https://exampl3.invalid/login"


def get_arguments():
    """Let the user choose a URL and output name without editing this file."""
    parser = argparse.ArgumentParser(description="Create a QR-code image.")
    parser.add_argument("--url", default=DEMO_URL, help="URL to place inside the QR code")
    parser.add_argument("--output", default="samples/demo_qr.png", help="PNG file to create")
    return parser.parse_args()


def main():
    arguments = get_arguments()
    # qrcode is installed from requirements.txt with the other Python packages.
    import qrcode

    # Make a black-and-white QR image that contains the safe demonstration URL.
    image = qrcode.make(arguments.url)

    # Save beside this file so the main program can find it easily.
    output_file = Path(arguments.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_file)
    print(f"Created: {output_file}")
    print(f"QR code contains: {arguments.url}")


if __name__ == "__main__":
    main()
