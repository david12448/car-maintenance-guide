const $ = (s) => document.querySelector(s);
const params = new URLSearchParams(location.search);
const id = params.get("id") || "mercedes-eclass-w212";

function esc(v) {
  return String(v ?? "").replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[m]));
}

function safetyClass(v) {
  if (v === "전문 정비 권장") return "safety-pro";
  if (v === "정비소/장비 권장") return "safety-shop";
  return "safety-owner";
}

function formatNumber(v) {
  if (v === null || v === undefined) return "";
  return Number(v).toLocaleString("ko-KR");
}

function specSummary(items) {
  if (!Array.isArray(items) || !items.length) return "";
  return '<div class="spec-summary">' +
    items.map((item) => '<div class="spec-row">' + esc(item) + '</div>').join("") +
    '</div>';
}

function videoCard(item) {
  const metrics = [];
  if (item.viewCount !== null && item.viewCount !== undefined) metrics.push("조회 " + formatNumber(item.viewCount));
  if (item.commentCount !== null && item.commentCount !== undefined) metrics.push("댓글 " + formatNumber(item.commentCount));
  if (item.positiveCommentRatio !== null && item.positiveCommentRatio !== undefined) {
    metrics.push("긍정 " + Math.round(item.positiveCommentRatio * 100) + "%");
  }

  const body = `
    <article class="video-card">
      <div class="video-top">
        <span class="pill">${esc(item.matchLabel || "차량 일치 확인")}</span>
        <span class="pill">${esc(item.topic || "정비 참고")}</span>
      </div>
      <h3>${esc(item.title)}</h3>
      <p class="video-channel">${esc(item.channel)}</p>
      <p class="video-summary">${esc(item.summary || "")}</p>
      <div class="video-metrics">${metrics.map((x) => "<span>" + esc(x) + "</span>").join("")}</div>
    </article>`;

  if (item.publicLinkPolicy === "direct" && item.videoId && item.safetyClass === "owner_simple") {
    return '<a class="video-link" href="https://www.youtube.com/watch?v=' +
      encodeURIComponent(item.videoId) +
      '" target="_blank" rel="noopener noreferrer">' +
      body +
      "</a>";
  }
  return body;
}

function renderVideos(v) {
  const section = $("#videosSection");
  const root = $("#videoGroups");
  const info = v.videoDiscovery;
  const videos = Array.isArray(v.videos) ? v.videos : [];

  if (!info && !videos.length) {
    section.hidden = true;
    return;
  }

  section.hidden = false;
  const groups = [
    { key: "korea", label: "국내 추천" },
    { key: "overseas", label: "해외 추천" }
  ];

  root.innerHTML = groups.map((group) => {
    const rows = videos
      .filter((x) => x.countryGroup === group.key && x.publicLinkPolicy !== "hide")
      .sort((a, b) =>
        (b.vehicleMatchScore || 0) - (a.vehicleMatchScore || 0) ||
        (b.popularityScore || 0) - (a.popularityScore || 0)
      );

    const cards = rows.length
      ? rows.map(videoCard).join("")
      : '<div class="video-empty">차량 사양과 영상 내용을 검증 중입니다.</div>';

    const preferred = group.key === "korea" && info?.preferredChannels?.length
      ? '<div class="video-preferred">우선 확인 채널: ' +
        info.preferredChannels.map(esc).join(" · ") +
        "</div>"
      : "";

    return '<section class="video-group"><h3>' +
      group.label +
      "</h3>" +
      preferred +
      '<div class="video-list">' +
      cards +
      "</div></section>";
  }).join("");
}

function recallRecords(records) {
  if (!Array.isArray(records) || !records.length) return "";
  return '<div class="recall-records">' +
    records.map((r) => `
      <article class="recall-record">
        <div class="recall-record-head">
          <strong>${esc(r.title)}</strong>
          <span>${esc(r.announced)}</span>
        </div>
        <div class="meta">대상 생산기간 ${esc(r.production)}</div>
        <p>${esc(r.summary)}</p>
        <div class="remedy"><strong>조치:</strong> ${esc(r.remedy)}</div>
      </article>`).join("") +
    "</div>";
}

