"""Draws the flat topic illustrations for articles (assets/book/art-<slug>.jpg, art-<slug>-2.jpg).
Run in an empty folder: it writes SVG + PNG files and a contact sheet; copy the PNGs into assets/book as JPG. Needs rsvg-convert and Pillow."""
import subprocess, os
T='#2f6f62'; TD='#1f5247'; M='#dfe9e4'; G='#e2b35a'; GD='#b9862a'; N='#18233a'; P='#f6f3ea'; W='#ffffff'; R='#d9796a'; S1='#eec9a6'; S2='#c9966f'; S3='#a8734f'; LB='#9fc6ba'
def bg(extra=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="1200" height="800">
<defs><linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f8f6ee"/><stop offset="1" stop-color="#e3eee9"/></linearGradient></defs>
<rect width="1200" height="800" fill="url(#b)"/>{extra}'''
def ground(y=640,c='#cfe0d9'): return f'<ellipse cx="600" cy="{y+60}" rx="560" ry="70" fill="{c}" opacity=".8"/>'
def line(pts,c,w): 
    d='M'+' L'.join(f'{x:.0f},{y:.0f}' for x,y in pts)
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w:.0f}" stroke-linecap="round" stroke-linejoin="round"/>'
def person(cx,base,h,shirt=T,hair=N,skin=S1,pants=N,pose='stand',la=None,ra=None,face='calm',dir=1,hairstyle='short',coat=None):
    """la/ra: list of points relative (dx,dy from shoulder) for left/right arm joints. dir: 1 legs to the right when sitting."""
    r=h*0.105; o=[]
    top=base-h; hy=top+r; sh=hy+r*1.55; tw=h*0.30; hip=sh+h*0.36
    if pose=='sit':
        o.append(line([(cx-tw*0.22,hip),(cx-tw*0.22+dir*h*0.26,hip),(cx-tw*0.22+dir*h*0.26,base)],pants,h*0.085))
        o.append(line([(cx+tw*0.22,hip),(cx+tw*0.22+dir*h*0.27,hip+4),(cx+tw*0.22+dir*h*0.27,base)],pants,h*0.085))
    elif pose=='kneel':
        o.append(line([(cx,hip),(cx+dir*h*0.2,base-h*0.04),(cx-dir*h*0.08,base-h*0.04)],pants,h*0.09))
    else:
        o.append(line([(cx-tw*0.22,hip),(cx-tw*0.24,base)],pants,h*0.085)); o.append(line([(cx+tw*0.22,hip),(cx+tw*0.24,base)],pants,h*0.085))
    # torso
    o.append(f'<rect x="{cx-tw/2:.0f}" y="{sh:.0f}" width="{tw:.0f}" height="{hip-sh+h*0.03:.0f}" rx="{tw*0.32:.0f}" fill="{shirt}"/>')
    if coat: o.append(f'<path d="M{cx-tw/2:.0f},{sh+tw*0.3:.0f} L{cx-tw/2:.0f},{hip+h*0.12:.0f} L{cx-4:.0f},{hip+h*0.12:.0f} L{cx-4:.0f},{sh+10:.0f} Z M{cx+tw/2:.0f},{sh+tw*0.3:.0f} L{cx+tw/2:.0f},{hip+h*0.12:.0f} L{cx+4:.0f},{hip+h*0.12:.0f} L{cx+4:.0f},{sh+10:.0f} Z" fill="{coat}"/>')
    aw=h*0.07
    for side,arm in ((-1,la),(1,ra)):
        sx=cx+side*tw*0.42; sy=sh+h*0.04
        if arm is None: arm=[(side*h*0.03,h*0.3)]
        pts=[(sx,sy)]+[(sx+dx,sy+dy) for dx,dy in arm]
        o.append(line(pts,coat or shirt,aw)); hx,hy2=pts[-1]; o.append(f'<circle cx="{hx:.0f}" cy="{hy2:.0f}" r="{aw*0.62:.0f}" fill="{skin}"/>')
    # neck + head
    o.append(f'<rect x="{cx-r*0.32:.0f}" y="{hy+r*0.7:.0f}" width="{r*0.64:.0f}" height="{r:.0f}" fill="{skin}"/>')
    if hairstyle=='long': o.append(f'<path d="M{cx-r*1.15:.0f},{hy:.0f} a{r*1.15:.0f},{r*1.2:.0f} 0 0 1 {r*2.3:.0f},0 v{r*1.9:.0f} h-{r*2.3:.0f} z" fill="{hair}"/>')
    o.append(f'<circle cx="{cx:.0f}" cy="{hy:.0f}" r="{r:.0f}" fill="{skin}"/>')
    if hairstyle=='hijab':
        o.append(f'<path d="M{cx-r*1.12:.0f},{hy+r*0.2:.0f} a{r*1.12:.0f},{r*1.25:.0f} 0 0 1 {r*2.24:.0f},0 l{r*0.2:.0f},{r*1.6:.0f} h-{r*2.64:.0f} z" fill="{hair}"/><ellipse cx="{cx:.0f}" cy="{hy+r*0.12:.0f}" rx="{r*0.72:.0f}" ry="{r*0.82:.0f}" fill="{skin}"/>')
    else:
        o.append(f'<path d="M{cx-r*1.02:.0f},{hy-r*0.1:.0f} a{r*1.02:.0f},{r*1.08:.0f} 0 0 1 {r*2.04:.0f},0 q-{r*0.5:.0f},-{r*0.55:.0f} -{r*1.02:.0f},-{r*0.5:.0f} q-{r*0.6:.0f},0 -{r*1.02:.0f},{r*0.5:.0f} z" fill="{hair}"/>')
    ey=hy+r*0.12
    if face=='calm':
        o.append(f'<path d="M{cx-r*0.48:.0f},{ey:.0f} q{r*0.14:.0f},{r*0.14:.0f} {r*0.28:.0f},0 M{cx+r*0.2:.0f},{ey:.0f} q{r*0.14:.0f},{r*0.14:.0f} {r*0.28:.0f},0" stroke="{N}" stroke-width="{max(2,r*0.09):.0f}" fill="none" stroke-linecap="round"/><path d="M{cx-r*0.25:.0f},{ey+r*0.42:.0f} q{r*0.25:.0f},{r*0.2:.0f} {r*0.5:.0f},0" stroke="{N}" stroke-width="{max(2,r*0.09):.0f}" fill="none" stroke-linecap="round"/>')
    elif face=='sad':
        o.append(f'<circle cx="{cx-r*0.34:.0f}" cy="{ey:.0f}" r="{r*0.09:.1f}" fill="{N}"/><circle cx="{cx+r*0.34:.0f}" cy="{ey:.0f}" r="{r*0.09:.1f}" fill="{N}"/><path d="M{cx-r*0.25:.0f},{ey+r*0.55:.0f} q{r*0.25:.0f},-{r*0.2:.0f} {r*0.5:.0f},0" stroke="{N}" stroke-width="{max(2,r*0.09):.0f}" fill="none" stroke-linecap="round"/>')
    else:
        o.append(f'<circle cx="{cx-r*0.34:.0f}" cy="{ey:.0f}" r="{r*0.09:.1f}" fill="{N}"/><circle cx="{cx+r*0.34:.0f}" cy="{ey:.0f}" r="{r*0.09:.1f}" fill="{N}"/><path d="M{cx-r*0.22:.0f},{ey+r*0.42:.0f} q{r*0.22:.0f},{r*0.18:.0f} {r*0.44:.0f},0" stroke="{N}" stroke-width="{max(2,r*0.09):.0f}" fill="none" stroke-linecap="round"/>')
    return ''.join(o)
def heart(x,y,s,c=R): return f'<path transform="translate({x},{y}) scale({s})" d="M0,10 C-22,-8 -12,-26 0,-12 C12,-26 22,-8 0,10 Z" fill="{c}"/>'
def bubble(x,y,w,h,c=W,tail=1): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h*0.4:.0f}" fill="{c}"/><path d="M{x+(w*0.25 if tail>0 else w*0.75):.0f},{y+h-2} l{-18*tail},{26} l{34*tail},-26 z" fill="{c}"/>'
def house(x,y,w,c,roof): return f'<rect x="{x}" y="{y}" width="{w}" height="{w*0.7:.0f}" rx="10" fill="{c}"/><path d="M{x-18},{y+6} L{x+w/2},{y-w*0.42:.0f} L{x+w+18},{y+6} Z" fill="{roof}"/><rect x="{x+w*0.4:.0f}" y="{y+w*0.3:.0f}" width="{w*0.2:.0f}" height="{w*0.4:.0f}" rx="6" fill="{P}"/><rect x="{x+w*0.12:.0f}" y="{y+w*0.18:.0f}" width="{w*0.18:.0f}" height="{w*0.18:.0f}" rx="4" fill="{P}"/>'
def chair(x,y,w,c=LB): return f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="10" fill="{c}"/><rect x="{x+8}" y="{y+20}" width="14" height="{90}" rx="6" fill="{c}"/><rect x="{x+w-22}" y="{y+20}" width="14" height="90" rx="6" fill="{c}"/>'
def sofa(x,y,w,c=LB): return f'<rect x="{x}" y="{y-110}" width="{w}" height="150" rx="34" fill="{c}"/><rect x="{x-26}" y="{y-50}" width="{w+52}" height="110" rx="30" fill="#8ab8aa"/><rect x="{x+10}" y="{y-36}" width="{w-20}" height="50" rx="20" fill="{M}"/>'
def battery(x,y,w,level,c): return f'<rect x="{x}" y="{y}" width="{w}" height="{w*0.5:.0f}" rx="12" fill="{W}" stroke="{N}" stroke-width="7"/><rect x="{x+w}" y="{y+w*0.16:.0f}" width="12" height="{w*0.18:.0f}" rx="4" fill="{N}"/><rect x="{x+10}" y="{y+10}" width="{(w-20)*level:.0f}" height="{w*0.5-20:.0f}" rx="6" fill="{c}"/>'
def plant(x,y,s=1): return f'<g transform="translate({x},{y}) scale({s})"><path d="M0,0 C-50,-40 -40,-110 0,-130 C40,-110 50,-40 0,0Z" fill="{T}"/><path d="M0,0 C-70,-10 -90,-60 -70,-90 C-30,-80 -5,-40 0,0Z" fill="#4c8f80"/><path d="M0,0 C70,-10 90,-60 70,-90 C30,-80 5,-40 0,0Z" fill="#4c8f80"/><path d="M-34,0 h68 l-10,60 h-48 z" fill="{GD}"/></g>'
def sun(x,y,r): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{G}" opacity=".9"/><circle cx="{x}" cy="{y}" r="{r*1.5:.0f}" fill="{G}" opacity=".18"/>'
END='</svg>'
A={}
# 1 panic hero
A['art-panic-attack-what-to-do']=bg(sun(980,150,60))+ground()+''.join(f'<circle cx="560" cy="430" r="{r}" fill="none" stroke="{R}" stroke-width="5" opacity="{o}" stroke-dasharray="14 18"/>' for r,o in((170,.55),(235,.35),(300,.2)))+chair(470,560,190)+person(560,690,330,shirt=T,pose='sit',la=[(30,60),(70,40)],ra=[(10,80),(-40,70)],face='sad',dir=-1)+heart(700,300,3.2)+line([(640,300),(672,300),(684,272),(700,330),(716,286),(728,300),(770,300)],W,7)+line([(250,300),(290,270),(330,300),(370,270)],LB,8)+line([(240,360),(280,330),(320,360)],LB,8)+END
# 1b breathing
A['art-panic-attack-what-to-do-2']=bg()+ground()+''.join(f'<circle cx="600" cy="400" r="{r}" fill="{c}" opacity="{o}"/>' for r,c,o in((300,T,.10),(225,T,.14),(150,T,.2)))+person(600,700,340,shirt=G,hair=N,pose='sit',la=[(-20,70),(30,95)],ra=[(20,70),(-30,95)],face='calm',dir=1,hairstyle='long')+chair(520,566,200)+line([(200,400),(330,400)],T,10)+f'<path d="M330,400 l-26,-18 v36 z" fill="{T}"/>'+line([(870,400),(1000,400)],GD,10)+f'<path d="M1000,400 l-26,-18 v36 z" fill="{GD}"/>'+''.join(f'<circle cx="{x}" cy="330" r="13" fill="{T}"/>' for x in(215,255,295,335))+''.join(f'<circle cx="{x}" cy="330" r="13" fill="{GD}"/>' for x in(850,886,922,958,994,1030))+END
# 2 divorce hero: parents kneeling beside child on sofa
A['art-telling-children-about-divorce']=bg(f'<rect x="120" y="120" width="170" height="210" rx="14" fill="{W}" opacity=".8"/><path d="M205,120 v210 M120,225 h170" stroke="{M}" stroke-width="8"/>')+ground(650)+sofa(400,560,400)+person(600,640,210,shirt=G,hair=S3,skin=S1,pose='sit',face='sad',dir=1,la=[(-10,50),(10,80)],ra=[(10,50),(-10,80)])+person(300,700,330,shirt=T,hair=N,skin=S2,pose='kneel',dir=1,ra=[(60,20),(150,-10)],face='calm')+person(905,700,320,shirt='#7d6a9c',hair=N,skin=S1,pose='kneel',dir=-1,la=[(-60,20),(-150,-10)],face='calm',hairstyle='hijab')+heart(600,250,2.6)+plant(1060,640,.9)+END
# 2b two homes, one love
A['art-telling-children-about-divorce-2']=bg(sun(600,150,56))+ground(650)+house(130,430,260,T,TD)+house(810,430,260,G,GD)+f'<path d="M400,640 C480,560 560,700 600,640 C640,580 720,700 800,640" fill="none" stroke="{N}" stroke-width="7" stroke-dasharray="4 20" stroke-linecap="round"/>'+person(600,690,190,shirt=R,hair=S3,pose='stand',la=[(-50,-10),(-90,-50)],ra=[(50,-10),(90,-50)],face='smile')+heart(260,330,2.2)+heart(940,330,2.2)+heart(600,400,1.6,GD)+END
# 3 people pleasing hero: carrying too many boxes
boxes=''.join(f'<rect x="{520+dx}" y="{y}" width="{w}" height="62" rx="10" fill="{c}"/>' for dx,y,w,c in((150,470,170,GD),(164,402,150,T),(142,334,165,R),(170,266,130,LB),(154,198,150,G)))
A['art-people-pleasing-saying-no']=bg()+ground()+person(600,700,330,shirt=T,hair=N,pose='stand',la=[(-20,70),(60,110)],ra=[(40,60),(110,90)],face='sad')+boxes+person(215,700,290,shirt='#7d6a9c',skin=S2,hair=N,ra=[(60,0),(120,-30)],face='smile')+f'<rect x="330" y="372" width="90" height="56" rx="10" fill="{G}"/>'+person(985,700,290,shirt=R,hair=S3,la=[(-60,0),(-120,-30)],face='smile',hairstyle='long')+f'<rect x="780" y="372" width="90" height="56" rx="10" fill="{LB}"/>'+line([(850,200),(880,176)],N,6)+line([(860,240),(896,230)],N,6)+END
# 3b boundary: calm hand up inside a soft circle
A['art-people-pleasing-saying-no-2']=bg(sun(180,150,50))+ground()+f'<circle cx="600" cy="470" r="270" fill="{T}" opacity=".10"/><circle cx="600" cy="470" r="270" fill="none" stroke="{T}" stroke-width="8" stroke-dasharray="26 18"/>'+person(600,700,340,shirt=G,hair=N,pose='stand',ra=[(70,-10),(110,-80)],face='calm',hairstyle='long')+f'<rect x="950" y="420" width="110" height="70" rx="10" fill="{GD}" opacity=".85"/><rect x="965" y="340" width="100" height="64" rx="10" fill="{R}" opacity=".85"/>'+bubble(700,170,150,96,W,1)+f'<path d="M745,206 l60,0 M745,232 l40,0" stroke="{T}" stroke-width="10" stroke-linecap="round"/>'+END
# 4 burnout hero: slumped at desk, low battery
A['art-burnout-signs-recovery']=bg(f'<circle cx="980" cy="190" r="74" fill="{W}"/><circle cx="980" cy="190" r="74" fill="none" stroke="{N}" stroke-width="8"/><path d="M980,190 V140 M980,190 L1016,212" stroke="{N}" stroke-width="8" stroke-linecap="round"/>')+ground()+person(560,700,330,shirt=T,hair=N,pose='sit',la=[(-10,60),(60,95)],ra=[(30,50),(110,90)],face='sad',dir=-1)+chair(470,566,190)+f'<rect x="560" y="520" width="520" height="26" rx="10" fill="{GD}"/><rect x="600" y="540" width="20" height="160" fill="{GD}"/><rect x="1020" y="540" width="20" height="160" fill="{GD}"/>'+f'<rect x="720" y="420" width="170" height="100" rx="10" fill="{N}"/><rect x="700" y="512" width="210" height="12" rx="6" fill="#3a4763"/>'+''.join(f'<rect x="{930+i*4}" y="{498-i*16}" width="120" height="14" rx="4" fill="{c}"/>' for i,c in enumerate((W,M,W,M,W,M)))+battery(250,180,180,.14,R)+line([(330,300),(330,330)],R,8)+END
# 4b recovery: rest, charging battery
A['art-burnout-signs-recovery-2']=bg(sun(950,170,64))+ground()+f'<rect x="200" y="330" width="70" height="330" rx="20" fill="{GD}"/><circle cx="235" cy="270" r="150" fill="{T}"/><circle cx="330" cy="330" r="100" fill="#4c8f80"/><circle cx="140" cy="340" r="90" fill="#4c8f80"/>'+person(560,700,330,shirt=G,hair=N,pose='sit',la=[(20,60),(80,70)],ra=[(20,70),(60,90)],face='calm',dir=1,hairstyle='hijab')+chair(480,566,190)+f'<path d="M640,450 h60 v50 a30,30 0 0 1 -60,0 z" fill="{W}"/><path d="M700,462 q26,6 0,30" fill="none" stroke="{W}" stroke-width="8"/><path d="M655,430 q10,-18 0,-34 M680,430 q10,-18 0,-34" stroke="{LB}" stroke-width="6" fill="none" stroke-linecap="round"/>'+battery(830,330,190,.7,T)+f'<path d="M925,350 l-26,44 h24 l-12,40 l40,-52 h-24 z" fill="{G}"/>'+END
# 5 psychiatrist vs psychologist hero
A['art-psychiatrist-vs-psychologist']=bg(f'<path d="M600,90 V720" stroke="{W}" stroke-width="10" stroke-dasharray="8 26" stroke-linecap="round"/>')+ground()+person(300,700,340,shirt=LB,hair=N,skin=S2,coat=W,la=[(-20,70),(30,90)],ra=[(40,60),(70,20)],face='smile')+f'<rect x="352" y="318" width="76" height="100" rx="8" fill="{W}" stroke="{N}" stroke-width="5"/><path d="M366,346 h48 M366,366 h48 M366,386 h30" stroke="{T}" stroke-width="6" stroke-linecap="round"/>'+f'<g transform="translate(160,200) rotate(-35)"><rect x="-56" y="-24" width="112" height="48" rx="24" fill="{R}"/><rect x="0" y="-24" width="56" height="48" rx="24" fill="{W}"/><rect x="0" y="-24" width="26" height="48" fill="{W}"/></g>'+f'<path d="M468,180 h34 v-34 h30 v34 h34 v30 h-34 v34 h-30 v-34 h-34 z" fill="{T}"/>'+person(880,700,330,shirt=G,hair=N,pose='sit',la=[(-20,60),(-60,80)],ra=[(20,60),(40,90)],face='smile',dir=-1,hairstyle='long')+chair(800,566,190)+bubble(660,170,170,100,W,-1)+bubble(880,110,190,110,T,1)+f'<path d="M700,206 h90 M700,234 h60" stroke="{T}" stroke-width="10" stroke-linecap="round"/><path d="M924,150 h100 M924,180 h70" stroke="{W}" stroke-width="10" stroke-linecap="round"/>'+END
# 5b choosing a door
def door(x,c,icon): return f'<rect x="{x}" y="250" width="210" height="400" rx="20" fill="{c}"/><rect x="{x+18}" y="268" width="174" height="382" rx="12" fill="{W}" opacity=".18"/><circle cx="{x+172}" cy="460" r="10" fill="{W}"/>'+icon
A['art-psychiatrist-vs-psychologist-2']=bg()+ground()+door(170,T,f'<path d="M245,330 h22 v-22 h16 v22 h22 v16 h-22 v22 h-16 v-22 h-22 z" fill="{W}"/>')+door(820,GD,f'<rect x="878" y="312" width="94" height="56" rx="22" fill="{W}"/><path d="M900,366 l-10,20 l28,-20 z" fill="{W}"/>')+person(600,700,320,shirt=R,hair=N,la=[(-50,30),(-70,-30)],ra=[(50,30),(70,-30)],face='smile')+f'<path d="M520,560 C460,600 420,640 390,690" fill="none" stroke="{N}" stroke-width="7" stroke-dasharray="4 20" stroke-linecap="round"/><path d="M680,560 C740,600 780,640 810,690" fill="none" stroke="{N}" stroke-width="7" stroke-dasharray="4 20" stroke-linecap="round"/>'+f'<circle cx="600" cy="180" r="46" fill="{G}"/><path d="M586,168 q0,-20 16,-20 q18,0 16,18 q-2,12 -16,16 v10" fill="none" stroke="{N}" stroke-width="8" stroke-linecap="round"/><circle cx="602" cy="210" r="5" fill="{N}"/>'+END
def cloud(x,y,s,c='#b8c4cc'): return f'<g transform="translate({x},{y}) scale({s})" fill="{c}"><circle cx="-60" cy="10" r="46"/><circle cx="0" cy="-14" r="62"/><circle cx="66" cy="8" r="48"/><rect x="-106" y="8" width="220" height="50" rx="25"/></g>'
def rain(x0,x1,y,c=LB): return ''.join(f'<path d="M{x},{y+(x%3)*14} l-8,26" stroke="{c}" stroke-width="6" stroke-linecap="round"/>' for x in range(x0,x1,34))
A['art-sadness-vs-depression']=bg(sun(720,200,62)+cloud(600,230,1.25))+ground()+rain(500,720,330)+chair(500,566,190)+person(595,700,330,shirt=T,hair=N,pose='sit',la=[(-10,60),(40,95)],ra=[(20,60),(60,95)],face='sad',dir=1,hairstyle='long')+plant(980,640,.9)+heart(250,330,2.4,R)+END
A['art-sadness-vs-depression-2']=bg(f'<rect x="600" y="0" width="600" height="800" fill="#c9d3d8" opacity=".55"/><path d="M600,60 V740" stroke="{W}" stroke-width="10" stroke-dasharray="8 26" stroke-linecap="round"/>'+sun(380,170,56)+cloud(260,210,.9)+''.join(cloud(x,y,1.2,'#9aa7b0') for x,y in((740,170),(940,140),(1100,210),(840,260))))+ground()+person(320,700,280,shirt=G,hair=N,ra=[(50,-10),(90,-60)],face='smile')+rain(780,1100,330,'#7d8fa0')+person(900,700,280,shirt='#5d6b7a',hair=N,pose='stand',la=[(-20,70),(10,110)],ra=[(20,70),(-10,110)],face='sad',dir=-1)+END
for k,v in A.items():
    open(k+'.svg','w').write(v); subprocess.run(['rsvg-convert','-w','1200',k+'.svg','-o',k+'.png'],check=True)
from PIL import Image
ks=list(A); sheet=Image.new('RGB',(2*600+30,((len(ks)+1)//2)*410+20),(255,255,255))
for i,k in enumerate(ks):
    im=Image.open(k+'.png').convert('RGB').resize((600,400)); sheet.paste(im,(10+(i%2)*610,10+(i//2)*410))
sheet.save('sheet.png'); print(len(ks))
