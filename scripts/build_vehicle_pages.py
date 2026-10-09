import html
import json
import os
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "vehicles"

vehicles = json.loads((DATA / "vehicles.json").read_text(encoding="utf-8"))
details = json.loads((DATA / "vehicle-details.json").read_text(encoding="utf-8"))
detail_map = {d["id"]: d for d in details}

def site_origin():
    configured = os.environ.get("SITE_ORIGIN", "").strip()
    if not configured:
        return None
    parts = urlsplit(configured)
    if (parts.scheme != "https" or not parts.hostname or parts.username or parts.password
            or parts.query or parts.fragment or (parts.path and not parts.path.endswith("/"))):
        raise ValueError("SITE_ORIGIN must be a verified absolute HTTPS deployment root ending in /")
    return configured.rstrip("/") + "/"

ORIGIN = site_origin()

def e(v):
    return html.escape(str(v if v is not None else ""), quote=True)

def safety_class(v):
    if v == "전문 정비 권장":
        return "safety-pro"
    if v == "정비소/장비 권장":
        return "safety-shop"
    return "safety-owner"

def render_specs(items):
    if not items:
        return ""
    return '<div class="spec-summary">' + "".join(
        f'<div class="spec-row">{e(x)}</div>' for x in items
    ) + "</div>"

def render_recalls(recall):
    records = recall.get("records", [])
    rec_html = ""
    if records:
        rows = []
        for r in records:
            rows.append(f"""
            <article class="recall-record">
              <div class="recall-record-head"><strong>{e(r.get("title"))}</strong><span>{e(r.get("announced"))}</span></div>
              <div class="meta">대상 생산기간 {e(r.get("production"))}</div>
              <p>{e(r.get("summary"))}</p>
              <div class="remedy"><strong>조치:</strong> {e(r.get("remedy"))}</div>
            </article>""")
        rec_html = '<div class="recall-records">' + "".join(rows) + "</div>"
    return f"""
    <section class="recall-card">
      <div>
        <p class="eyebrow">RECALL &amp; SERVICE CAMPAIGN</p>
        <h2>{e(recall.get("headline"))}</h2>
        <p>{e(recall.get("summary"))}</p>
        {rec_html}
      </div>
      <div class="recall-side">
        <span class="recall-status">{e(recall.get("status"))}</span>
        <span class="disabled-action">{e(recall.get("actionLabel"))}</span>
      </div>
    </section>"""

def render_variants(detail):
    variants = detail.get("variants", [])
    if not variants:
        return ""
    cards = []
    for v in variants:
        status = {"verified":"검증 완료","partial":"부분 검증","pending":"검증 중"}.get(v.get("verification"), "검증 중")
        primary = '<span class="variant-primary">현재 기준</span>' if v.get("isPrimary") else ""
        facts = [
            f'{v.get("yearFrom")}–{v.get("yearTo")}' if v.get("yearFrom") != v.get("yearTo") else str(v.get("yearFrom")),
            v.get("fuel"),
            v.get("engine"),
            v.get("transmission"),
            v.get("drivetrain"),
        ]
        fact_html = "".join(f'<span>{e(x)}</span>' for x in facts if x)
        cards.append(f"""
        <article class="variant-card {'is-primary' if v.get('isPrimary') else ''}">
          <div class="variant-card-head">{primary}<span class="variant-status">{e(status)}</span></div>
          <h3>{e(v.get("label"))}</h3>
          <div class="variant-facts">{fact_html}</div>
          <p>{e(v.get("note"))}</p>
        </article>""")
    return f"""
    <section class="variant-panel">
      <div class="variant-panel-head">
        <div><p class="eyebrow">VARIANT CHECK</p><h2>내 차 사양 먼저 확인</h2></div>
      </div>
      <p class="variant-warning">{e(detail.get("variantPolicyNote"))}</p>
      <div class="variant-grid">{''.join(cards)}</div>
    </section>"""

def render_maintenance(items):
    cards = []
    for item in items or []:
        cards.append(f"""
        <article class="maintenance-card">
          <div class="maintenance-top">
            <span class="pill">{e(item.get("category"))}</span>
            <span class="safety-pill {safety_class(item.get("safety"))}">{e(item.get("safety"))}</span>
          </div>
          <h3>{e(item.get("name"))}</h3>
          <p>{e(item.get("summary"))}</p>
          <div class="maintenance-scope">적용범위: {e(item.get("scopeLabel") or "차량 사양 확인 후 적용")}</div>
          <div class="meta">{e(item.get("status"))}</div>
        </article>""")
    return "".join(cards)

