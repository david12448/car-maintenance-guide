const $=s=>document.querySelector(s);
const params=new URLSearchParams(location.search);
const id=params.get("id")||"mercedes-eclass-w212";

function esc(v){return String(v??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}
function safetyClass(v){
  if(v==="전문 정비 권장")return "safety-pro";
  if(v==="정비소/장비 권장")return "safety-shop";
  return "safety-owner";
}
function formatNumber(v){
  if(v===null||v===undefined)return "";
  return Number(v).toLocaleString("ko-KR");
}
function videoCard(item){
  const metrics=[];
  if(item.viewCount!==null&&item.viewCount!==undefined)metrics.push("조회 "+formatNumber(item.viewCount));
  if(item.commentCount!==null&&item.commentCount!==undefined)metrics.push("댓글 "+formatNumber(item.commentCount));
  if(item.positiveCommentRatio!==null&&item.positiveCommentRatio!==undefined)metrics.push("긍정 "+Math.round(item.positiveCommentRatio*100)+"%");
  const body=`
    <article class="video-card">
      <div class="video-top">
        <span class="pill">${esc(item.matchLabel||"차량 일치 확인")}</span>
        <span class="pill">${esc(item.topic||"정비 참고")}</span>
      </div>
      <h3>${esc(item.title)}</h3>
      <p class="video-channel">${esc(item.channel)}</p>
      <p class="video-summary">${esc(item.summary||"")}</p>
      <div class="video-metrics">${metrics.map(x=>'<span>'+esc(x)+'</span>').join("")}</div>
    </article>`;
  if(item.publicLinkPolicy==="direct"&&item.videoId&&item.safetyClass==="owner_simple"){
    return '<a class="video-link" href="https://www.youtube.com/watch?v='+encodeURIComponent(item.videoId)+'" target="_blank" rel="noopener noreferrer">'+body+'</a>';
  }
  return body;
}
function renderVideos(v){
  const section=$("#videosSection");
  const root=$("#videoGroups");
  const info=v.videoDiscovery;
  const videos=Array.isArray(v.videos)?v.videos:[];
  if(!info&&!videos.length)return;
  section.hidden=false;
  const groups=[
    {key:"korea",label:"국내 추천"},
    {key:"overseas",label:"해외 추천"}
  ];
  root.innerHTML=groups.map(group=>{
    const rows=videos
      .filter(x=>x.countryGroup===group.key&&x.publicLinkPolicy!=="hide")
      .sort((a,b)=>(b.vehicleMatchScore||0)-(a.vehicleMatchScore||0)||(b.popularityScore||0)-(a.popularityScore||0));
    const cards=rows.length?rows.map(videoCard).join(""):'<div class="video-empty">차량 사양과 영상 내용을 검증 중입니다.</div>';
    const preferred=group.key==="korea"&&info?.preferredChannels?.length
      ? '<div class="video-preferred">우선 확인 채널: '+info.preferredChannels.map(esc).join(" · ")+'</div>'
      : "";
    return '<section class="video-group"><h3>'+group.label+'</h3>'+preferred+'<div class="video-list">'+cards+'</div></section>';
  }).join("");
}
function recallRecords(records){
  if(!Array.isArray(records)||!records.length)return "";
  return '<div class="recall-records">'+records.map(r=>`
    <article class="recall-record">
      <div class="recall-record-head"><strong>${esc(r.title)}</strong><span>${esc(r.announced)}</span></div>
      <div class="meta">대상 생산기간 ${esc(r.production)}</div>
      <p>${esc(r.summary)}</p>
      <div class="remedy"><strong>조치:</strong> ${esc(r.remedy)}</div>
    </article>`).join("")+'</div>';
}

fetch("./data/vehicle-details.json")
  .then(r=>{if(!r.ok)throw new Error("detail load failed");return r.json()})
  .then(rows=>{
    const v=rows.find(x=>x.id===id);
    if(!v)throw new Error("vehicle not found");
    document.title=v.focusVariant+" 정비 가이드";
    $("#vehicleTitle").textContent=v.title;
    $("#vehicleFocus").textContent=v.focusVariant+" · "+v.production+" · "+v.verification;

    $("#identityCard").innerHTML=`
      <p class="eyebrow">IDENTITY</p>
      <h2>차량 식별 상태</h2>
      <p>${esc(v.identityNotice)}</p>
      <div class="status-row"><span class="status-dot"></span><strong>${esc(v.verification)}</strong></div>`;

    $("#recallCard").innerHTML=`
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

    $("#maintenanceGrid").innerHTML=v.maintenance.map(item=>`
      <article class="maintenance-card">
        <div class="maintenance-top">
          <span class="pill">${esc(item.category)}</span>
          <span class="safety-pill ${safetyClass(item.safety)}">${esc(item.safety)}</span>
        </div>
        <h3>${esc(item.name)}</h3>
        <p>${esc(item.summary)}</p>
        <div class="meta">${esc(item.status)}</div>
      </article>`).join("");

    renderVideos(v);\n\n    $("#sourcesCard").innerHTML=`
      <p class="eyebrow">SOURCE BASIS</p>
      <h2>검증 기준</h2>
      <p>아래 유형의 공식 자료를 우선해 정보를 검증합니다. 내부 원본 URL과 수집 경로는 공개 데이터에 포함하지 않습니다.</p>
      <div class="source-tags">${v.sourceLabels.map(x=>'<span>'+esc(x)+'</span>').join("")}</div>`;
  })
  .catch(()=>{
    $("#vehicleTitle").textContent="차량 정보를 찾을 수 없습니다";
    $("#vehicleFocus").textContent="차량 목록으로 돌아가 다른 차량을 선택해주세요.";
    $("#identityCard").innerHTML='<p>상세 데이터가 아직 준비되지 않았습니다.</p>';
  });
