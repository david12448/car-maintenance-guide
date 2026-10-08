import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

for path in DATA.glob("*.json"):
    obj = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(obj, list), f"{path.name}: top-level must be list"

vehicles = json.loads((DATA / "vehicles.json").read_text(encoding="utf-8"))
topics = json.loads((DATA / "topics.json").read_text(encoding="utf-8"))

ids = [v["id"] for v in vehicles]
assert len(ids) == len(set(ids)), "duplicate vehicle id"
for v in vehicles:
    assert v["yearFrom"] <= v["yearTo"]
    assert v["origin"] in {"국산차", "수입차"}

topic_ids = [t["id"] for t in topics]
assert len(topic_ids) == len(set(topic_ids)), "duplicate topic id"

# Public JSON must not expose private collection infrastructure or direct source URLs.
for path in DATA.glob("*.json"):
    text = path.read_text(encoding="utf-8").lower()
    for forbidden in ("https://", "http://", '"source_url"', '"raw_url"', '"collector"', '"parser"', '"endpoint"'):
        assert forbidden not in text, f"{path.name}: forbidden public token {forbidden}"

print(f"OK public vehicles={len(vehicles)} topics={len(topics)}")
