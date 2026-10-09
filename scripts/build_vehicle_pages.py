import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "vehicles"
CANONICAL_OUT = ROOT / "maintenance"
CONFIG = json.loads((ROOT / "config/site.json").read_text(encoding="utf-8"))
SITE_ORIGIN = (os.getenv("PUBLIC_SITE_ORIGIN") or CONFIG["defaultOrigin"]).rstrip("/")

vehicles = json.loads((DATA / "vehicles.json").read_text(encoding="utf-8"))
details = json.loads((DATA / "vehicle-details.json").read_text(encoding="utf-8"))
detail_map = {d["id"]: d for d in details}

def absolute_url(path):
    return SITE_ORIGIN + "/" + path.strip("/")

def canonical_path(vehicle):
    return f'maintenance/{vehicle["makerSlug"]}/{vehicle["publicSlug"]}/'

def legacy_path(vehicle):
    return f'vehicles/{vehicle["id"]}/'

def route_for(vehicle):
    return canonical_path(vehicle) if vehicle.get("urlStatus") == "pilot" else legacy_path(vehicle)

def seo_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

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

def full_page(vehicle, rendered, *, canonical, stylesheet, back_href, breadcrumb_items=None):
    json_ld = ""
    if breadcrumb_items:
        data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": absolute_url(path)}
                for i, (name, path) in enumerate(breadcrumb_items)
            ],
        }
        json_ld = f'<script type="application/ld+json">{seo_json(data)}</script>'
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{e(rendered["title"])} {e(rendered["focus"])} 정비·리콜 정보">
  <title>{e(rendered["title"])} 정비·리콜 가이드</title>
  <link rel="canonical" href="{e(canonical)}">
  <link rel="stylesheet" href="{stylesheet}?v=20261010-url1">
  {json_ld}
</head>
<body>
  <header class="detail-hero">
    <div class="wrap">
      <a class="back-link" href="{back_href}">← 차량 목록</a>
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

def compatibility_redirect(vehicle, rendered):
    target = absolute_url(canonical_path(vehicle))
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,follow">
  <meta http-equiv="refresh" content="0; url={e(target)}">
  <link rel="canonical" href="{e(target)}">
  <title>{e(rendered["title"])} 새 주소로 이동</title>
  <script>location.replace({json.dumps(target)});</script>
</head>
<body>
  <p>새 고정 주소로 이동합니다. <a href="{e(target)}">계속하기</a></p>
</body>
</html>"""

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def patch_canonical(path, target):
    text = path.read_text(encoding="utf-8")
    marker = "<!-- SEO_CANONICAL -->"
    if marker not in text:
        raise RuntimeError(f"canonical marker missing: {path}")
    path.write_text(text.replace(marker, f'<link rel="canonical" href="{e(target)}">'), encoding="utf-8")

OUT.mkdir(exist_ok=True)
CANONICAL_OUT.mkdir(exist_ok=True)

pilot = [v for v in vehicles if v.get("urlStatus") == "pilot"]
pilot_makers = sorted({v["makerSlug"] for v in pilot})

for vehicle in vehicles:
    detail = detail_map.get(vehicle["id"])
    rendered = render_detail(vehicle, detail) if detail else render_pending(vehicle)
    legacy_file = OUT / vehicle["id"] / "index.html"
    if vehicle.get("urlStatus") == "pilot":
        canonical = absolute_url(canonical_path(vehicle))
        breadcrumb = [
            ("자동차 생활", ""),
            ("정비·리콜", "maintenance/"),
            (vehicle["maker"], f'maintenance/{vehicle["makerSlug"]}/'),
            (rendered["title"], canonical_path(vehicle)),
        ]
        canonical_file = CANONICAL_OUT / vehicle["makerSlug"] / vehicle["publicSlug"] / "index.html"
        write(canonical_file, full_page(
            vehicle, rendered,
            canonical=canonical,
            stylesheet="../../../styles.css",
            back_href="../../../",
            breadcrumb_items=breadcrumb,
        ))
        write(legacy_file, compatibility_redirect(vehicle, rendered))
    else:
        legacy_canonical = absolute_url(legacy_path(vehicle))
        write(legacy_file, full_page(
            vehicle, rendered,
            canonical=legacy_canonical,
            stylesheet="../../styles.css",
            back_href="../../",
        ))

maintenance_cards = []
for maker_slug in pilot_makers:
    maker_vehicles = [v for v in pilot if v["makerSlug"] == maker_slug]
    maker_name = maker_vehicles[0]["maker"]
    maintenance_cards.append(
        f'<a class="card-link" href="./{e(maker_slug)}/"><article class="card">'
        f'<span class="pill">제조사</span><h3>{e(maker_name)}</h3>'
        f'<div class="meta">고정 URL 파일럿 {len(maker_vehicles)}대</div>'
        f'<span class="card-action">차량 보기 →</span></article></a>'
    )
maintenance_page = f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="제조사와 차종별 자동차 정비·리콜 가이드">
<title>자동차 정비·리콜 가이드</title>
<link rel="canonical" href="{e(absolute_url("maintenance/"))}">
<link rel="stylesheet" href="../styles.css?v=20261010-url1">
</head><body>
<header class="module-hero"><div class="wrap"><a class="back-link" href="../">← 자동차 생활 홈</a>
<p class="eyebrow">MAINTENANCE</p><h1>정비·리콜</h1>
<p class="hero-copy">제조사 → 차종·세대 → 연식·엔진 사양 순으로 확인합니다.</p></div></header>
<main class="wrap module-main"><div class="cards">{''.join(maintenance_cards)}</div></main>
</body></html>"""
write(CANONICAL_OUT / "index.html", maintenance_page)

