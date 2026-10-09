import json
import os
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
vehicles = json.loads((ROOT / "data/vehicles.json").read_text(encoding="utf-8"))
config = json.loads((ROOT / "config/site.json").read_text(encoding="utf-8"))
origin = (os.getenv("PUBLIC_SITE_ORIGIN") or config["defaultOrigin"]).rstrip("/")

def text(path):
    return path.read_text(encoding="utf-8")

pilot = [v for v in vehicles if v["urlStatus"] == "pilot"]
assert pilot, "pretty URL pilot required"

for v in pilot:
    canonical_path = ROOT / "maintenance" / v["makerSlug"] / v["publicSlug"] / "index.html"
    legacy_path = ROOT / "vehicles" / v["id"] / "index.html"
    assert canonical_path.exists(), f"missing canonical page {canonical_path}"
    assert legacy_path.exists(), f"missing legacy page {legacy_path}"
    expected = f'{origin}/maintenance/{v["makerSlug"]}/{v["publicSlug"]}/'
    c = text(canonical_path)
    l = text(legacy_path)
    assert f'<link rel="canonical" href="{expected}">' in c
    assert '<meta name="robots" content="noindex,follow">' in l
    assert f'<link rel="canonical" href="{expected}">' in l
    assert expected in l

for rel, expected in [
    ("index.html", f"{origin}/"),
    ("fuel/index.html", f"{origin}/fuel/"),
    ("purchase/index.html", f"{origin}/purchase/"),
]:
    assert f'<link rel="canonical" href="{expected}">' in text(ROOT / rel)

sitemap = ROOT / "sitemap.xml"
robots = ROOT / "robots.txt"
assert sitemap.exists() and robots.exists()
root = ET.parse(sitemap).getroot()
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = {x.text for x in root.findall("s:url/s:loc", ns)}
for v in pilot:
    pretty = f'{origin}/maintenance/{v["makerSlug"]}/{v["publicSlug"]}/'
    legacy = f'{origin}/vehicles/{v["id"]}/'
    assert pretty in locs
    assert legacy not in locs
assert f"Sitemap: {origin}/sitemap.xml" in text(robots)

legacy_query = text(ROOT / "vehicle.html")
assert "data/vehicles.json" in legacy_query
assert 'urlStatus==="pilot"' in legacy_query

print(f"OK pretty_url_pilot={len(pilot)} sitemap_urls={len(locs)} origin={origin}")
