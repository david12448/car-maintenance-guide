const $=s=>document.querySelector(s);
const state={stations:[],meta:null,regions:[]};
const brandNames={SKE:"SK에너지",GSC:"GS칼텍스",HDO:"HD현대오일뱅크",SOL:"S-OIL",RTE:"자영알뜰",RTX:"고속도로알뜰",NHO:"농협알뜰",ETC:"자가상표",E1G:"E1",SKG:"SK가스"};
function esc(v){return String(v??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}
function uniq(v){return [...new Set(v.filter(Boolean))].sort((a,b)=>a.localeCompare(b,"ko"))}
function setOptions(el,values,label){const cur=el.value;el.innerHTML='<option value="">'+label+'</option>'+values.map(v=>'<option value="'+esc(v)+'">'+esc(v)+'</option>').join("");if([...el.options].some(x=>x.value===cur))el.value=cur}
function selectedRegion(){return state.regions.find(r=>r.name===$("#fuelSido").value)||null}
function canonicalSido(name){if(!name)return"";for(const r of state.regions){if(r.name===name||(r.aliases||[]).includes(name))return r.name}return name}
function priceFor(s,p){return (s.fuels||[]).find(x=>x.product_code===p)||null}
function trade(f){if(!f||!f.trade_date)return"기준시각 확인 중";const d=f.trade_date,t=f.trade_time||"";const date=d.length===8?d.slice(0,4)+"-"+d.slice(4,6)+"-"+d.slice(6,8):d;const time=t.length>=4?t.slice(0,2)+":"+t.slice(2,4):t;return time?date+" "+time:date}
function tags(s){const x=s.services||{},r=[];if(x.car_wash)r.push("세차장");if(x.light_maintenance)r.push("경정비");if(x.convenience_store)r.push("편의점");if(x.quality_program)r.push("품질인증");return r}
function rebuildRegions(){
  const sido=$("#fuelSido"),sig=$("#fuelSigungu");
  setOptions(sido,state.regions.map(r=>r.name),"시·도 전체");
  const region=selectedRegion();
  setOptions(sig,region?region.sigungu:[],"시·군·구 전체");
  sig.disabled=!region;
  updateMapSelection();
}
function rebuildBrands(){
  setOptions($("#fuelBrand"),uniq(state.stations.map(x=>x.brand_code)),"브랜드 전체");
  [...$("#fuelBrand").options].forEach(o=>{if(o.value&&brandNames[o.value])o.textContent=brandNames[o.value]});
}
function updateMapSelection(){
  const selected=$("#fuelSido").value;
  document.querySelectorAll(".map-region-button").forEach(btn=>{
    const on=btn.dataset.sido===selected;
    btn.classList.toggle("is-active",on);
    btn.setAttribute("aria-pressed",on?"true":"false");
  });
  const region=selectedRegion();
  const sig=$("#fuelSigungu").value;
  $("#regionSelectionStatus").textContent=region?(sig?region.short+" · "+sig:region.short+" 전체"):"전국을 보고 있습니다.";
}
function selectSido(name){
  $("#fuelSido").value=name||"";
  $("#fuelSigungu").value="";
  rebuildRegions();
  render();
}
function render(){
  const product=$("#fuelProduct").value;
  const selectedSido=$("#fuelSido").value;
  const selectedSig=$("#fuelSigungu").value;
  let rows=state.stations.filter(s=>{
    const stationSido=canonicalSido(s.region?.sido);
    if(selectedSido&&stationSido!==selectedSido)return false;
    if(selectedSig&&s.region?.sigungu!==selectedSig)return false;
    if($("#fuelBrand").value&&s.brand_code!==$("#fuelBrand").value)return false;
    if($("#filterCarWash").checked&&!s.services?.car_wash)return false;
    if($("#filterMaintenance").checked&&!s.services?.light_maintenance)return false;
    if($("#filterConvenience").checked&&!s.services?.convenience_store)return false;
    if($("#filterQuality").checked&&!s.services?.quality_program)return false;
    return!!priceFor(s,product)
  });
  rows.sort((a,b)=>$("#fuelSort").value==="name"?String(a.name).localeCompare(String(b.name),"ko"):(priceFor(a,product)?.price??Infinity)-(priceFor(b,product)?.price??Infinity));
  const result=$("#fuelResults");
  updateMapSelection();
  if(!state.stations.length){
    const region=selectedRegion(),sig=selectedSig;
    const where=region?(sig?region.short+" "+sig:region.short):"전국";
    $("#fuelSummary").textContent=where+" · 가격 데이터 연동 전";
    result.innerHTML='<div class="fuel-empty"><strong>'+esc(where)+'의 지역 선택은 정상 동작합니다.</strong><p>현재 실제 주유소 가격 데이터가 아직 연결되지 않아 금액은 표시하지 않습니다. 오피넷 Private 수집이 활성화되면 이 조건 그대로 가격순 목록이 나타납니다.</p></div>';
    return
  }
  $("#fuelSummary").textContent=rows.length+"개 주유소";
  result.innerHTML=rows.length?rows.map(s=>{const f=priceFor(s,product),h=s.hours||{},ts=tags(s);return '<article class="fuel-card"><div class="fuel-card-top"><span class="pill">'+esc(brandNames[s.brand_code]||s.brand_code||"브랜드 확인 중")+'</span><span class="fuel-price">'+Number(f.price).toLocaleString("ko-KR")+'원/L</span></div><h3>'+esc(s.name)+'</h3><p class="fuel-address">'+esc(s.location?.address||"")+'</p><div class="fuel-meta">가격 기준: '+esc(trade(f))+'</div><div class="fuel-meta">운영시간: '+(h.status==="verified"?(h.open_24h?"24시간":esc((h.open_time||"")+"–"+(h.close_time||""))):"확인 필요")+'</div><div class="fuel-tags">'+ts.map(x=>"<span>"+esc(x)+"</span>").join("")+'</div><div class="fuel-card-benefit">주유 할인카드 연결: 준비 중</div></article>'}).join(""):'<div class="fuel-empty">선택한 조건에 맞는 검증된 가격 데이터가 없습니다.</div>'
}
Promise.all([
  fetch("../data/fuel/stations.json?v=20261010-map1").then(r=>r.ok?r.json():Promise.reject()),
  fetch("../data/fuel/meta.json?v=20261010-map1").then(r=>r.ok?r.json():Promise.reject()),
  fetch("../data/fuel/regions.json?v=20261010-map1").then(r=>r.ok?r.json():Promise.reject())
]).then(([stations,meta,regions])=>{
  state.stations=Array.isArray(stations)?stations:[];
  state.meta=meta;
  state.regions=Array.isArray(regions)?regions:[];
  $("#fuelUpdated").textContent=meta?.updatedAt?"갱신 "+meta.updatedAt:"실가격 연동 준비 중";
  rebuildRegions();
  rebuildBrands();
  render()
}).catch(()=>{
  $("#fuelResults").innerHTML='<div class="fuel-empty">지역 또는 주유소 데이터를 불러오지 못했습니다.</div>'
});
$("#fuelSido").addEventListener("change",()=>{$("#fuelSigungu").value="";rebuildRegions();render()});
$("#fuelSigungu").addEventListener("change",()=>{updateMapSelection();render()});
document.querySelectorAll(".map-region-button").forEach(btn=>btn.addEventListener("click",()=>selectSido(btn.dataset.sido)));
$("#clearMapRegion").addEventListener("click",()=>selectSido(""));
["fuelProduct","fuelBrand","fuelSort","filterCarWash","filterMaintenance","filterConvenience","filterQuality"].forEach(id=>$("#"+id).addEventListener("change",render));