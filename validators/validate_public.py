import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

for path in DATA.glob("*.json"):
    obj = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(obj, list), f"{path.name}: top-level must be list"

vehicles = json.loads((DATA / "vehicles.json").read_text(encoding="utf-8"))
topics = json.loads((DATA / "topics.json").read_text(encoding="utf-8"))
details = json.loads((DATA / "vehicle-details.json").read_text(encoding="utf-8"))

ids = [v["id"] for v in vehicles]
assert len(ids) == len(set(ids)), "duplicate vehicle id"
for v in vehicles:
    assert v["yearFrom"] <= v["yearTo"]
    assert v["origin"] in {"국산차", "수입차"}

topic_ids = [t["id"] for t in topics]
assert len(topic_ids) == len(set(topic_ids)), "duplicate topic id"

detail_ids = [d["id"] for d in details]
assert len(detail_ids) == len(set(detail_ids)), "duplicate detail id"
assert set(detail_ids).issubset(set(ids)), "detail vehicle must exist in vehicles.json"

for d in details:
    recall = d["recall"]
    assert recall["publicSourceRef"]
    assert "http" not in recall["publicSourceRef"].lower()
    for r in recall.get("records", []):
        assert r["title"]
        assert r["summary"]
        assert r["remedy"]
    for video in d.get("videos", []):
        assert video["countryGroup"] in {"korea", "overseas"}
        assert video["safetyClass"] in {"owner_simple", "shop_assisted", "professional"}
        assert video["publicLinkPolicy"] in {"direct", "metadata_only", "hide"}
        if video["publicLinkPolicy"] == "direct":
            assert video["safetyClass"] == "owner_simple", "direct video links only allowed for owner_simple"
            assert video.get("videoId"), "direct video link requires videoId"

# Public JSON must not expose private collection infrastructure or direct source URLs.
for path in DATA.glob("*.json"):
    text = path.read_text(encoding="utf-8").lower()
    for forbidden in ("https://", "http://", '"source_url"', '"raw_url"', '"collector"', '"parser"', '"endpoint"'):
        assert forbidden not in text, f"{path.name}: forbidden public token {forbidden}"

print(f"OK public vehicles={len(vehicles)} topics={len(topics)} details={len(details)}")