function renderDetail(v) {
  document.title = v.focusVariant + " 정비 가이드";
  $("#vehicleTitle").textContent = v.title;
  $("#vehicleFocus").textContent = v.focusVariant + " · " + v.production + " · " + v.verification;

  $("#identityCard").innerHTML = `
    <p class="eyebrow">IDENTITY</p>
    <h2>차량 식별 상태</h2>
    <p>${esc(v.identityNotice)}</p>
    ${specSummary(v.specSummary)}
    <div class="status-row"><span class="status-dot"></span><strong>${esc(v.verification)}</strong></div>`;

  $("#recallCard").innerHTML = `
    <div>
      <p class="eyebrow">RECALL & SERVICE CAMPAIGN</p>
      <h2>${esc(v.recall.headline)}</h2>
      <p>${esc(v.recall.summary)}</p>
      ${recallRecords(v.recall.records)}
    </div>
    <div class="recall-side">
      <span class="recall-status">${esc(v.recall.status)}</span>
      <button class="disabled-action" type="button" disabled>${esc(v.recall.actionLabel)}</button>
    </div>`;

  $("#maintenanceGrid").innerHTML = v.maintenance.map((item) => `
    <article class="maintenance-card">
      <div class="maintenance-top">
        <span class="pill">${esc(item.category)}</span>
        <span class="safety-pill ${safetyClass(item.safety)}">${esc(item.safety)}</span>
      </div>
      <h3>${esc(item.name)}</h3>
      <p>${esc(item.summary)}</p>
      <div class="meta">${esc(item.status)}</div>
    </article>`).join("");

  renderVideos(v);

  $("#sourcesCard").innerHTML = `
    <p class="eyebrow">SOURCE BASIS</p>
    <h2>검증 기준</h2>
    <p>아래 유형의 공식 자료를 우선해 정보를 검증합니다. 내부 원본 URL과 수집 경로는 공개 데이터에 포함하지 않습니다.</p>
    <div class="source-tags">${v.sourceLabels.map((x) => "<span>" + esc(x) + "</span>").join("")}</div>`;
}

function renderPending(vehicle) {
  document.title = vehicle.maker + " " + vehicle.model + " " + vehicle.generation + " 정비 가이드";
  $("#vehicleTitle").textContent = vehicle.maker + " " + vehicle.model + " " + vehicle.generation;
  $("#vehicleFocus").textContent = vehicle.yearFrom + "–" + vehicle.yearTo + " · 상세 자료 수집 준비 중";

  $("#identityCard").innerHTML = `
    <p class="eyebrow">IDENTITY</p>
    <h2>기본 차량 정보</h2>
    <p>이 차량은 목록에 등록되어 있으며 세부 정비·리콜 자료를 순차적으로 검증하고 있습니다.</p>
    <div class="spec-summary">
      <div class="spec-row">제조사: ${esc(vehicle.maker)}</div>
      <div class="spec-row">차종: ${esc(vehicle.model)}</div>
      <div class="spec-row">세대/코드: ${esc(vehicle.generation)} / ${esc(vehicle.platform || "확인 중")}</div>
      <div class="spec-row">연식 범위: ${vehicle.yearFrom}–${vehicle.yearTo}</div>
    </div>
    <div class="status-row"><span class="status-dot"></span><strong>${esc(vehicle.status)}</strong></div>`;

  $("#recallCard").innerHTML = `
    <div>
      <p class="eyebrow">RECALL & SERVICE CAMPAIGN</p>
      <h2>리콜·무상수리 자료 수집 중</h2>
      <p>차종·세대·생산기간이 일치하는 공식 리콜 자료를 확인하고 있습니다. 개별 차량 대상 여부는 차량번호 또는 VIN 공식 조회가 최종 기준입니다.</p>
    </div>
    <div class="recall-side"><span class="recall-status">검증 준비 중</span></div>`;

  $("#maintenanceGrid").innerHTML = `
    <article class="maintenance-card">
      <div class="maintenance-top"><span class="pill">준비 중</span></div>
      <h3>정비·관리 항목 수집 예정</h3>
      <p>와이퍼, 필터류, 엔진오일, 냉각수, 전기·조명, 리콜 등 차량별 정보를 공식 자료부터 순차적으로 연결합니다.</p>
      <div class="meta">상세 데이터 준비 중</div>
    </article>`;

  $("#videosSection").hidden = true;
  $("#sourcesCard").innerHTML = `
    <p class="eyebrow">SOURCE BASIS</p>
    <h2>수집 기준</h2>
    <p>제조사 공식 매뉴얼·자동차리콜센터·공공 통계를 우선하고, 유튜브·블로그는 차량 사양이 맞는지 확인한 뒤 참고자료로 추가합니다.</p>`;
}

Promise.all([
  fetch("./data/vehicle-details.json").then((r) => {
    if (!r.ok) throw new Error("detail load failed");
    return r.json();
  }),
  fetch("./data/vehicles.json").then((r) => {
    if (!r.ok) throw new Error("vehicles load failed");
    return r.json();
  })
])
  .then(([details, vehicles]) => {
    const detail = details.find((x) => x.id === id);
    if (detail) {
      renderDetail(detail);
      return;
    }

    const vehicle = vehicles.find((x) => x.id === id);
    if (vehicle) {
      renderPending(vehicle);
      return;
    }

    throw new Error("vehicle not found");
  })
  .catch((error) => {
    console.error(error);
    $("#vehicleTitle").textContent = "차량 정보를 불러오지 못했습니다";
    $("#vehicleFocus").textContent = "차량 목록으로 돌아가 다시 선택해주세요.";
    $("#identityCard").innerHTML = '<p>상세 데이터를 불러오는 과정에서 오류가 발생했습니다.</p>';
    $("#recallCard").innerHTML = "";
    $("#maintenanceGrid").innerHTML = "";
    $("#videosSection").hidden = true;
    $("#sourcesCard").innerHTML = "";
  });
