const state={rows:[],origin:""};
const $=s=>document.querySelector(s);
const search=$("#search"),maker=$("#maker"),model=$("#model"),generation=$("#generation"),cards=$("#cards"),count=$("#count");

fetch("./data/vehicles.json")
  .then(r=>{if(!r.ok)throw new Error("vehicles load failed");return r.json()})
  .then(rows=>{state.rows=rows;rebuildFilters();render()})
  .catch(()=>{cards.innerHTML='<div class="empty">차량 데이터를 불러오지 못했습니다.</div>'});

function uniq(values){return [...new Set(values.filter(Boolean))].sort((a,b)=>a.localeCompare(b,"ko"))}
function setOptions(el,values,label){
  const selected=el.value;
  el.innerHTML='<option value="">'+label+'</option>'+uniq(values).map(v=>'<option value="'+escapeHtml(v)+'">'+escapeHtml(v)+'</option>').join("");
  if([...el.options].some(o=>o.value===selected))el.value=selected;
}
function escapeHtml(v){return String(v).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}
function baseRows(){
  return state.rows.filter(v=>(!state.origin||v.origin===state.origin));
}
function rebuildFilters(){
  const a=baseRows();
  setOptions(maker,a.map(v=>v.maker),"제조사 전체");
  const b=a.filter(v=>!maker.value||v.maker===maker.value);
  setOptions(model,b.map(v=>v.model),"차종 전체");
  const c=b.filter(v=>!model.value||v.model===model.value);
  setOptions(generation,c.map(v=>v.generation),"세대 전체");
}
function matchesText(v,q){
  if(!q)return true;
  const hay=[v.origin,v.maker,v.model,v.generation,v.platform,v.yearFrom,v.yearTo,...(v.aliases||[])].join(" ").toLowerCase();
  return q.split(/\s+/).every(token=>hay.includes(token));
}
function render(){
  const q=search.value.trim().toLowerCase();
  const rows=baseRows().filter(v=>
    (!maker.value||v.maker===maker.value)&&
    (!model.value||v.model===model.value)&&
    (!generation.value||v.generation===generation.value)&&
    matchesText(v,q)
  );
  count.textContent=rows.length+"대";
  cards.innerHTML=rows.length?rows.map(v=>`
    <article class="card">
      <span class="pill">${escapeHtml(v.origin)}</span>
      <span class="pill ${v.status==="우선 수집"?"priority":""}">${escapeHtml(v.status)}</span>
      <h3>${escapeHtml(v.maker)} ${escapeHtml(v.model)}</h3>
      <div class="generation">${escapeHtml(v.generation)}</div>
      <div class="meta">${v.yearFrom}–${v.yearTo} · ${escapeHtml(v.platform||"플랫폼 확인 중")}</div>
      <div class="aliases">${(v.aliases||[]).map(escapeHtml).join(" · ")}</div>
    </article>`).join(""):'<div class="empty">조건에 맞는 초기 차량이 없습니다. 데이터가 확대되면 자동으로 추가됩니다.</div>';
}
document.querySelectorAll("#originTabs .tab").forEach(btn=>btn.addEventListener("click",()=>{
  document.querySelectorAll("#originTabs .tab").forEach(x=>x.classList.remove("is-active"));
  btn.classList.add("is-active");state.origin=btn.dataset.origin;maker.value="";model.value="";generation.value="";rebuildFilters();render();
}));
maker.addEventListener("change",()=>{model.value="";generation.value="";rebuildFilters();render()});
model.addEventListener("change",()=>{generation.value="";rebuildFilters();render()});
generation.addEventListener("change",render);
search.addEventListener("input",render);
