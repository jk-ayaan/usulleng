#!/usr/bin/env python3
"""우슐랭(우체국 맛집 가이드) 투톤 앱 아이콘 생성 → SVG + PNG(rsvg-convert)."""
import math, subprocess, os

RED  = "#D6392B"   # 우체국 레드
CREAM= "#FFF4EA"   # 크림 화이트
SZ   = 1024
os.makedirs("icon", exist_ok=True)

def star_points(cx, cy, R, r, n=5, rot=-90):
    pts=[]
    for i in range(n*2):
        ang=math.radians(rot + i*180.0/n)
        rad=R if i%2==0 else r
        pts.append(f"{cx+rad*math.cos(ang):.1f},{cy+rad*math.sin(ang):.1f}")
    return " ".join(pts)

def squircle(fill):
    return f'<rect x="0" y="0" width="{SZ}" height="{SZ}" rx="224" ry="224" fill="{fill}"/>'

# Material "place" teardrop pin (viewBox 24); transform to canvas
PIN_PATH="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"
PIN_G='<g transform="translate(176,178) scale(28)">'  # head center -> (512,430), tip -> (512,794)

def icon_pin_star():
    star=star_points(512,424,118,47)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SZ}" height="{SZ}" viewBox="0 0 {SZ} {SZ}">
{squircle(RED)}
{PIN_G}<path d="{PIN_PATH}" fill="{CREAM}"/></g>
<polygon points="{star}" fill="{RED}"/>
</svg>'''

def icon_pin_utensil():
    # 수저: 왼쪽 숟가락 + 오른쪽 젓가락 2개 (핀 머리 안, 세로 배치)
    g='<g fill="{0}">'.format(RED)
    spoon=('<ellipse cx="468" cy="378" rx="34" ry="44"/>'
           '<rect x="458" y="402" width="20" height="92" rx="10"/>')
    cs=('<rect x="536" y="352" width="17" height="142" rx="8"/>'
        '<rect x="566" y="352" width="17" height="142" rx="8"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SZ}" height="{SZ}" viewBox="0 0 {SZ} {SZ}">
{squircle(RED)}
{PIN_G}<path d="{PIN_PATH}" fill="{CREAM}"/></g>
{g}{spoon}{cs}</g>
</svg>'''

def icon_badge_star():
    star=star_points(512,520,232,92)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SZ}" height="{SZ}" viewBox="0 0 {SZ} {SZ}">
{squircle(RED)}
<circle cx="512" cy="512" r="372" fill="none" stroke="{CREAM}" stroke-width="34"/>
<polygon points="{star}" fill="{CREAM}"/>
</svg>'''

variants={"pin_star":icon_pin_star(),"pin_utensil":icon_pin_utensil(),"badge_star":icon_badge_star()}
for name,svg in variants.items():
    open(f"icon/{name}.svg","w").write(svg)
    for px in (1024,512):
        out=f"icon/{name}_{px}.png"
        subprocess.run(["rsvg-convert","-w",str(px),"-h",str(px),"-o",out,f"icon/{name}.svg"],check=True)
    print("rendered",name)

# 비교용 contact sheet (3개 가로 배열 + 라벨)
labels={"pin_star":"1. 핀+별 (추천)","pin_utensil":"2. 핀+수저","badge_star":"3. 뱃지+별"}
cw,ch,pad,top=360,360,56,70
W=cw*3+pad*4; H=ch+top+90
cells=[]
for i,n in enumerate(["pin_star","pin_utensil","badge_star"]):
    x=pad+i*(cw+pad); y=top
    cells.append(f'<image x="{x}" y="{y}" width="{cw}" height="{ch}" href="{n}_1024.png"/>')
    cells.append(f'<text x="{x+cw/2}" y="{y+ch+44}" font-family="AppleSDGothicNeo,Apple SD Gothic Neo,sans-serif" font-size="30" font-weight="700" fill="#222" text-anchor="middle">{labels[n]}</text>')
sheet=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="#FAFAFA"/>
<text x="{W/2}" y="46" font-family="AppleSDGothicNeo,sans-serif" font-size="34" font-weight="800" fill="#111" text-anchor="middle">우슐랭 · 우체국 맛집 가이드 앱 아이콘 (투톤)</text>
{"".join(cells)}
</svg>'''
open("icon/_sheet.svg","w").write(sheet.replace('href=','xlink:href='))
subprocess.run(["rsvg-convert","-o","icon/_sheet.png","icon/_sheet.svg"],cwd=".",check=True)
print("done")
