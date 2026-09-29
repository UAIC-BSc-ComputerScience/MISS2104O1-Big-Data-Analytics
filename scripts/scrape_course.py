#!/usr/bin/env python3
"""Mirror the authenticated UAIC Big Data Analytics course site.

Credentials are read from BDA_USERNAME and BDA_PASSWORD and are never written
to disk. The crawler stays on edu.info.uaic.ro and under /big-data-analytics/.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://edu.info.uaic.ro/big-data-analytics/"
ALLOWED_HOST = "edu.info.uaic.ro"
ALLOWED_PREFIX = "/big-data-analytics/"
OUTPUT_DIR = Path("course-materials")
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"

PAGE_EXTENSIONS = {"", ".html", ".htm", ".php", ".asp", ".aspx"}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


def clean_component(value: str) -> str:
    value = unquote(value)
    value = re.sub(r'[<>:"\\|?*\x00-\x1f]', "_", value)
    value = value.strip().strip(".")
    return value or "_"


def local_path_for(url: str, content_type: str | None = None) -> Path:
    parsed = urlparse(url)
    path = parsed.path

    if path.endswith("/"):
        path += "index.html"

    rel = path.removeprefix(ALLOWED_PREFIX)
    parts = [clean_component(p) for p in rel.split("/") if p]

    if not parts:
        parts = ["index.html"]

    target = OUTPUT_DIR.joinpath(*parts)

    if target.suffix == "" and content_type and "text/html" in content_type:
        target = target.with_suffix(".html")

    if parsed.query:
        digest = hashlib.sha256(parsed.query.encode()).hexdigest()[:10]
        target = target.with_name(f"{target.stem}__q_{digest}{target.suffix}")

    return target


def allowed(url: str) -> bool:
    if url.startswith(SKIP_SCHEMES):
        return False
    parsed = urlparse(url)
    return (
        parsed.scheme in {"http", "https"}
        and parsed.hostname == ALLOWED_HOST
        and parsed.path.startswith(ALLOWED_PREFIX)
    )


def normalize(url: str, base: str) -> str | None:
    absolute = urljoin(base, url)
    absolute, _ = urldefrag(absolute)
    if not allowed(absolute):
        return None
    return absolute


def looks_like_page(url: str, content_type: str | None) -> bool:
    if content_type and "text/html" in content_type:
        return True
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix in PAGE_EXTENSIONS


def main() -> int:
    username = os.environ.get("BDA_USERNAME")
    password = os.environ.get("BDA_PASSWORD")

    if not username or not password:
        print("Missing BDA_USERNAME or BDA_PASSWORD.", file=sys.stderr)
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        "User-Agent": "MISS2104O1-course-mirror/1.0 (educational personal archive)"
    })

    queue: deque[str] = deque([BASE_URL])
    seen: set[str] = set()
    manifest: list[dict[str, object]] = []

    while queue:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)

        print(f"GET {url}")
        try:
            response = session.get(url, timeout=45, allow_redirects=True)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            manifest.append({"url": url, "status": "error", "error": str(exc)})
            continue

        final_url = response.url
        if not allowed(final_url):
            print(f"  SKIP redirect outside course path: {final_url}")
            continue

        content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
        target = local_path_for(final_url, content_type)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(response.content)

        manifest.append({
            "url": final_url,
            "path": target.as_posix(),
            "status_code": response.status_code,
            "content_type": content_type,
            "bytes": len(response.content),
            "sha256": hashlib.sha256(response.content).hexdigest(),
        })
        print(f"  -> {target} ({len(response.content)} bytes)")

        if looks_like_page(final_url, content_type):
            soup = BeautifulSoup(response.content, "html.parser")
            candidates: list[str] = []

            for tag, attr in [
                ("a", "href"),
                ("img", "src"),
                ("script", "src"),
                ("link", "href"),
                ("source", "src"),
                ("video", "src"),
                ("audio", "src"),
                ("iframe", "src"),
            ]:
                for node in soup.find_all(tag):
                    value = node.get(attr)
                    if value:
                        candidates.append(value)

            for candidate in candidates:
                child = normalize(candidate, final_url)
                if child and child not in seen:
                    queue.append(child)

        time.sleep(0.15)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    errors = sum(1 for item in manifest if item.get("status") == "error")
    print(f"\nDownloaded {len(manifest) - errors} resources; {errors} errors.")
    print(f"Manifest: {MANIFEST_PATH}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