def render_videos(detail):
    info = detail.get("videoDiscovery")
    videos = [v for v in detail.get("videos", []) if v.get("publicLinkPolicy") != "hide"]
    if not info and not videos:
        return ""
    sections = []
    for key, label in (("korea", "국내 추천"), ("overseas", "해외 추천")):
        rows = [v for v in videos if v.get("countryGroup") == key]
        rows.sort(key=lambda x: (x.get("vehicleMatchScore", 0), x.get("popularityScore", 0)), reverse=True)
        cards = []
        for v in rows:
            metrics = []
            if v.get("viewCount") is not None:
                metrics.append(f'조회 {int(v["viewCount"]):,}')
            if v.get("commentCount") is not None:
                metrics.append(f'댓글 {int(v["commentCount"]):,}')
            if v.get("positiveCommentRatio") is not None:
                metrics.append(f'긍정 {round(v["positiveCommentRatio"]*100)}%')
            card = f"""
              <article class="video-card">
                <div class="video-top"><span class="pill">{e(v.get("matchLabel") or "차량 일치 확인")}</span><span class="pill">{e(v.get("topic") or "정비 참고")}</span></div>
                <h3>{e(v.get("title"))}</h3>
                <p class="video-channel">{e(v.get("channel"))}</p>
                <p class="video-summary">{e(v.get("summary"))}</p>
                <div class="video-metrics">{''.join(f'<span>{e(m)}</span>' for m in metrics)}</div>
              </article>"""
            if v.get("publicLinkPolicy") == "direct" and v.get("safetyClass") == "owner_simple" and v.get("videoId"):
                card = f'<a class="video-link" href="https://www.youtube.com/watch?v={e(v["videoId"])}" target="_blank" rel="noopener noreferrer">{card}</a>'
            cards.append(card)
        preferred = ""
        if key == "korea" and info and info.get("preferredChannels"):
            preferred = '<div class="video-preferred">우선 확인 채널: ' + " · ".join(e(x) for x in info["preferredChannels"]) + "</div>"
        body = "".join(cards) if cards else '<div class="video-empty">차량 사양과 영상 내용을 검증 중입니다.</div>'
        sections.append(f'<section class="video-group"><h3>{label}</h3>{preferred}<div class="video-list">{body}</div></section>')
    return f"""
    <section>
      <div class="section-head">
        <div><p class="eyebrow">REFERENCE VIDEOS</p><h2>정비 참고 영상</h2></div>
        <p class="count">차량 일치도 · 조회수 · 댓글 반응 순</p>
      </div>
      <div class="video-groups">{''.join(sections)}</div>
    </section>"""

def render_detail(vehicle, detail):
    identity = f"""
    <section class="detail-panel">
      <p class="eyebrow">IDENTITY</p>
      <h2>차량 식별 상태</h2>
      <p>{e(detail.get("identityNotice"))}</p>
      {render_specs(detail.get("specSummary"))}
      <div class="status-row"><span class="status-dot"></span><strong>{e(detail.get("verification"))}</strong></div>
    </section>"""
    sources = "".join(f"<span>{e(x)}</span>" for x in detail.get("sourceLabels", []))
    return {
        "title": detail.get("title"),
        "focus": f'{detail.get("focusVariant")} · {detail.get("production")} · {detail.get("verification")}',
        "body": render_variants(detail) + identity + render_recalls(detail["recall"]) + f"""
        <section>
          <div class="section-head"><div><p class="eyebrow">MAINTENANCE</p><h2>정비·관리 항목</h2></div></div>
          <div class="maintenance-grid">{render_maintenance(detail.get("maintenance"))}</div>
        </section>
        {render_videos(detail)}
        <section class="detail-panel">
          <p class="eyebrow">SOURCE BASIS</p>
          <h2>검증 기준</h2>
          <p>아래 유형의 공식 자료를 우선해 정보를 검증합니다. 내부 원본 URL과 수집 경로는 공개 데이터에 포함하지 않습니다.</p>
          <div class="source-tags">{sources}</div>
        </section>"""
    }

