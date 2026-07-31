#!/usr/bin/env python3
"""Inline the woff2 fonts into src/index.template.html and write index.html.

The published page has to be a single self-contained file: artifact hosting
blocks requests to font CDNs, and a silent fallback would lose the woodtype
wordmark the whole design rests on.
"""

import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
TEMPLATE = ROOT / "src" / "index.template.html"
OUTPUT = ROOT / "index.html"
# Artifact hosting supplies its own document skeleton, so that build gets the
# stylesheet plus the body contents and nothing else. Not committed.
FRAGMENT = ROOT / "dist" / "artifact.html"

FONTS = {
    "__BEVAN_400__": "fonts/bevan-400.woff2",
    "__COURIER_400__": "fonts/courier-prime-400.woff2",
    "__COURIER_700__": "fonts/courier-prime-700.woff2",
}


def main() -> int:
    html = TEMPLATE.read_text(encoding="utf-8")

    for token, relative in FONTS.items():
        path = ROOT / relative
        if not path.exists():
            print(f"missing font: {relative}", file=sys.stderr)
            return 1
        if token not in html:
            print(f"template has no slot for {token}", file=sys.stderr)
            return 1
        html = html.replace(token, base64.b64encode(path.read_bytes()).decode("ascii"))

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUTPUT.name} ({OUTPUT.stat().st_size / 1024:.0f} KB)")

    style = re.search(r"<style>.*?</style>", html, re.S)
    body = re.search(r"<body>(.*)</body>", html, re.S)
    if not style or not body:
        print("could not locate <style> and <body> to build the fragment", file=sys.stderr)
        return 1
    FRAGMENT.parent.mkdir(exist_ok=True)
    FRAGMENT.write_text(style.group(0) + "\n" + body.group(1).strip() + "\n", encoding="utf-8")
    print(f"wrote {FRAGMENT.relative_to(ROOT)} ({FRAGMENT.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
