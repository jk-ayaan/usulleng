#!/usr/bin/env python3
"""2024·2025 우체국 맛집가이드 PDF 2개를 파싱·병합 → data/restaurants.json.
각 식당에 editions(["2024"]/["2025"]/["2024","2025"]) 태그. 표시정보는 최신(2025) 우선.
기존 data/restaurants.json 의 좌표를 name+구 키로 시드(재지오코딩 최소화)."""
import fitz, re, json, os
from collections import Counter

hdr_re = re.compile(r"추천\s*\d+")
PDFS = {"2024": "raw/guide_2024.pdf", "2025": "raw/guide_2025.pdf"}

def raw_blocks(pg):
    out = []
    for b in pg.get_text("dict")["blocks"]:
        if "lines" not in b: continue
        raw = " ".join("".join(s["text"] for s in l["spans"]) for l in b["lines"])
        if not raw.strip(): continue
        size = max(s["size"] for l in b["lines"] for s in l["spans"])
        x0, y0, x1, y1 = b["bbox"]
        out.append((round(size, 1), (x0+x1)/2, (y0+y1)/2, raw))
    return out

def _c(s): return re.sub(r"\s+", " ", s).strip()

def parse(path):
    """내용 기반 분류 — 2024(설명 9pt)·2025(설명 8pt) 레이아웃 차이 흡수."""
    doc = fitz.open(path); cards = []
    for pno in range(doc.page_count):
        pg = doc[pno]; W = pg.rect.width; H = pg.rect.height
        bs = raw_blocks(pg)
        heads = [b for b in bs if hdr_re.search(b[3]) and b[0] < 7.6 and len(b[3]) < 40 and b[1] < W-30]
        for (sz, cx, cy, txt) in heads:
            left = cx < W/2; top = cy < H/2
            q = [b for b in bs if (b[1] < W/2) == left and (b[2] < H/2) == top and b[1] < W-30 and b[2] < H-45]
            name = next((_c(b[3]) for b in q if b[0] >= 14), "")
            # 후보 정보블록: 7.5~13pt(8pt 상세 + 9pt 설명), 이름/헤더 제외, y순
            cand = sorted([b for b in q if 7.5 <= b[0] < 13 and not hdr_re.search(b[3])], key=lambda b: b[2])
            addr = phone = hours = menu_raw = desc = ""
            for sz2, bx, by, raw in cand:
                c = _c(raw)
                if not addr and re.match(r"(부산광역시|울산광역시|경상남도|부산 |울산 |경남 )", c): addr = c
                elif not phone and re.match(r"0\d{1,3}-\d{3,4}-\d{4}", c): phone = c
                elif not hours and re.search(r"\d{1,2}:\d{2}|연중무휴|휴무|브레이크", c): hours = c
                elif not menu_raw and ("₩" in raw or "\\" in raw or re.search(r"\d{1,3},\d{3}", raw)): menu_raw = raw
                elif not desc and len(c) >= 6: desc = c
            cards.append(dict(office=_c(txt), name=name, desc=desc,
                              menu_raw=menu_raw, addr=addr, phone=phone, hours=hours))
    return cards

# ── 정제 헬퍼 ──
OFFICE_GU = {"부산연제우체국": "연제구", "동부산우체국": "기장군", "남부산우체국": "남구"}
BUSAN_GU = {"중구","서구","동구","영도구","부산진구","동래구","남구","북구","해운대구","사하구","금정구","강서구","연제구","수영구","사상구","기장군"}
def region(a): return "부산" if a.startswith("부산") else "울산" if a.startswith("울산") else "경남"
def district(a, off):
    m = re.match(r"(?:부산광역시|울산광역시|경상남도|부산|울산|경남)\s*(\S+?[시군구])", a)
    g = m.group(1) if m else ""
    if region(a) == "부산" and g not in BUSAN_GU: g = OFFICE_GU.get(off, g)
    return g
def clean_office(o):
    o = re.sub(r"\s*추천\s*\d+\s*$", "", o); o = re.sub(r"\s*\(.*?\)\s*", "", o)
    return o.replace("헤운대", "해운대").strip()
def office_area(o):
    m = re.search(r"\((.*?)\)", o); return m.group(1) if m else ""
def fmt_menu(raw):
    s = raw.replace("\\", "₩")
    parts = re.split(r"\s*ㅣ\s*|\s{2,}", s)
    parts = [re.sub(r"\s+", " ", p).strip() for p in parts if p.strip()]
    return " · ".join(parts)
