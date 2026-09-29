#!/usr/bin/env python3
"""Download active same-site PDF links from the UAIC BDA course page for personal study."""
import argparse
import getpass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, build_opener

BASE = "https://edu.info.uaic.ro/big-data-analytics/"
OUTPUT = Path("materials")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list active PDF links only")
    args = parser.parse_args()
    username = input("Course username: ")
    password = getpass.getpass("Course password: ")
    manager = HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, BASE, username, password)
    opener = build_opener(HTTPBasicAuthHandler(manager))
    with opener.open(BASE, timeout=30) as response:
        source = response.read().decode("utf-8", errors="replace")
    links = Links()
    links.feed(source)
    pdfs = []
    for href in links.hrefs:
        url = urljoin(BASE, href)
        parsed = urlsplit(url)
        if parsed.netloc != urlsplit(BASE).netloc or not parsed.path.lower().endswith(".pdf"):
            continue
        if not parsed.path.startswith(urlsplit(BASE).path):
            continue
        relative = unquote(parsed.path[len(urlsplit(BASE).path):])
        target = Path(relative)
        if target.is_absolute() or ".." in target.parts:
            continue
        if (url, target) not in pdfs:
            pdfs.append((url, target))
    for url, target in pdfs:
        if args.list:
            print(f"{target}: {url}")
            continue
        destination = OUTPUT / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with opener.open(url, timeout=60) as response:
                content = response.read()
            if not content.startswith(b"%PDF"):
                raise ValueError("response is not a PDF")
            destination.write_bytes(content)
            print(f"Saved {destination} ({len(content)} bytes)")
        except Exception as exc:
            print(f"FAILED {url}: {exc}")
    print(f"{len(pdfs)} active PDFs found.")


if __name__ == "__main__":
    main()
