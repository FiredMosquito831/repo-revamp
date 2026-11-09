#!/usr/bin/env python3
"""Verify a revamped site: live or local.

Checks, in order:
  1. HTTP -> HTTPS redirect (live only)
  2. the root returns 200
  3. og.png returns 200 and is exactly 1200x630
  4. robots.txt returns 200 and references the sitemap
  5. every URL in sitemap.xml returns 200
  6. every internal link on every page resolves (local only, optional)

Standard library only. No network calls in --local mode.

Usage:
  python verify_site.py --base-url https://example.com
  python verify_site.py --local-dir docs --base-url https://example.com
  python verify_site.py --base-url https://example.com --json out.json

Exit code 0 only when every check passes.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse

USER_AGENT = "repo-revamp-verify/1.0"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Return the redirect response instead of following it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url: str, timeout: float = 20.0, follow: bool = True) -> tuple[int, bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)
    except urllib.error.URLError as error:
        return 0, str(error).encode(), {}


def png_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def sitemap_urls(base: str, timeout: float) -> tuple[list[str], str]:
    status, body, _ = fetch(urljoin(base, "/sitemap.xml"), timeout)
    if status != 200:
        return [], f"sitemap.xml returned {status}"
    try:
        root = ET.fromstring(body)
    except ET.ParseError as error:
        return [], f"sitemap.xml does not parse: {error}"
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [element.text.strip() for element in root.findall(".//s:loc", namespace) if element.text]
    if not urls:
        urls = [element.text.strip() for element in root.findall(".//loc") if element.text]
    return urls, ""


def check_live(base: str, timeout: float, results: list[dict]) -> None:
    parsed = urlparse(base)
    if parsed.scheme == "https":
        http_url = f"http://{parsed.netloc}/"
        status, _, headers = fetch(http_url, timeout, follow=False)
        location = headers.get("Location", "")
        ok = status in (301, 302, 307, 308) and location.startswith("https://")
        results.append({
            "check": "http_to_https",
            "target": http_url,
            "status": status,
            "ok": ok,
            "detail": location or "no redirect",
        })

    status, _, _ = fetch(base, timeout)
    results.append({"check": "root", "target": base, "status": status, "ok": status == 200})

    og_url = urljoin(base, "/og.png")
    status, body, _ = fetch(og_url, timeout)
    size = png_size(body) if status == 200 else None
    results.append({
        "check": "og_image",
        "target": og_url,
        "status": status,
        "ok": status == 200 and size == (1200, 630),
        "detail": f"{size[0]}x{size[1]}" if size else "not a PNG or not fetched",
    })

    robots_url = urljoin(base, "/robots.txt")
    status, body, _ = fetch(robots_url, timeout)
    text = body.decode("utf-8", "replace")
    results.append({
        "check": "robots",
        "target": robots_url,
        "status": status,
        "ok": status == 200 and "Sitemap:" in text,
        "detail": "references a sitemap" if "Sitemap:" in text else "no Sitemap line",
    })

    urls, error = sitemap_urls(base, timeout)
    if error:
        results.append({"check": "sitemap", "target": urljoin(base, "/sitemap.xml"),
                        "status": 0, "ok": False, "detail": error})
        return

    results.append({"check": "sitemap", "target": urljoin(base, "/sitemap.xml"),
                    "status": 200, "ok": True, "detail": f"{len(urls)} URLs"})

    for url in urls:
        status, _, _ = fetch(url, timeout)
        results.append({"check": "sitemap_url", "target": url, "status": status, "ok": status == 200})
        time.sleep(0.05)


def check_local(directory: Path, base: str, results: list[dict]) -> None:
    index = directory / "index.html"
    results.append({"check": "local_index", "target": str(index),
                    "status": 200 if index.is_file() else 0, "ok": index.is_file()})

    og = directory / "og.png"
    size = png_size(og.read_bytes()) if og.is_file() else None
    results.append({"check": "local_og", "target": str(og),
                    "status": 200 if og.is_file() else 0,
                    "ok": size == (1200, 630),
                    "detail": f"{size[0]}x{size[1]}" if size else "missing or not a PNG"})

    sitemap = directory / "sitemap.xml"
    if sitemap.is_file():
        try:
            root = ET.fromstring(sitemap.read_bytes())
            namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [e.text.strip() for e in root.findall(".//s:loc", namespace) if e.text]
            if not locs:
                locs = [e.text.strip() for e in root.findall(".//loc") if e.text]
            missing = []
            for loc in locs:
                path = urlparse(loc).path
                target = directory / path.lstrip("/")
                if path.endswith("/"):
                    target = target / "index.html"
                if not target.is_file():
                    missing.append(loc)
            results.append({"check": "local_sitemap", "target": str(sitemap),
                            "status": 200, "ok": not missing,
                            "detail": f"{len(locs)} URLs, {len(missing)} missing" +
                                      (f": {missing[:5]}" if missing else "")})
        except ET.ParseError as error:
            results.append({"check": "local_sitemap", "target": str(sitemap),
                            "status": 0, "ok": False, "detail": f"parse error: {error}"})
    else:
        results.append({"check": "local_sitemap", "target": str(sitemap),
                        "status": 0, "ok": False, "detail": "missing"})

    link_re = re.compile(r'(?:href|src)="([^"]+)"')
    broken: list[str] = []
    pages = sorted(directory.rglob("*.html"))
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for raw in link_re.findall(text):
            if raw.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
                continue
            parsed = urlparse(raw)
            if parsed.scheme in ("http", "https") or raw.startswith("//"):
                continue
            target = (page.parent / parsed.path).resolve()
            if parsed.path.endswith("/") or parsed.path == "":
                target = target / "index.html"
            if not target.is_file():
                broken.append(f"{page.relative_to(directory)} -> {raw}")
    results.append({"check": "local_links", "target": str(directory),
                    "status": 200, "ok": not broken,
                    "detail": f"{len(pages)} pages, {len(broken)} broken" +
                              (f": {broken[:5]}" if broken else "")})


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a revamped site.")
    parser.add_argument("--base-url", required=True, help="the site's canonical URL")
    parser.add_argument("--local-dir", help="also check a local docs/ directory")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--json", help="write the results as JSON to this path")
    parser.add_argument("--skip-live", action="store_true", help="local checks only")
    args = parser.parse_args()

    results: list[dict] = []
    if not args.skip_live:
        check_live(args.base_url.rstrip("/") + "/", args.timeout, results)
    if args.local_dir:
        check_local(Path(args.local_dir), args.base_url, results)

    failures = [row for row in results if not row["ok"]]
    for row in results:
        mark = "PASS" if row["ok"] else "FAIL"
        detail = f" - {row['detail']}" if row.get("detail") else ""
        print(f"{mark}  {row['check']:<14} {row['status']:>3}  {row['target']}{detail}")

    print()
    print(f"{len(results) - len(failures)}/{len(results)} checks passed")
    if failures:
        print(f"{len(failures)} FAILED")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
