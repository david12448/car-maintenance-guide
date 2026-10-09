"""Verify directly addressable car maintenance pages and legacy compatibility."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cars=json.loads((ROOT/"data/vehicles.json").read_text(encoding="utf-8"))
details={x["id"] for x in json.loads((ROOT/"data/vehicle-details.json").read_text(encoding="utf-8"))}
config=json.loads((ROOT/"site.config.json").read_text(encoding="utf-8"))
assert config["public_origin"] is None, "Do not pin an unapproved custom domain"
assert not (ROOT/"CNAME").exists(), "DNS must not be configured in URL pilot"
assert not (ROOT/"sitemap.xml").exists(), "Canonical sitemap cannot predate verified origin"
assert (ROOT/"vehicle.html").is_file(), "Legacy vehicle query wrapper is required"
assert "new URLSearchParams" in (ROOT/"vehicle.html").read_text(encoding="utf-8")
for v in cars:
    file=ROOT/"vehicles"/v["id"]/"index.html"
    assert file.is_file(), f"Missing static URL: {file}"
    raw=file.read_text(encoding="utf-8")
    assert f"{v['maker']} {v['model']}" in raw
    assert '../../styles.css' in raw
    assert 'evococoons.com' not in raw and 'prince-in-wonderworld.com' not in raw
    if v["id"] not in details:
        assert 'name="robots" content="noindex"' in raw, "Pending page must not advertise for indexing"
    else:
        assert 'name="robots" content="noindex"' not in raw, "Reviewed detail must remain indexable"
print("PASS:",len(cars),"existing vehicle static routes verified, pending noindex, legacy preserved")