CATS = [
 ("카페·디저트", r"카페|커피|아메리카노|아인슈페너|라떼|에이드|스무디|디저트|베이커리|제과|빵집|케이크|로스터|티라미수|와플|빙수|아이스크림|도넛|도너츠|스콘|마카롱|크로플|까눌레|꽈배기|콩방"),
 ("면류",       r"냉면|밀면|국수|칼국수|막국수|우동|소바|짜장|짬뽕|쫄면|메밀|면옥|국시"),
 ("국밥·탕",    r"국밥|순대국|곰탕|설렁탕|추어탕|해장국|삼계탕|매운탕|지리|전골|샤브|뼈해장|갈비탕|육개장|보양식|감자탕|콩나물국밥|탕반"),
 ("회·해산물",  r"물회|회덮|회센|회타운|모듬회|활어|초밥|스시|해산물|해물|조개|꼬막|장어|문어|낙지|아구|아귀|복국|복어|대게|멍게|전복|굴요리|미역|생선|연어|참치|광어|도다리|붕장어|곰장어|가자미|쭈꾸미|꽃게|오징어|횟집|회\b"),
 ("고기·구이",  r"삼겹|구이|불고기|갈비|돼지|한우|소고기|곱창|막창|대창|족발|보쌈|수육|오리|닭갈비|양꼬치|숯불|육회|스테이크|정육|고깃|식육|흑돼지|소금구이"),
 ("중식",       r"중식|중국집|중화|마라|탕수육|딤섬|차이나|반점|짜장면"),
 ("일식·돈카츠",r"돈카츠|돈까스|라멘|이자카야|텐동|규동|일식|사케|스시"),
 ("양식·파스타",r"파스타|피자|이탈리|레스토랑|버거|브런치|리조또|감바스|비스트로|스테이크하우스"),
 ("치킨·호프",  r"치킨|닭강정|통닭|호프|맥주|포차|펍\b"),
 ("분식",       r"떡볶이|김밥|분식|순대\b|튀김|어묵|만두|토스트|핫도그|호떡"),
 ("한식·백반",  r"한식|백반|정식|쌈밥|보리밥|비빔밥|찌개|파전|전집|반찬|가정식|솥밥|곤드레|두부|청국장|된장|한정식|밥상|집밥|옻닭|오리|황태|굴비|코다리"),
]
def categorize(name, menu, desc):
    blob = f"{name} {menu} {desc}"
    for cat, pat in CATS:
        if re.search(pat, blob): return cat
    return "기타"

def norm(s): return re.sub(r"\s+", "", s or "")
def to_rec(c):
    a = c["addr"].strip(); off = clean_office(c["office"])
    return dict(name=c["name"].strip(), region=region(a), district=district(a, off),
                office=off, office_area=office_area(c["office"]),
                category=categorize(c["name"], fmt_menu(c["menu_raw"]), c["desc"]),
                desc=re.sub(r"\s+", " ", c["desc"]).strip(), menu=fmt_menu(c["menu_raw"]),
                addr=a, phone=c["phone"].strip(), hours=re.sub(r"\s+", " ", c["hours"]).strip())

c24 = [to_rec(c) for c in parse(PDFS["2024"]) if c["name"] and c["addr"]]
c25 = [to_rec(c) for c in parse(PDFS["2025"]) if c["name"] and c["addr"]]
key = lambda r: norm(r["name"]) + "|" + r["district"]
m25 = {key(r): r for r in c25}; m24 = {key(r): r for r in c24}

# 기존 좌표 시드
seed = {}
if os.path.exists("data/restaurants.json"):
    for r in json.load(open("data/restaurants.json")):
        if r.get("lat") is not None:
            seed[norm(r["name"]) + "|" + r["district"]] = (r["lat"], r["lng"], r.get("geo", "address"))

union = []; seen = set()
def emit(base, eds):
    k = key(base)
    rec = dict(base); rec["editions"] = eds
    if k in seed: rec["lat"], rec["lng"], rec["geo"] = (*seed[k][:2], seed[k][2])
    else: rec["lat"] = rec["lng"] = None; rec["geo"] = None
    union.append(rec); seen.add(k)

for r in c24:  # 2024 순서 유지, 표시정보는 2025 있으면 최신으로
    k = key(r); eds = ["2024"] + (["2025"] if k in m25 else [])
    emit(m25.get(k, r), eds)
for r in c25:  # 2025 신규
    if key(r) not in seen: emit(r, ["2025"])

for i, r in enumerate(union, 1): r["id"] = i
json.dump(union, open("data/restaurants.json", "w"), ensure_ascii=False, indent=1)
ed = Counter(tuple(r["editions"]) for r in union)
print(f"병합 {len(union)}곳 | 양쪽 {ed[('2024','2025')]} · 2024만 {ed[('2024',)]} · 2025만 {ed[('2025',)]}")
print("지역:", Counter(r["region"] for r in union))
print("좌표 시드됨:", sum(1 for r in union if r['lat'] is not None), "· 지오코딩 필요:", sum(1 for r in union if r['lat'] is None))
print("음식종류:", Counter(r["category"] for r in union).most_common())
