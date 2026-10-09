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
    variants = d.get("variants", [])
    assert variants, f'{d["id"]}: variants required'
    variant_ids = [v["variantId"] for v in variants]
    assert len(variant_ids) == len(set(variant_ids)), f'{d["id"]}: duplicate variantId'
    assert sum(1 for v in variants if v.get("isPrimary")) == 1, f'{d["id"]}: exactly one primary variant required'
    vehicle = next(v for v in vehicles if v["id"] == d["id"])
    for variant in variants:
        assert variant["yearFrom"] <= variant["yearTo"]
        assert vehicle["yearFrom"] <= variant["yearFrom"] <= vehicle["yearTo"]
        assert vehicle["yearFrom"] <= variant["yearTo"] <= vehicle["yearTo"]
        assert variant["verification"] in {"verified","partial","pending"}
    recall = d["recall"]
    assert recall["publicSourceRef"]
    assert "http" not in recall["publicSourceRef"].lower()
    for r in recall.get("records", []):
        assert r["title"]
        assert r["summary"]
        assert r["remedy"]
    for item in d.get("maintenance", []):
        assert item.get("scopeLabel"), f'{d["id"]}: maintenance scopeLabel required'
        app = item.get("applicability")
        assert app and app.get("mode") in {"generation_common","variant_specific","pending"}
        if app["mode"] == "variant_specific":
            assert app.get("variantIds"), f'{d["id"]}: variant_specific requires variantIds'
            assert all(x in variant_ids for x in app["variantIds"])
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


# Fuel module public data validation.
FUEL_DATA = DATA / "fuel"
fuel_stations = json.loads((FUEL_DATA / "stations.json").read_text(encoding="utf-8"))
fuel_meta = json.loads((FUEL_DATA / "meta.json").read_text(encoding="utf-8"))
assert isinstance(fuel_stations, list), "fuel stations must be list"
assert isinstance(fuel_meta, dict), "fuel meta must be object"
assert fuel_meta["status"] in {"awaiting_private_feed","active","stale"}
fuel_station_ids = [x["station_id"] for x in fuel_stations]
assert len(fuel_station_ids) == len(set(fuel_station_ids)), "duplicate fuel station"
for station in fuel_stations:
    assert station["brand_code"] in {"SKE","GSC","HDO","SOL","RTE","RTX","NHO","ETC","E1G","SKG"}
    assert station["verification"] in {"verified","partial","pending"}
    assert station["hours"]["status"] in {"verified","partial","unknown"}
    assert station["region"]["sido"] and station["region"]["sigungu"]
    for fuel in station["fuels"]:
        assert fuel["product_code"] in {"B027","D047","B034","C004","K015"}
        assert type(fuel["price"]) in {int,float} and fuel["price"] >= 0
for path in FUEL_DATA.glob("*.json"):
    fuel_text = path.read_text(encoding="utf-8").lower()
    for forbidden in ("https://","http://",'"certkey"','"api_key"','"source_url"','"endpoint"'):
        assert forbidden not in fuel_text, f"{path.name}: forbidden fuel token {forbidden}"


# Purchase module public data validation.
PURCHASE_DATA = DATA / "purchase"
purchase_offers = json.loads((PURCHASE_DATA / "offers.json").read_text(encoding="utf-8"))
purchase_meta = json.loads((PURCHASE_DATA / "meta.json").read_text(encoding="utf-8"))
assert isinstance(purchase_offers, list), "purchase offers must be list"
assert isinstance(purchase_meta, dict), "purchase meta must be object"
assert purchase_meta["status"] in {"awaiting_private_feed","active","stale"}
purchase_ids=[x["offer_id"] for x in purchase_offers]
assert len(purchase_ids)==len(set(purchase_ids)), "duplicate purchase offer"
for offer in purchase_offers:
    assert offer["market"] in {"new","used"}
    assert offer["price"]["price_type"] in {"manufacturer_msrp","listing_price","reference_market_price"}
    assert type(offer["price"]["amount_krw"]) is int and offer["price"]["amount_krw"]>=0
    if offer["market"]=="used":
        assert offer["price"]["price_type"]!="manufacturer_msrp"
    if offer["market"]=="new":
        assert offer["price"]["price_type"]!="reference_market_price"
for path in PURCHASE_DATA.glob("*.json"):
    purchase_text=path.read_text(encoding="utf-8").lower()
    for forbidden in ("https://","http://",'"source_url"','"raw_url"','"collector"','"parser"','"endpoint"'):
        assert forbidden not in purchase_text, f"{path.name}: forbidden purchase token {forbidden}"
