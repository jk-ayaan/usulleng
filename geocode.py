#!/usr/bin/env python3
"""Kakao Local API 로 data/restaurants.json 의 주소 → 좌표(lat/lng) 채우기.
사용:  KAKAO_REST_KEY=발급키 .venv/bin/python geocode.py
- 1차: 주소검색(address.json)  2차 실패 시: 키워드검색(keyword.json, 식당명+구)
- 결과는 raw/geocode_cache.json 에 캐시(재실행 시 재사용)
"""
import json, os, sys, time, urllib.parse, urllib.request, re

KEY = os.environ.get("KAKAO_REST_KEY", "").strip()
if not KEY:
    sys.exit("환경변수 KAKAO_REST_KEY 가 필요합니다.")

HDR = {"Authorization": f"KakaoAK {KEY}"}
DATA = "data/restaurants.json"
CACHE = "raw/geocode_cache.json"

def _get(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def by_address(addr):
    # 도로명 본번지까지만 (층/호/건물명 제거) 로 검색 정확도 ↑
    q = re.sub(r"\s*,.*$", "", addr)
    q = re.sub(r"\s*(지하\s*)?\d*\s*층.*$", "", q)
    q = re.sub(r"\s+\S*\d+호.*$", "", q).strip()
    url = "https://dapi.kakao.com/v2/local/search/address.json?" + urllib.parse.urlencode({"query": q})
    docs = _get(url).get("documents", [])
    if docs:
        d = docs[0]
        return float(d["y"]), float(d["x"]), "address"
    return None

def by_keyword(name, district, addr):
    q = f"{district} {name}".strip()
    url = "https://dapi.kakao.com/v2/local/search/keyword.json?" + urllib.parse.urlencode({"query": q, "size": 1})
    docs = _get(url).get("documents", [])
    if docs:
        d = docs[0]
        return float(d["y"]), float(d["x"]), "keyword"
    return None

def main():
    rows = json.load(open(DATA))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    ok = miss = 0
    for r in rows:
        k = r["addr"]
        if k in cache and cache[k]:
            r["lat"], r["lng"] = cache[k]["lat"], cache[k]["lng"]
            r["geo"] = cache[k]["geo"]; ok += 1; continue
        res = None
        try:
            res = by_address(r["addr"]) or by_keyword(r["name"], r["district"], r["addr"])
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
    addr_n = sum(1 for r in rows if r.get("geo") == "address")
    kw_n = sum(1 for r in rows if r.get("geo") == "keyword")
    print(f"\n좌표 완료: {ok}/{len(rows)}  (주소 {addr_n} · 키워드 {kw_n} · 실패 {miss})")

if __name__ == "__main__":
    main()