for maker_slug in pilot_makers:
    maker_vehicles = [v for v in pilot if v["makerSlug"] == maker_slug]
    maker_name = maker_vehicles[0]["maker"]
    cards = []
    for vehicle in maker_vehicles:
        detail = detail_map.get(vehicle["id"])
        rendered = render_detail(vehicle, detail) if detail else render_pending(vehicle)
        cards.append(
            f'<a class="card-link" href="./{e(vehicle["publicSlug"])}/"><article class="card">'
            f'<span class="pill">{e(vehicle["generation"])}</span><h3>{e(rendered["title"])}</h3>'
            f'<div class="meta">{vehicle["yearFrom"]}–{vehicle["yearTo"]}</div>'
            f'<span class="card-action">정비·리콜 정보 보기 →</span></article></a>'
        )
    maker_page = f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{e(maker_name)} 차종별 정비·리콜 가이드">
<title>{e(maker_name)} 정비·리콜 가이드</title>
<link rel="canonical" href="{e(absolute_url(f"maintenance/{maker_slug}/"))}">
<link rel="stylesheet" href="../../styles.css?v=20261010-url1">
</head><body>
<header class="module-hero"><div class="wrap"><a class="back-link" href="../">← 정비·리콜</a>
<p class="eyebrow">MAKER</p><h1>{e(maker_name)}</h1>
<p class="hero-copy">차종·세대별 고정 URL 파일럿</p></div></header>
<main class="wrap module-main"><div class="cards">{''.join(cards)}</div></main>
</body></html>"""
    write(CANONICAL_OUT / maker_slug / "index.html", maker_page)

patch_canonical(ROOT / "index.html", absolute_url(""))
patch_canonical(ROOT / "fuel/index.html", absolute_url("fuel/"))
patch_canonical(ROOT / "purchase/index.html", absolute_url("purchase/"))

sitemap_paths = ["", "fuel/", "purchase/", "maintenance/"]
sitemap_paths += [f"maintenance/{m}/" for m in pilot_makers]
sitemap_paths += [canonical_path(v) for v in pilot]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n' + \
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
    ''.join(f'  <url><loc>{e(absolute_url(p))}</loc></url>\n' for p in sitemap_paths) + \
    '</urlset>\n'
write(ROOT / "sitemap.xml", sitemap)
write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {absolute_url('sitemap.xml')}\n")

print(
    f"built vehicle pages={len(vehicles)} details={len(details)} "
    f"pretty_url_pilot={len(pilot)} origin={SITE_ORIGIN}"
)
