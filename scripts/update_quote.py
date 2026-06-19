#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
THEME = "tokyonight"

START = "<!-- QUOTE:START"
END = "<!-- QUOTE:END -->"

FALLBACK = ("Imagination is more important than knowledge.", "Albert Einstein")


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_quote():
    try:
        data = _get("https://zenquotes.io/api/random")
        return data[0]["q"].strip(), data[0]["a"].strip()
    except Exception as e:
        print(f"zenquotes failed: {e}", file=sys.stderr)
    try:
        data = _get("https://dummyjson.com/quotes/random")
        return data["quote"].strip(), data["author"].strip()
    except Exception as e:
        print(f"dummyjson failed: {e}", file=sys.stderr)
    print("using fallback quote", file=sys.stderr)
    return FALLBACK


def build_block(quote, author):
    q = urllib.parse.quote(quote)
    a = urllib.parse.quote(author)
    url = (
        f"https://readme-daily-quotes.vercel.app/api"
        f"?type=horizontal&theme={THEME}&quote={q}&author={a}"
    )
    return (
        f'{START} — updated daily by .github/workflows/quote.yml '
        f'(do not edit between the markers) -->\n'
        f'<p align="center">\n'
        f'  <img src="{url}" alt="thought of the day" />\n'
        f'</p>\n'
        f'{END}'
    )


def main():
    quote, author = fetch_quote()
    print(f'Quote: "{quote}" — {author}')

    with open(README, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(content):
        print("ERROR: QUOTE markers not found in README.md", file=sys.stderr)
        sys.exit(1)

    new_content = pattern.sub(lambda _: build_block(quote, author), content)

    if new_content == content:
        print("No change.")
        return

    with open(README, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README.md updated.")


if __name__ == "__main__":
    main()