def render_pending(vehicle):
    specs = [
        f'제조사: {vehicle.get("maker")}',
        f'차종: {vehicle.get("model")}',
        f'세대/코드: {vehicle.get("generation")} / {vehicle.get("platform") or "확인 중"}',
        f'연식 범위: {vehicle.get("yearFrom")}–{vehicle.get("yearTo")}',
    ]
    return {
        "title": f'{vehicle.get("maker")} {vehicle.get("model")} {vehicle.get("generation")}',
        "focus": f'{vehicle.get("yearFrom")}–{vehicle.get("yearTo")} · 상세 자료 수집 준비 중',
        "body": f"""
        <section class="detail-panel">
          <p class="eyebrow">IDENTITY</p><h2>기본 차량 정보</h2>
          <p>이 차량은 목록에 등록되어 있으며 세부 정비·리콜 자료를 순차적으로 검증하고 있습니다.</p>
          {render_specs(specs)}
          <div class="status-row"><span class="status-dot"></span><strong>{e(vehicle.get("status"))}</strong></div>
        </section>
        <section class="recall-card">
          <div><p class="eyebrow">RECALL &amp; SERVICE CAMPAIGN</p><h2>리콜·무상수리 자료 수집 중</h2>
          <p>차종·세대·생산기간이 일치하는 공식 리콜 자료를 확인하고 있습니다. 개별 차량 대상 여부는 차량번호 또는 VIN 공식 조회가 최종 기준입니다.</p></div>
          <div class="recall-side"><span class="recall-status">검증 준비 중</span></div>
        </section>
        <section>
          <div class="section-head"><div><p class="eyebrow">MAINTENANCE</p><h2>정비·관리 항목</h2></div></div>
          <div class="maintenance-grid"><article class="maintenance-card">
            <div class="maintenance-top"><span class="pill">준비 중</span></div>
            <h3>정비·관리 항목 수집 예정</h3>
            <p>와이퍼, 필터류, 엔진오일, 냉각수, 전기·조명, 리콜 등 차량별 정보를 공식 자료부터 순차적으로 연결합니다.</p>
            <div class="meta">상세 데이터 준비 중</div>
          </article></div>
        </section>
        <section class="detail-panel"><p class="eyebrow">SOURCE BASIS</p><h2>수집 기준</h2>
        <p>제조사 공식 매뉴얼·자동차리콜센터·공공 통계를 우선하고, 유튜브·블로그는 차량 사양이 맞는지 확인한 뒤 참고자료로 추가합니다.</p></section>"""
    }

OUT.mkdir(exist_ok=True)
for vehicle in vehicles:
    detail = detail_map.get(vehicle["id"])
    rendered = render_detail(vehicle, detail) if detail else render_pending(vehicle)
    # Do not index data-poor pending pages; never invent a canonical hostname.
    robots = '<meta name="robots" content="noindex">' if detail is None else ""
    canonical = (f'<link rel="canonical" href="{e(ORIGIN + "vehicles/" + vehicle["id"] + "/")}">'
                 if ORIGIN and detail is not None else "")
    page = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{e(rendered["title"])} 자동차 정비 및 리콜 가이드">
  <title>{e(rendered["title"])} 정비 가이드</title>
  {robots}
  {canonical}
  <link rel="stylesheet" href="../../styles.css?v=20261009c">
</head>
<body>
  <header class="detail-hero">
    <div class="wrap">
      <a class="back-link" href="../../">← 차량 목록</a>
      <p class="eyebrow">VEHICLE GUIDE</p>
      <h1>{e(rendered["title"])}</h1>
      <p class="hero-copy">{e(rendered["focus"])}</p>
    </div>
  </header>
  <main class="wrap detail-main">
    {rendered["body"]}
    <section class="safety-note">
      <h2>안전 기준</h2>
      <p>차량을 들어 올리거나 제동·변속기·연료·에어백·고전압 계통과 관련된 작업은 전문 정비 권장을 우선합니다. 이 페이지는 차량 식별과 공식 규격·리콜 확인을 돕는 정보 가이드입니다.</p>
    </section>
  </main>
</body>
</html>"""
    path = OUT / vehicle["id"] / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")


# Emit a sitemap only after a verified canonical origin is supplied via SITE_ORIGIN.
sitemap = ROOT / "sitemap.xml"
if ORIGIN:
    indexable = [v["id"] for v in vehicles if v["id"] in detail_map]
    urls = [ORIGIN] + [ORIGIN + "vehicles/" + slug + "/" for slug in indexable]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join("  <url><loc>" + xml_escape(u) + "</loc></url>\n" for u in urls)
    xml += "</urlset>\n"
    sitemap.write_text(xml, encoding="utf-8")
elif sitemap.exists():
    raise ValueError("Do not publish an unverified sitemap while domain is undecided")

print(f"built vehicle pages={len(vehicles)} details={len(details)} canonical={bool(ORIGIN)}")
