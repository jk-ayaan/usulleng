#!/usr/bin/env python3
"""Kakao Local API 로 data/restaurants.json 의 주소 → 좌표(lat/lng) 채우기.
사용:  KAKAO_REST_KEY=발급키 .venv/bin/python geocode.py
- 이미 lat 있는 행은 건너뜀(시드 보존). 1차 주소검색 → 실패 시 키워드검색.
- 결과는 region 박스 안에 있어야 채택(동명이구 오매칭 방지). raw/geocode_cache.json 캐시."""
import json, os, sys, time, urllib.parse, urllib.request, re

KEY = os.environ.get("KAKAO_REST_KEY", "").strip()
if not KEY:
    sys.exit("환경변수 KAKAO_REST_KEY 가 필요합니다.")

HDR = {"Authorization": f"KakaoAK {KEY}"}
DATA = "data/restaurants.json"
CACHE = "raw/geocode_cache.json"
BBOX = {"부산": (34.95, 35.42, 128.70, 129.35),
        "울산": (35.40, 35.80, 128.95, 129.47),
        "경남": (34.55, 35.93, 127.55, 129.25)}

def inbox(region, lat, lng):
    a, b, c, d = BBOX[region]; return a <= lat <= b and c <= lng <= d

def _get(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def by_address(addr, region):
    q = re.sub(r"\s*,.*$", "", addr)
    q = re.sub(r"\s*(지하\s*)?\d*\s*층.*$", "", q)
    q = re.sub(r"\s+\S*\d+호.*$", "", q).strip()
    url = "https://dapi.kakao.com/v2/local/search/address.json?" + urllib.parse.urlencode({"query": q})
    for d in _get(url).get("documents", []):
        lat, lng = float(d["y"]), float(d["x"])
        if inbox(region, lat, lng):
            return lat, lng, "address"
    return None

def by_keyword(name, district, region):
    for q in (f"{region} {district} {name}", f"{region} {name}", f"{district} {name}"):
        url = "https://dapi.kakao.com/v2/local/search/keyword.json?" + urllib.parse.urlencode({"query": q, "size": 5})
        for d in _get(url).get("documents", []):
            lat, lng = float(d["y"]), float(d["x"])
            if inbox(region, lat, lng):
                return lat, lng, "keyword"
    return None

def main():
    rows = json.load(open(DATA))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    ok = miss = skip = 0
    for r in rows:
        if r.get("lat") is not None:  # 시드/기존 좌표 보존
            skip += 1; continue
        k = r["addr"] + "|" + r["region"]
        if k in cache and cache[k]:
            r["lat"], r["lng"], r["geo"] = cache[k]["lat"], cache[k]["lng"], cache[k]["geo"]; ok += 1; continue
        res = None
        try:
            res = by_address(r["addr"], r["region"]) or by_keyword(r["name"], r["district"], r["region"])
        except Exception as e:
            print("ERR", r["name"], e)
        time.sleep(0.05)
        if res:
            lat, lng, src = res
            r["lat"], r["lng"], r["geo"] = lat, lng, src
            cache[k] = {"lat": lat, "lng": lng, "geo": src}; ok += 1
        else:
            cache[k] = None; miss += 1
            print("MISS", r["name"], "|", r["addr"])
    json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)
    json.dump(rows, open(DATA, "w"), ensure_ascii=False, indent=1)
    have = sum(1 for r in rows if r.get("lat") is not None)
    print(f"\n좌표: 보유 {have}/{len(rows)}  (이번에 변환 {ok} · 시드/기존 {skip} · 실패 {miss})")

if __name__ == "__main__":
    main()
