#!/usr/bin/env python3
"""data/restaurants.json → index.html : 우슐랭 · 우체국 맛집 가이드(부산·울산·경남).
지역탭 + 발행연도(2024/2025) 필터·태그 + 지도(Leaflet/OSM) + 종류·지역 필터."""
import json, datetime, os
from collections import Counter

rows_in = json.load(open("data/restaurants.json", encoding="utf-8"))

def slim(r):
    return {
        "n": r["name"], "r": r["region"], "g": r["district"],
        "o": r["office"], "c": r["category"], "ed": r.get("editions", []),
        "d": r.get("desc", ""), "m": r.get("menu", ""), "a": r["addr"],
        "p": r.get("phone", ""), "h": r.get("hours", ""),
        "lat": r.get("lat"), "lng": r.get("lng"),
    }

data = [slim(r) for r in rows_in if r.get("name") and r.get("lat") is not None]
data_js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
total = len(data)
reg_counts = Counter(r["r"] for r in data)
ed_counts = Counter(("2024" in r["ed"], "2025" in r["ed"]) for r in data)
updated = datetime.date.today().isoformat()
print("총", total, "· 지역", dict(reg_counts), "· 2024:", sum(1 for r in data if "2024" in r["ed"]), "2025:", sum(1 for r in data if "2025" in r["ed"]))

