#!/usr/bin/env python3
"""Add canonical links and a curated sitemap to a static GitHub Pages build.

SITE_URL must be the *currently deployed* URL, not an unapproved future domain.
The site root can be a project path (/repo/) or a domain root (/).
"""
import argparse
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

CANONICAL = re.compile(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>\s*', re.I)


def normalized_site_url(value):
    parsed = urlsplit(value.strip())
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment
            or "//" in parsed.path):
        raise ValueError("SITE_URL must be a plain HTTPS origin with optional base path")
    return value.strip().rstrip("/") + "/"


def build(root, site_url):
    root = Path(root)
    base = normalized_site_url(site_url)
    listed_pages = [
        root / "index.html",
        root / "fuel" / "index.html",
        root / "purchase" / "index.html",
    ] + sorted((root / "vehicles").glob("*/index.html"))
    if not (root / "data" / "vehicle-details.json").is_file():
        raise FileNotFoundError("Missing verified vehicle detail index")
    detail_ids = {
        x["id"] for x in json.loads(
            (root / "data" / "vehicle-details.json").read_text(encoding="utf-8")
        )
    }
    sitemap_urls = []
    for page in listed_pages:
        if not page.is_file():
            raise FileNotFoundError(page)
        parent = page.parent.relative_to(root).as_posix()
        relative_url = "" if parent == "." else parent + "/"
        absolute_url = base + relative_url
        source = page.read_text(encoding="utf-8")
        if not re.search(r"</head\s*>", source, flags=re.I):
            raise ValueError(f"{page}: missing </head>")
        source = CANONICAL.sub("", source)
        canonical = '<link rel="canonical" href="' + html.escape(absolute_url, quote=True) + '">'
        source = re.sub(r"</head\s*>", "  " + canonical + "\n</head>", source, count=1, flags=re.I)
        page.write_text(source, encoding="utf-8")
        # Sitemap contains substantive pages only, not empty purchase/fuel feeds
        # or placeholder vehicle pages awaiting details.
        if parent == "." or (parent.startswith("vehicles/") and parent.split("/")[-1] in detail_ids):
            sitemap_urls.append(absolute_url)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines.extend("  <url><loc>" + html.escape(u, quote=True) + "</loc></url>" for u in sitemap_urls)
    lines.append("</urlset>")
    (root / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"SEO metadata: canonical={len(listed_pages)} sitemap={len(sitemap_urls)} base={base}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--site-url", default=os.environ.get("SITE_URL"))
    args = p.parse_args()
    if not args.site_url:
        p.error("SITE_URL (or --site-url) is required")
    build(args.root, args.site_url)
