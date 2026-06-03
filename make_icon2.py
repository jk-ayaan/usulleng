#!/usr/bin/env python3
"""우편 아이콘 + 'Food' 글자 투톤 앱 아이콘 시안."""
import subprocess, os, math
RED="#D6392B"; CREAM="#FFF4EA"; SZ=1024
FONT="Avenir Next, Helvetica Neue, Arial, sans-serif"
os.makedirs("icon", exist_ok=True)
def squircle(f): return f'<rect width="{SZ}" height="{SZ}" rx="224" fill="{f}"/>'

def envelope_filled():
    # 크림 봉투 + 빨강 플랩선 + 빨강 'Food'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SZ}" height="{SZ}" viewBox="0 0 {SZ} {SZ}">
{squircle(RED)}
<rect x="176" y="312" width="672" height="408" rx="40" fill="{CREAM}"/>
<polyline points="176,328 512,548 848,328" fill="none" stroke="{RED}" stroke-width="30" stroke-linejoin="round" stroke-linecap="round"/>
<text x="512" y="676" font-family="{FONT}" font-size="150" font-weight="800" fill="{RED}" text-anchor="middle" letter-spacing="1">Food</text>
</svg>'''

def stamp():
    body=f'<rect x="222" y="222" width="580" height="580" rx="26" fill="{CREAM}"/>'
    holes=[]
    edge=580; x0=222; y0=222; n=12; step=edge/n
    for i in range(n+1):
        p=x0+i*step
        for cx,cy in [(p,y0),(p,y0+edge),(x0,p),(x0+edge,p)]:
            holes.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="19" fill="{RED}"/>')
    star_pts=[]
    for i in range(10):
        a=math.radians(-90+i*36); r=46 if i%2==0 else 18
        star_pts.append(f"{512+r*math.cos(a):.0f},{372+r*math.sin(a):.0f}")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SZ}" height="{SZ}" viewBox="0 0 {SZ} {SZ}">
{squircle(RED)}
{body}
{''.join(holes)}
<rect x="296" y="296" width="432" height="432" rx="10" fill="none" stroke="{RED}" stroke-width="9" stroke-dasharray="2 0" opacity="0.0"/>
<polygon points="{' '.join(star_pts)}" fill="{RED}"/>
<text x="512" y="600" font-family="{FONT}" font-size="158" font-weight="800" fill="{RED}" text-anchor="middle" letter-spacing="4">FOOD</text>
</svg>'''

def envelope_line():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SZ}" height="{SZ}" viewBox="0 0 {SZ} {SZ}">
{squircle(RED)}
<rect x="196" y="320" width="632" height="392" rx="30" fill="none" stroke="{CREAM}" stroke-width="30"/>
<polyline points="210,338 512,556 814,338" fill="none" stroke="{CREAM}" stroke-width="30" stroke-linejoin="round" stroke-linecap="round"/>
<text x="512" y="668" font-family="{FONT}" font-size="132" font-weight="800" fill="{CREAM}" text-anchor="middle" letter-spacing="1">Food</text>
</svg>'''

variants={"env_food":envelope_filled(),"stamp_food":stamp(),"envline_food":envelope_line()}
for n,svg in variants.items():
    open(f"icon/{n}.svg","w").write(svg)
    for px in (1024,512):
        subprocess.run(["rsvg-convert","-w",str(px),"-h",str(px),"-o",f"icon/{n}_{px}.png",f"icon/{n}.svg"],check=True)
    print("rendered",n)

labels={"env_food":"A. 봉투 + Food","stamp_food":"B. 우표 + FOOD","envline_food":"C. 라인봉투 + Food"}
cw=cw=360; pad=56; top=70; W=cw*3+pad*4; H=cw+top+90; cells=[]
for i,n in enumerate(["env_food","stamp_food","envline_food"]):
    x=pad+i*(cw+pad); y=top
    cells.append(f'<image x="{x}" y="{y}" width="{cw}" height="{cw}" xlink:href="{n}_1024.png"/>')
    cells.append(f'<text x="{x+cw/2}" y="{y+cw+44}" font-family="AppleSDGothicNeo,sans-serif" font-size="30" font-weight="700" fill="#222" text-anchor="middle">{labels[n]}</text>')
sheet=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="#FAFAFA"/>
<text x="{W/2}" y="46" font-family="AppleSDGothicNeo,sans-serif" font-size="34" font-weight="800" fill="#111" text-anchor="middle">우편 아이콘 + Food (투톤)</text>
{''.join(cells)}</svg>'''
open("icon/_sheet2.svg","w").write(sheet)
subprocess.run(["rsvg-convert","-o","icon/_sheet2.png","icon/_sheet2.svg"],check=True)
print("done")