HTML = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#d6392b">
<meta name="description" content="우슐랭 — 부산지방우정청 우체국 직원이 추천한 부산·울산·경남 맛집. 2024·2025 판본 __TOTAL__곳. 지도·검색·길찾기.">
<title>우슐랭 · 우체국 맛집 가이드 (부산·울산·경남)</title>
<link rel="icon" type="image/png" href="icon/final/favicon_32.png">
<link rel="apple-touch-icon" href="icon/final/apple-touch-icon_180.png">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css">
<style>
:root{--bg:#f4f1ee;--card:#fff;--ink:#221a17;--sub:#6f6258;--line:#eadfd7;--brand:#d6392b;--brand2:#e8632c;--cream:#fff4ea;--shadow:0 6px 22px rgba(80,40,30,.09);--safe-t:env(safe-area-inset-top);--safe-b:env(safe-area-inset-bottom)}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0}
body{font-family:"Pretendard","Pretendard Variable",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5;-webkit-text-size-adjust:100%}
a{color:inherit;text-decoration:none}img{display:block}

.hero{background:linear-gradient(135deg,var(--brand) 0%,var(--brand2) 100%);color:#fff;padding:calc(15px + var(--safe-t)) 16px 0}
.hero .wrap{max-width:1180px;margin:0 auto}
.hero .topline{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:0 2px}
.hero h1{margin:0;font-size:21px;font-weight:800;letter-spacing:-.02em;display:flex;align-items:center;gap:8px}
.hero .stamp{background:var(--cream);color:var(--brand);font-weight:900;font-size:12px;border-radius:7px;padding:3px 7px;letter-spacing:.02em;box-shadow:0 2px 6px rgba(0,0,0,.18)}
.hero p{margin:6px 0 0;font-size:12.5px;opacity:.94;font-weight:500;max-width:700px}
.hero .src{font-size:11px;opacity:.8;margin-top:3px}
.tabs{display:flex;gap:6px;overflow-x:auto;margin-top:13px;padding:0 2px;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{flex:none;border:0;background:rgba(255,255,255,.15);color:#fff;border-radius:13px 13px 0 0;padding:11px 17px;font-size:14.5px;font-weight:700;cursor:pointer;opacity:.84;display:flex;align-items:center;gap:7px;white-space:nowrap}
.tab .tn{font-size:11px;opacity:.7;font-weight:700}
.tab.on{background:var(--bg);color:var(--ink);opacity:1}
.tab.on .tn{color:var(--brand);opacity:1}

.tools{position:sticky;top:0;z-index:1000;background:rgba(255,255,255,.94);backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--line);box-shadow:0 2px 10px rgba(80,40,30,.05)}
.tools .wrap{max-width:1180px;margin:0 auto;padding:11px 14px 7px}
.searchrow{display:flex;gap:8px;align-items:center}
.search{flex:1;display:flex;align-items:center;gap:8px;background:var(--bg);border:1.5px solid var(--line);border-radius:14px;padding:11px 14px;min-width:0}
.search:focus-within{border-color:var(--brand);background:#fff}
.search svg{flex:none;width:18px;height:18px;color:var(--sub)}
.search input{border:0;background:transparent;width:100%;font-size:15px;outline:none;color:var(--ink);min-width:0}
.viewtog{flex:none;display:flex;background:var(--bg);border:1.5px solid var(--line);border-radius:14px;overflow:hidden}
.viewtog button{border:0;background:transparent;padding:10px 12px;font-size:13px;font-weight:700;color:var(--sub);cursor:pointer;display:flex;align-items:center;gap:5px}
.viewtog button.on{background:var(--brand);color:#fff}
.viewtog svg{width:15px;height:15px}
.chips{display:flex;gap:7px;overflow-x:auto;padding:8px 2px 3px;scrollbar-width:none;align-items:center}
.chips::-webkit-scrollbar{display:none}
.chip{flex:none;border:1.5px solid var(--line);background:#fff;color:var(--sub);border-radius:999px;padding:7px 13px;font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;transition:.12s}
.chip:hover{border-color:var(--brand)}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.chip .ct{opacity:.55;font-weight:700;margin-left:3px;font-size:11px}
.chip.on .ct{opacity:.7}
.chiplabel{flex:none;align-self:center;font-size:11px;font-weight:800;color:#b3a89e;padding:0 4px 0 2px}
#eds .chip.on{background:var(--brand);border-color:var(--brand);color:#fff}
.count{max-width:1180px;margin:0 auto;padding:13px 16px 2px;font-size:13px;color:var(--sub);font-weight:600}
.count b{color:var(--brand);font-weight:800}

.grid{max-width:1180px;margin:0 auto;padding:10px 12px calc(60px + var(--safe-b));display:grid;grid-template-columns:1fr;gap:13px}
@media(min-width:560px){.grid{grid-template-columns:repeat(2,1fr);gap:14px;padding-inline:16px}}
@media(min-width:900px){.grid{grid-template-columns:repeat(3,1fr)}}
@media(min-width:1200px){.grid{grid-template-columns:repeat(4,1fr)}}
.grid.hidden{display:none}
.card{background:var(--card);border-radius:18px;overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column;border:1px solid var(--line);transition:transform .15s,box-shadow .15s}
.card:active{transform:scale(.99)}
@media(hover:hover){.card:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(80,40,30,.15)}}
.ctop{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:11px 14px 0}
.cat{font-size:11.5px;font-weight:800;color:#fff;padding:4px 10px;border-radius:999px;white-space:nowrap}
.ctr{display:flex;align-items:center;gap:6px;flex:none}
.eds{display:flex;gap:4px}
.edp{font-size:10px;font-weight:800;padding:2px 6px;border-radius:6px;border:1px solid var(--line);color:var(--sub);background:var(--bg);letter-spacing:.01em}
.edp.y25{color:#fff;background:var(--brand);border-color:var(--brand)}
.gu{font-size:11.5px;font-weight:700;color:var(--sub);white-space:nowrap}
.body{padding:8px 14px 14px;display:flex;flex-direction:column;gap:7px;flex:1}
.office{display:inline-flex;align-items:center;gap:5px;align-self:flex-start;font-size:11px;font-weight:800;color:var(--brand);background:var(--cream);border:1px solid #f3dcca;padding:3px 9px 3px 7px;border-radius:999px}
.office svg{width:12px;height:12px}
.name{font-size:18px;font-weight:800;letter-spacing:-.02em;line-height:1.3}
.hl{font-size:13px;color:var(--brand);font-weight:700;display:flex;gap:6px;align-items:flex-start}
.hl .ic{flex:none;margin-top:1px}
.hl span{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.desc{font-size:12.5px;color:#857669;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.row{font-size:12.5px;color:var(--sub);display:flex;gap:6px;align-items:flex-start}
.row .ic{flex:none;margin-top:2px;opacity:.7}
.row span{overflow:hidden;display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical}
.acts{display:flex;gap:7px;margin-top:auto;padding-top:11px}
.act{flex:1;display:flex;align-items:center;justify-content:center;gap:5px;padding:9px 6px;border-radius:11px;font-size:12.5px;font-weight:700;border:1.5px solid var(--line);color:var(--sub)}
.act svg{width:14px;height:14px}
.act.call{background:var(--brand);border-color:var(--brand);color:#fff}
.act:active{filter:brightness(.96)}

#map{display:none;width:100%;height:calc(100vh - var(--toolsH,300px));min-height:420px;background:#e4ddd5}
#map.show{display:block}
.leaflet-popup-content{margin:0;width:236px!important}
.leaflet-popup-content-wrapper{border-radius:14px;overflow:hidden;padding:0}
.pop{width:236px;font-family:inherit}
.pop .pbody{padding:11px 13px 12px}
.pop .poff{display:inline-flex;align-items:center;gap:4px;font-size:10.5px;font-weight:800;color:var(--brand);background:var(--cream);padding:2px 8px;border-radius:999px;margin-bottom:6px}
.pop .pn{font-size:15.5px;font-weight:800;color:var(--ink);line-height:1.3;margin-bottom:3px}
.pop .ped{font-size:10px;font-weight:800;color:var(--sub);margin-bottom:5px}
.pop .pm{font-size:12px;color:var(--brand);font-weight:700;margin-bottom:4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pop .pa{font-size:11.5px;color:var(--sub);line-height:1.4;margin-bottom:9px}
.pop .pacts{display:flex;gap:6px}
.pop .pacts a{flex:1;text-align:center;padding:7px 4px;border-radius:9px;font-size:11.5px;font-weight:700;border:1.5px solid var(--line);color:var(--sub)}
.pop .pacts a.call{background:var(--brand);border-color:var(--brand);color:#fff}
.mk{width:16px;height:16px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid #fff;box-shadow:0 2px 5px rgba(0,0,0,.35)}
.maphint{position:fixed;z-index:900;left:50%;transform:translateX(-50%);bottom:calc(16px + var(--safe-b));background:rgba(40,26,23,.85);color:#fff;font-size:12px;font-weight:600;padding:7px 14px;border-radius:999px;pointer-events:none;opacity:0;transition:.3s}
.maphint.show{opacity:1}
.empty{grid-column:1/-1;text-align:center;padding:70px 20px;color:var(--sub)}
.empty .em{font-size:42px}
.empty p{font-weight:600;margin:12px 0 0}
.top{position:fixed;right:16px;bottom:calc(16px + var(--safe-b));width:46px;height:46px;border-radius:50%;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 20px rgba(0,0,0,.25);opacity:0;pointer-events:none;transition:.2s;z-index:1100;cursor:pointer}
.top.show{opacity:1;pointer-events:auto}
.locate{position:fixed;left:16px;bottom:calc(16px + var(--safe-b));width:48px;height:48px;border-radius:50%;background:#fff;color:var(--brand);display:flex;align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(0,0,0,.22);z-index:1100;cursor:pointer;border:0;transition:.15s}
.locate.on{background:var(--brand);color:#fff}
.locate:active{transform:scale(.93)}
.locate svg{width:23px;height:23px}
.locate[hidden]{display:none}
.dist{color:var(--brand);font-weight:800}
.udot{width:16px;height:16px;border-radius:50%;background:#1a73e8;border:3px solid #fff;box-shadow:0 0 0 2px rgba(26,115,232,.45),0 1px 5px rgba(0,0,0,.4);animation:bfpulse 2s infinite}
@keyframes bfpulse{0%{box-shadow:0 0 0 0 rgba(26,115,232,.5),0 1px 5px rgba(0,0,0,.4)}70%{box-shadow:0 0 0 16px rgba(26,115,232,0),0 1px 5px rgba(0,0,0,.4)}100%{box-shadow:0 0 0 0 rgba(26,115,232,0),0 1px 5px rgba(0,0,0,.4)}}
.dd{position:relative;margin-left:8px;flex:none}
.dd-btn{display:flex;align-items:center;gap:6px;background:var(--bg);border:1.5px solid var(--line);border-radius:14px;padding:10px 11px;font-size:13px;font-weight:700;color:var(--ink);cursor:pointer;white-space:nowrap;max-width:150px}
.dd-btn>span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dd-btn .lic,.dd-btn .chev{width:14px;height:14px;color:var(--sub);flex:none}
.dd-btn .chev{transition:transform .2s}
.dd.open .dd-btn{border-color:var(--brand);background:#fff}
.dd.open .dd-btn .chev{transform:rotate(180deg)}
.dd-panel{position:absolute;right:0;top:calc(100% + 6px);width:210px;background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:0 14px 34px rgba(80,40,30,.2);padding:6px;z-index:1200;display:none;max-height:70vh;overflow:auto}
.dd.open .dd-panel{display:block}
.dd-h{font-size:11px;font-weight:800;color:#b3a89e;padding:8px 10px 4px;letter-spacing:.02em}
.dd-opt{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:9px 10px;border-radius:9px;font-size:13.5px;font-weight:600;color:var(--ink);cursor:pointer}
@media(hover:hover){.dd-opt:hover{background:var(--bg)}}
.dd-opt.on{background:rgba(214,57,43,.1);color:var(--brand);font-weight:800}
.dd-opt .ck{width:16px;height:16px;flex:none;opacity:0;color:var(--brand)}
.dd-opt.on .ck{opacity:1}
.dd-div{height:1px;background:var(--line);margin:6px 6px}
footer{max-width:1180px;margin:0 auto;padding:14px 18px calc(34px + var(--safe-b));color:#a99e94;font-size:11.5px;line-height:1.7;text-align:center}
footer a{text-decoration:underline}
footer b{color:var(--sub)}
.foot-src{display:flex;flex-wrap:wrap;gap:6px 14px;justify-content:center;margin-bottom:9px}
.foot-src a{display:inline-flex;align-items:center;gap:5px;color:var(--brand);font-weight:700;text-decoration:none;background:var(--cream);border:1px solid #f3dcca;padding:5px 11px;border-radius:999px}
.foot-src svg{width:13px;height:13px}
</style>
</head>
<body>
<header class="hero"><div class="wrap">
  <div class="topline">
    <div>
      <h1><span class="stamp">우슐랭</span> 우체국 맛집 가이드</h1>
      <p id="subtitle"></p>
      <p class="src">출처: 부산지방우정청 「우체국 추천 맛집가이드」 2024·2025 판본 · 부산·울산·경남 37개 우체국 직원 추천</p>
    </div>
  </div>
  <div class="tabs" id="tabs"></div>
</div></header>

<div class="tools"><div class="wrap">
  <div class="searchrow">
    <label class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg><input id="q" type="search" inputmode="search" autocomplete="off" placeholder="식당·메뉴·지역·우체국 검색"></label>
    <div class="viewtog" id="viewtog">
      <button data-v="list" class="on"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>목록</button>
      <button data-v="map"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg>지도</button>
    </div>
  </div>
  <div class="chips" id="eds"></div>
  <div style="display:flex;align-items:center"><div class="chips" id="cats" style="flex:1"></div>
    <div class="dd" id="dd">
      <button class="dd-btn" id="ddBtn" type="button" aria-haspopup="true" aria-expanded="false"><svg class="lic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M3 6h18M6 12h12M10 18h4"/></svg><span id="ddLabel"></span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M6 9l6 6 6-6"/></svg></button>
      <div class="dd-panel" id="ddPanel" role="menu"></div>
    </div>
  </div>
  <div class="chips" id="gus"></div>
</div></div>

<div class="count" id="count"></div>
<main class="grid" id="grid"></main>
<div id="map"></div>
<div class="maphint" id="maphint"></div>
<button class="locate" id="locate" hidden aria-label="내 위치"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3.4"/><path d="M12 2v3.2M12 18.8V22M2 12h3.2M18.8 12H22"/><circle cx="12" cy="12" r="8"/></svg></button>
<div class="top" id="top"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 19V5M5 12l7-7 7 7"/></svg></div>
<footer id="footer"></footer>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script>
const DB=__DATA__;
const UPDATED="__UPDATED__";
const REGIONS=["부산","울산","경남","전체"];
const PALETTE=["#d2453b","#e8632c","#0e7c86","#3f51b5","#7e57c2","#2e9e5b","#b5762e","#d6457f","#7a8b27","#0a6ebd","#7a8896"];
const state={region:"부산",ed:"전체",q:"",cat:"전체",gu:"전체",sort:"def",view:"list",radius:0,loc:null};

const esc=s=>(s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const norm=s=>(s||"").toLowerCase().replace(/\s+/g,"");
const catColor=(()=>{const m={};return k=>{if(!(k in m)){m[k]=PALETTE[Object.keys(m).length%PALETTE.length]}return m[k]}})();
const regOf=(r,reg)=>reg==="전체"||r.r===reg;
const edOf=(r,ed)=>ed==="전체"||r.ed.indexOf(ed)>=0;
const rows=()=>DB.filter(r=>regOf(r,state.region)&&edOf(r,state.ed));

const PIN='<svg class="ic" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s-7-6.3-7-11a7 7 0 0114 0c0 4.7-7 11-7 11z"/><circle cx="12" cy="10" r="2.4"/></svg>';
const CLK='<svg class="ic" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>';
const FORK='<svg class="ic" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 3v7a2 2 0 002 2 2 2 0 002-2V3M7 12v9M17 3c-1.5 0-2.5 2-2.5 5s1 4 2.5 4v9"/></svg>';
const MAIL='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>';
const edPills=ed=>`<span class="eds">${ed.map(y=>`<span class="edp y${y.slice(2)}">${y}</span>`).join("")}</span>`;

// ── 현재 위치 ──
function haversine(la1,lo1,la2,lo2){const R=6371,d=x=>x*Math.PI/180;const dla=d(la2-la1),dlo=d(lo2-lo1);const a=Math.sin(dla/2)**2+Math.cos(d(la1))*Math.cos(d(la2))*Math.sin(dlo/2)**2;return 2*R*Math.asin(Math.sqrt(a))}
function distKm(r){return state.loc&&r.lat!=null?haversine(state.loc.lat,state.loc.lng,r.lat,r.lng):null}
function fmtDist(km){if(km==null)return"";return km<1?Math.round(km*1000)+"m":(km<10?km.toFixed(1):Math.round(km))+"km"}
let toastT;function toast(m){const h=document.getElementById("maphint");h.innerHTML=m;h.classList.add("show");clearTimeout(toastT);toastT=setTimeout(()=>h.classList.remove("show"),2800)}
let userMarker,userCircle;
function showUser(){if(!mapReady||!state.loc)return;const ll=[state.loc.lat,state.loc.lng];
  if(userMarker){userMarker.setLatLng(ll);userCircle.setLatLng(ll).setRadius(state.loc.acc||40)}
  else{userMarker=L.marker(ll,{icon:L.divIcon({className:"",html:'<div class="udot"></div>',iconSize:[16,16],iconAnchor:[8,8]}),zIndexOffset:2000,interactive:false}).addTo(map);
    userCircle=L.circle(ll,{radius:state.loc.acc||40,color:"#1a73e8",weight:1,fillColor:"#1a73e8",fillOpacity:.1,interactive:false}).addTo(map)}}
function locate(){
  if(!navigator.geolocation){toast("위치 정보를 가져올 수 없어요.");return}
  toast("현재 위치 확인 중…");
  navigator.geolocation.getCurrentPosition(p=>{
    state.loc={lat:p.coords.latitude,lng:p.coords.longitude,acc:p.coords.accuracy};
    document.getElementById("locate").classList.add("on");
    if(state.view==="map"){initMap();showUser();map.setView([state.loc.lat,state.loc.lng],14)}
    renderDD();render();
  },()=>{toast("위치 권한을 확인해 주세요.");let ch=false;if(state.sort==="dist"){state.sort="def";ch=true}if(state.radius>0){state.radius=0;ch=true}if(ch){renderDD();render()}},{enableHighAccuracy:true,timeout:9000,maximumAge:60000})}

const CK='<svg class="ck" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M5 12l5 5L20 6"/></svg>';
const SORTNM={def:"기본순",name:"가나다순",dist:"거리순"};
function ddLabelText(){return SORTNM[state.sort]+(state.radius>0?` · ${state.radius}km`:"")}
function renderDD(){
  let h=`<div class="dd-h">정렬</div>`;
  ["def","name","dist"].forEach(k=>h+=`<div class="dd-opt${state.sort===k?" on":""}" data-g="s" data-v="${k}"><span>${SORTNM[k]}</span>${CK}</div>`);
  h+=`<div class="dd-div"></div><div class="dd-h">📍 내 위치 기준</div>`;
  [[0,"전체"]].concat([1,3,5,10].map(n=>[n,`${n}km 이내`])).forEach(([v,lab])=>h+=`<div class="dd-opt${state.radius===v?" on":""}" data-g="r" data-v="${v}"><span>${lab}</span>${CK}</div>`);
  document.getElementById("ddPanel").innerHTML=h;
  document.getElementById("ddLabel").textContent=ddLabelText();
}
function ddOpen(o){document.getElementById("dd").classList.toggle("open",o);document.getElementById("ddBtn").setAttribute("aria-expanded",o?"true":"false")}

function tally(key){const m=new Map();rows().forEach(r=>{const v=r[key];if(v)m.set(v,(m.get(v)||0)+1)});return [...m.entries()].sort((a,b)=>b[1]-a[1])}
function buildChips(elId,key,stateKey,label){
  const el=document.getElementById(elId);
  let h=`<span class="chiplabel">${label}</span><button class="chip${state[stateKey]==="전체"?" on":""}" data-v="전체">전체<i class="ct">${rows().length}</i></button>`;
  tally(key).forEach(([v,n])=>h+=`<button class="chip${state[stateKey]===v?" on":""}" data-v="${esc(v)}">${esc(v)}<i class="ct">${n}</i></button>`);
  el.innerHTML=h;
  el.onclick=e=>{const b=e.target.closest(".chip");if(!b)return;state[stateKey]=b.dataset.v;[...el.children].forEach(c=>c.classList&&c.classList.toggle("on",c===b));render()};
}
function buildEdChips(){
  const el=document.getElementById("eds");
  const opts=[["전체","전체"],["2024","2024"],["2025","2025"]];
  let h=`<span class="chiplabel">발행</span>`;
  opts.forEach(([v,lab])=>{const n=DB.filter(r=>regOf(r,state.region)&&edOf(r,v)).length;
    h+=`<button class="chip${state.ed===v?" on":""}" data-v="${v}">${lab}<i class="ct">${n}</i></button>`});
  el.innerHTML=h;
  el.onclick=e=>{const b=e.target.closest(".chip");if(!b)return;state.ed=b.dataset.v;
    buildEdChips();buildTabs();buildChips("cats","c","cat","종류");buildChips("gus","g","gu","지역");render()};
}
function filtered(){
  const q=norm(state.q);
  let list=rows().filter(r=>{
    if(state.cat!=="전체"&&r.c!==state.cat)return false;
    if(state.gu!=="전체"&&r.g!==state.gu)return false;
    if(state.radius>0&&state.loc){const dk=distKm(r);if(dk==null||dk>state.radius)return false}
    if(q){const hay=norm(r.n+r.a+r.m+r.c+r.g+r.o+r.d);if(!hay.includes(q))return false}
    return true;
  });
  const s=state.sort;
  if(s==="dist"&&state.loc)list=[...list].sort((a,b)=>(distKm(a)??1e9)-(distKm(b)??1e9));
  else if(s==="name")list=[...list].sort((a,b)=>a.n.localeCompare(b.n,"ko"));
  return list;
}
function card(r){
  const col=catColor(r.c);
  const tel=(r.p||"").replace(/[^0-9+]/g,"");
  const mapq=encodeURIComponent(r.n+" "+r.a);
  const dk=distKm(r);
  return `<article class="card"><div class="ctop"><span class="cat" style="background:${col}">${esc(r.c)}</span><span class="ctr">${edPills(r.ed)}<span class="gu">${esc(r.g)}</span></span></div>
  <div class="body">
  <span class="office">${MAIL}${esc(r.o)} 추천</span>
  <div class="name">${esc(r.n)}</div>
  ${r.m?`<div class="hl">${FORK}<span>${esc(r.m)}</span></div>`:""}
  ${r.d?`<div class="desc">${esc(r.d)}</div>`:""}
  <div class="row">${PIN}<span>${dk!=null?`<span class="dist">${fmtDist(dk)}</span> · `:""}${esc(r.a)}</span></div>
  ${r.h?`<div class="row">${CLK}<span>${esc(r.h)}</span></div>`:""}
  <div class="acts">${tel?`<a class="act call" href="tel:${tel}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3 19.5 19.5 0 01-6-6 19.8 19.8 0 01-3-8.6A2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.6a2 2 0 01-.5 2.1L8 9.6a16 16 0 006 6l1.2-1.2a2 2 0 012.1-.5c.8.3 1.7.5 2.6.6a2 2 0 011.7 2z"/></svg>전화</a>`:""}
  <a class="act" href="https://map.kakao.com/?q=${mapq}" target="_blank" rel="noopener">${PIN.replace('class="ic" ','')}카카오맵</a>
  <a class="act" href="https://map.naver.com/p/search/${mapq}" target="_blank" rel="noopener">네이버</a></div></div></article>`;
}

let map,cluster,mapReady=false;
function initMap(){if(mapReady)return;map=L.map("map",{zoomControl:true}).setView([35.16,129.07],11);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",{attribution:'© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> · © <a href="https://carto.com/">CARTO</a>',subdomains:"abcd",maxZoom:19}).addTo(map);
  cluster=L.markerClusterGroup({maxClusterRadius:46,showCoverageOnHover:false});map.addLayer(cluster);mapReady=true}
function popHtml(r){const tel=(r.p||"").replace(/[^0-9+]/g,"");const mapq=encodeURIComponent(r.n+" "+r.a);const dk=distKm(r);
  return `<div class="pop"><div class="pbody"><span class="poff">${MAIL}${esc(r.o)} 추천</span><div class="pn">${esc(r.n)}</div><div class="ped">📖 ${r.ed.join("·")} 수록 · ${esc(r.c)} · ${esc(r.g)}</div>${r.m?`<div class="pm">${esc(r.m)}</div>`:""}<div class="pa">${dk!=null?`<span class="dist">${fmtDist(dk)}</span> · `:""}${esc(r.a)}${r.h?"<br>"+esc(r.h):""}</div><div class="pacts">${tel?`<a class="call" href="tel:${tel}">전화</a>`:""}<a href="https://map.kakao.com/?q=${mapq}" target="_blank" rel="noopener">카카오맵</a><a href="https://map.naver.com/p/search/${mapq}" target="_blank" rel="noopener">네이버</a></div></div></div>`}
function renderMap(list){initMap();cluster.clearLayers();const ms=[];
  list.forEach(r=>{if(r.lat==null||r.lng==null)return;const col=catColor(r.c);
    const m=L.marker([r.lat,r.lng],{icon:L.divIcon({className:"",html:`<div class="mk" style="background:${col}"></div>`,iconSize:[16,16],iconAnchor:[8,15],popupAnchor:[0,-14]})});
    m.bindPopup(popHtml(r));ms.push(m)});
  cluster.addLayers(ms);setTimeout(()=>map.invalidateSize(),60);
  if(ms.length){try{const b=cluster.getBounds();b.isValid()&&map.fitBounds(b.pad(.12),{maxZoom:15})}catch(e){}}}

function render(){const list=filtered();document.getElementById("count").innerHTML=`<b>${list.length}</b>곳`;
  if(state.view==="map")renderMap(list);
  else document.getElementById("grid").innerHTML=list.length?list.map(card).join(""):`<div class="empty"><div class="em">🔍</div><p>조건에 맞는 맛집이 없어요.<br>검색어·필터·지역·발행연도를 바꿔보세요.</p></div>`}

function setToolsH(){document.documentElement.style.setProperty("--toolsH",(document.querySelector(".tools").offsetHeight+document.querySelector(".hero").offsetHeight)+"px")}
function buildTabs(){document.getElementById("tabs").innerHTML=REGIONS.map(k=>{const n=DB.filter(r=>regOf(r,k)&&edOf(r,state.ed)).length;return `<button class="tab${k===state.region?" on":""}" data-s="${k}">${k}<span class="tn">${n}</span></button>`}).join("")}
function subtitle(){const n=rows().length;const edtxt=state.ed==="전체"?"2024·2025":state.ed+"년판";const rtxt=state.region==="전체"?"부산·울산·경남":state.region;return `${rtxt} 우체국 추천 맛집 ${n}곳 · ${edtxt} · 종류·지역으로 찾아보세요`}

function switchRegion(reg){state.region=reg;state.cat="전체";state.gu="전체";state.q="";document.getElementById("q").value="";
  document.getElementById("subtitle").textContent=subtitle();
  buildTabs();buildEdChips();buildChips("cats","c","cat","종류");buildChips("gus","g","gu","지역");
  if(mapReady)try{map.closePopup()}catch(e){}
  render();window.scrollTo({top:0,behavior:"instant"});setToolsH()}
function setView(v){state.view=v;document.querySelectorAll("#viewtog button").forEach(b=>b.classList.toggle("on",b.dataset.v===v));
  document.getElementById("grid").classList.toggle("hidden",v==="map");document.getElementById("map").classList.toggle("show",v==="map");
  document.getElementById("locate").hidden=(v!=="map");
  render();
  if(v==="map"){if(state.loc)showUser();toast("핀을 누르면 정보가 나와요")}}

let t;document.getElementById("q").addEventListener("input",e=>{clearTimeout(t);state.q=e.target.value;t=setTimeout(()=>{render();document.getElementById("subtitle").textContent=subtitle()},120)});
document.getElementById("ddBtn").addEventListener("click",e=>{e.stopPropagation();ddOpen(!document.getElementById("dd").classList.contains("open"))});
document.getElementById("ddPanel").addEventListener("click",e=>{e.stopPropagation();const o=e.target.closest(".dd-opt");if(!o)return;
  const g=o.dataset.g,v=o.dataset.v;let need=false;
  if(g==="s"){state.sort=v;if(v==="dist"&&!state.loc)need=true}
  else{state.radius=+v;if(+v>0&&!state.loc)need=true}
  renderDD();if(need)locate();else render()});
document.addEventListener("click",e=>{if(!e.target.closest("#dd"))ddOpen(false)});
document.getElementById("locate").addEventListener("click",()=>{if(state.sort==="def")state.sort="dist";renderDD();locate()});
document.getElementById("viewtog").addEventListener("click",e=>{const b=e.target.closest("button");if(b)setView(b.dataset.v)});
document.getElementById("tabs").addEventListener("click",e=>{const b=e.target.closest(".tab");if(b&&b.dataset.s!==state.region)switchRegion(b.dataset.s);document.getElementById("subtitle").textContent=subtitle()});
const topBtn=document.getElementById("top");addEventListener("scroll",()=>topBtn.classList.toggle("show",state.view==="list"&&scrollY>600),{passive:true});
topBtn.addEventListener("click",()=>scrollTo({top:0,behavior:"smooth"}));addEventListener("resize",setToolsH);

document.getElementById("footer").innerHTML=`<div class="foot-src">
  <a href="source/woomeb-guide-2024.pdf" target="_blank" rel="noopener">${MAIL}2024년판 원문 PDF</a>
  <a href="source/woomeb-guide-2025.pdf" target="_blank" rel="noopener">${MAIL}2025년판 원문 PDF</a>
  <a href="https://www.koreapost.go.kr/user/bbs/638/98/1932/bbsDataView/100081301.do" target="_blank" rel="noopener">📮 부산지방우정청 안내</a>
</div>
<b>우슐랭(우체국+미슐랭)</b> · 부산지방우정청 「우체국 추천 맛집가이드」 2024(발행 2024.05)·2025(발행 2025.03) 판본 통합 · 부산·울산·경남 37개 우체국 직원 추천<br>각 식당의 <b>2024/2025</b> 배지는 해당 연도 가이드 수록 여부 · 공개 자료 정리본으로 실제와 다를 수 있어요(방문 전 영업시간·휴무 확인) · 종류 자동분류 · 좌표 © Kakao · 지도 © OpenStreetMap·CARTO · 갱신 ${UPDATED}`;
document.getElementById("subtitle").textContent=subtitle();
buildTabs();buildEdChips();renderDD();buildChips("cats","c","cat","종류");buildChips("gus","g","gu","지역");render();setToolsH();
</script>
</body>
</html>"""

out = (HTML.replace("__DATA__", data_js).replace("__TOTAL__", str(total)).replace("__UPDATED__", updated))
with open("index.html", "w", encoding="utf-8") as f:
    f.write(out)
print(f"index.html 생성 ({len(out):,} bytes)")
