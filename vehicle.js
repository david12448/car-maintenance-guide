const $=s=>document.querySelector(s);
const params=new URLSearchParams(location.search);
const id=params.get("id")||"mercedes-eclass-w212";

function esc(v){return String(v??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}
function safetyClass(v){
  if(v==="전문 정비 권장")return "safety-pro";
  if(v==="정비소/장비 권장")return "safety-shop";
  return "safety-owner";
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

    $("#sourcesCard").innerHTML=`
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
