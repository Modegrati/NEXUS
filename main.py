#!/usr/bin/env python3
"""
NEXUS SECURITY TERMINAL v4.7.2  —  SMOOTH EDITION
Windows: pip install windows-curses
Linux:   langsung jalan
"""

import curses
import time
import random
import math
from datetime import datetime

BOOT_SPEED     = 0.018
PANEL_HOLD     = 7
SINGLE_HOLD    = 3.5
FRAME_DELAY    = 0.05
STATUS_H       = 2
GLITCH_DUR     = 0.35
ALERT_MIN      = 15
ALERT_MAX      = 25

LOCS = {
    'NYC':(0.20,0.14),'WDC':(0.24,0.15),'LAX':(0.26,0.08),'CHI':(0.22,0.12),
    'SAO':(0.58,0.22),'BUE':(0.72,0.19),'MEX':(0.34,0.11),'BOG':(0.42,0.17),
    'LON':(0.19,0.42),'PAR':(0.25,0.44),'BER':(0.22,0.47),'ROM':(0.28,0.45),
    'MOS':(0.14,0.57),'MAD':(0.29,0.39),'STO':(0.14,0.46),'WAR':(0.20,0.49),
    'CAI':(0.34,0.49),'LGA':(0.46,0.43),'JHB':(0.64,0.50),'NAI':(0.45,0.50),
    'RIY':(0.34,0.54),'TEH':(0.30,0.57),'ISL':(0.32,0.61),'DXB':(0.35,0.56),
    'DEL':(0.34,0.66),'MUM':(0.40,0.65),'KAR':(0.36,0.62),
    'BEI':(0.24,0.73),'SHH':(0.30,0.75),'TOK':(0.23,0.83),'SEO':(0.24,0.79),
    'SYD':(0.66,0.83),'MEL':(0.68,0.80),'JKT':(0.52,0.75),'BKK':(0.42,0.73),
    'SIN':(0.50,0.74),'MAN':(0.46,0.72),'TAI':(0.30,0.78),
}

CONNS = [
    ('MOS','BEI'),('BEI','TOK'),('NYC','LON'),('LON','BER'),('BER','MOS'),
    ('TEH','DEL'),('DEL','BEI'),('NYC','SAO'),('LON','CAI'),('CAI','RIY'),
    ('RIY','TEH'),('TOK','SYD'),('JKT','SYD'),('MUM','SIN'),('BKK','JKT'),
    ('WDC','LON'),('LAX','TOK'),('PAR','MAD'),('NAI','JHB'),('ISL','DEL'),
    ('SEO','TOK'),('SHH','SIN'),('MEX','BOG'),('CHI','LON'),('STO','MOS'),
]

def fake_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

def fake_port():
    return random.choice([22,80,443,8080,3306,5432,21,25,53,110,993,3389,8443,27017,6379,9090])

def fake_proto():
    return random.choice(['TCP','UDP','HTTP','HTTPS','DNS','SSH','FTP','SMTP','ICMP','TLS','QUIC'])

def fake_proc():
    n = ['sshd','nginx','apache2','mysqld','postgres','redis-serv','python3','node',
         'docker','cron','systemd','bash','java','chrome','firewalld','kubelet',
         'etcd','prometheus','grafana','vault','consul','haproxy','ffmpeg']
    u = ['root','www-data','mysql','postgres','redis','nobody','admin','daemon','sys-net']
    return random.choice(u), random.choice(n)

def bresenham(y1,x1,y2,x2):
    pts=[]; dx,dy=abs(x2-x1),abs(y2-y1)
    sx=1 if x1<x2 else -1; sy=1 if y1<y2 else -1; err=dx-dy
    while True:
        pts.append((y1,x1))
        if x1==x2 and y1==y2: break
        e2=2*err
        if e2>-dy: err-=dy; x1+=sx
        if e2<dx: err+=dx; y1+=sy
    return pts

def pbar(pct, w=20, f='\u2588', e='\u2591'):
    n=int(pct/100*w)
    return f*n+e*(w-n)

# ═════════════════════════════════════════
# WARNA — global, di-set setelah initscr
# ═════════════════════════════════════════
G=R=Y=C=M=W=GB=RB=YB=CB=WB=GD=0

def init_colors():
    global G,R,Y,C,M,W,GB,RB,YB,CB,WB,GD
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN,  curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED,    curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN,   curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA,curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE,  curses.COLOR_BLACK)
    G  = curses.color_pair(1)
    R  = curses.color_pair(2)
    Y  = curses.color_pair(3)
    C  = curses.color_pair(4)
    M  = curses.color_pair(5)
    W  = curses.color_pair(6)
    GB = G | curses.A_BOLD
    RB = R | curses.A_BOLD
    YB = Y | curses.A_BOLD
    CB = C | curses.A_BOLD
    WB = W | curses.A_BOLD
    GD = G | curses.A_DIM

def sstr(win,y,x,t,a=0):
    h,w=win.getmaxyx()
    if y<0 or y>=h or x<0 or x>=w: return
    if x+len(t)>w: t=t[:w-x]
    try: win.addstr(y,x,t,a)
    except: pass

def sch(win,y,x,c,a=0):
    h,w=win.getmaxyx()
    if y<0 or y>=h or x<0 or x>=w: return
    try: win.addch(y,x,c,a)
    except: pass

# ═════════════════════════════════════════
# BOOT
# ═════════════════════════════════════════
def boot(stdscr):
    stdscr.clear()
    h,w=stdscr.getmaxyx(); cy=h//2-9
    lines=[
        (CB,"\u2554"+("\u2550"*58)+"\u2557"),
        (CB,"\u2551        NEXUS SECURITY TERMINAL  v4.7.2                     \u2551"),
        (CB,"\u2551        CLASSIFIED // EYES ONLY                             \u2551"),
        (CB,"\u255a"+("\u2550"*58)+"\u255d"),
        (0,""),
        (G,"[BOOT] Initializing secure kernel..."),
        (G,"[BOOT] Loading cryptographic modules... AES-256-GCM ready"),
        (G,"[BOOT] Establishing encrypted tunnel... TLS 1.3 handshake OK"),
        (G,"[BOOT] Connecting to satellite array..."),
        (G,"[BOOT] Loading geospatial threat database... 2.4M entries"),
        (G,"[BOOT] Activating network interceptor... promiscuous mode ON"),
        (G,"[BOOT] Calibrating radar subsystem... sweep rate 6 RPM"),
        (G,"[BOOT] Mounting decryption engine... GPU accel enabled"),
        (YB,"[ OK ] All 7 subsystems nominal."),
        (0,""),
        (GB,">>> ENTERING SECURE MODE... PRESS Q TO EXIT <<<"),
    ]
    for attr,text in lines:
        if cy>=h: break
        if text=="": cy+=1; continue
        for i,ch in enumerate(text):
            if cy>=h: break
            try:
                if attr: stdscr.addch(cy,min(i,w-1),ch,attr)
                else: stdscr.addch(cy,min(i,w-1),ch)
            except: pass
            stdscr.refresh()
            time.sleep(BOOT_SPEED)
        cy+=1
    time.sleep(0.8)
    stdscr.clear(); stdscr.refresh()

# ═════════════════════════════════════════
# PANEL 1 — GLOBAL THREAT MAP
# ═════════════════════════════════════════
class ThreatMap:
    def __init__(self):
        self.warns={}; self.act_conns=[]; self._refresh()
    def _refresh(self):
        n=random.randint(3,6)
        ch=random.sample(list(LOCS.keys()),min(n,len(LOCS)))
        wt=['INTRUSION','BREACH','MALWARE','DDoS','EXPLOIT','BACKDOOR',
            'DATA LEAK','RANSOMWARE','PHISHING','ZERO-DAY']
        self.warns={l:random.choice(wt) for l in ch}
        self.act_conns=random.sample(CONNS,min(random.randint(4,7),len(CONNS)))
    def draw(self,win,frame):
        win.erase(); h,w=win.getmaxyx()
        if h<5 or w<12: return
        ih, iw = h-2, w-2
        for y in range(1,h-1):
            for x in range(1,w-1):
                if y%3==0 and x%7==0: sch(win,y,x,'+',GD)
                elif y%3==0: sch(win,y,x,'-',GD)
                elif x%7==0: sch(win,y,x,'|',GD)
        for l1,l2 in self.act_conns:
            p1,p2=LOCS[l1],LOCS[l2]
            y1=int(p1[0]*ih)+1; x1=int(p1[1]*iw)+1
            y2=int(p2[0]*ih)+1; x2=int(p2[1]*iw)+1
            pts=bresenham(y1,x1,y2,x2)
            for i,(py,px) in enumerate(pts):
                if 0<py<h-1 and 0<px<w-1: sch(win,py,px,'\u00b7',GD)
            for offset in [0, 0.5]:
                prog=((frame*0.02+offset)%1.0)
                idx=min(int(prog*len(pts)),len(pts)-1)
                py,px=pts[idx]
                if 0<py<h-1 and 0<px<w-1: sch(win,py,px,'\u25c6',YB)
        for name,(py,px) in LOCS.items():
            y=int(py*ih)+1; x=int(px*iw)+1
            if not(1<y<h-2 and 1<x<w-8): continue
            if name in self.warns:
                if (frame//7)%2==0:
                    sch(win,y,x,'\u25cf',RB)
                    wt=self.warns[name]
                    sstr(win,y,x+2,f"!! {wt}",RB)
                else:
                    sch(win,y,x,'\u25cf',R)
            else:
                sch(win,y,x,'\u25cf',GB)
                sstr(win,y,x+2,name,G)
        win.border()
        sstr(win,0,2," GLOBAL THREAT MAP",CB)
        if (frame//12)%3==0: sstr(win,0,max(2,w-16),"!! ELEVATED",RB)
        else: sstr(win,0,max(2,w-14),"ELEVATED",Y)
        if frame%100==0: self._refresh()

# ═════════════════════════════════════════
# PANEL 2 — SATELLITE TRACKER
# ═════════════════════════════════════════
class SatelliteTracker:
    def __init__(self):
        self.sats=[
            {'n':'NEXUS-1', 'r':0.38,'spd':0.018,'ph':0.0, 'inc':0.3},
            {'n':'NEXUS-2', 'r':0.30,'spd':0.028,'ph':1.6, 'inc':-0.25},
            {'n':'NEXUS-3', 'r':0.45,'spd':0.013,'ph':3.2, 'inc':0.5},
            {'n':'AURORA-7','r':0.34,'spd':0.022,'ph':4.8, 'inc':-0.4},
        ]
    def draw(self,win,frame):
        win.erase(); h,w=win.getmaxyx()
        if h<8 or w<20: return
        cx,cy=w//2, h//2-2; mr=min(cx-3,cy-3)
        if mr<4: return
        er=max(2,int(mr*0.15))
        for ad in range(0,360,8):
            rad=math.radians(ad)
            ey=int(cy+er*math.sin(rad)); ex=int(cx+er*math.cos(rad)*1.6)
            if 1<ey<h-1 and 1<ex<w-1: sch(win,ey,ex,'\u25a0',C|curses.A_DIM)
        for dy in range(-er+1,er):
            for dx in range(-int(er*1.6)+1,int(er*1.6)):
                if (dy/max(1,er))**2+(dx/max(1,er*1.6))**2<0.6:
                    ey,ex=cy+dy,cx+dx
                    if 1<ey<h-1 and 1<ex<w-1: sch(win,ey,ex,'\u00b7',C|curses.A_DIM)
        for s in self.sats:
            orb=int(mr*s['r'])
            for ad in range(0,360,5):
                rad=math.radians(ad)
                oy=int(cy+orb*math.sin(rad)*math.cos(s['inc']))
                ox=int(cx+orb*math.cos(rad))
                if 1<oy<h-1 and 1<ox<w-1: sch(win,oy,ox,'\u00b7',GD)
        info_lines=[]
        for s in self.sats:
            orb=int(mr*s['r']); ang=s['ph']+frame*s['spd']
            sy=int(cy+orb*math.sin(ang)*math.cos(s['inc']))
            sx=int(cx+orb*math.cos(ang))
            if 1<sy<h-1 and 1<sx<w-1:
                sch(win,sy,sx,'\u25c6',YB)
                dist=math.sqrt((sy-cy)**2+(sx-cx)**2)
                if dist>er+2:
                    pts=bresenham(sy,sx,cy,cx)
                    for i,(ly,lx) in enumerate(pts):
                        if 1<ly<h-1 and 1<lx<w-1 and i%3==0: sch(win,ly,lx,'\u250a',GD)
            lat=math.degrees(math.asin(max(-1,min(1,math.sin(ang)*math.cos(s['inc'])))))
            lon=math.degrees(ang)%360-180
            alt=random.randint(350,850); vel=random.uniform(6.5,7.8); sig=random.randint(55,100)
            info_lines.append(f"{s['n']}: {lat:+6.1f},{lon:+7.1f} {alt}km {vel:.1f}km/s S:{sig}%")
        iy=h-len(info_lines)-1
        for i,line in enumerate(info_lines):
            sstr(win,iy+i,2,line[:w-4],G)
        win.border()
        sstr(win,0,2," SATELLITE TRACKER",CB)
        sstr(win,0,max(2,w-14),f"ACTIVE: {len(self.sats)}/4",GB)

# ═════════════════════════════════════════
# PANEL 3 — SYSTEM MONITOR
# ═════════════════════════════════════════
class SysMonitor:
    def __init__(self):
        self.cpu_hist=[random.randint(15,80) for _ in range(50)]
        self.mem=random.randint(40,70); self.dsk=random.randint(30,55)
        self.lines=[]; self.swap=random.randint(5,20)
        self.net_in=0.0; self.net_out=0.0
    def draw(self,win,frame):
        win.erase(); h,w=win.getmaxyx()
        if h<8 or w<20: return
        y=1
        sstr(win,y,1,"CPU UTILIZATION",YB); y+=1
        self.cpu_hist.append(random.randint(max(0,self.cpu_hist[-1]-20),min(100,self.cpu_hist[-1]+20)))
        if len(self.cpu_hist)>50: self.cpu_hist.pop(0)
        avg=sum(self.cpu_hist[-20:])/20
        bw=min(18,w-16)
        sstr(win,y,1,f"AVG {avg:5.1f}% {pbar(avg,bw)}",G); y+=1
        for c in range(min(4,max(0,(h-12)//2))):
            cv=random.randint(max(0,int(avg)-25),min(100,int(avg)+25))
            sstr(win,y,1,f" C{c} {cv:3d}% {pbar(cv,bw)}",G); y+=1
        y+=1
        self.mem=max(20,min(95,self.mem+random.randint(-2,2)))
        mu=16.0*self.mem/100
        sstr(win,y,1,f"MEM {mu:4.1f}G/16G {pbar(self.mem,bw)}",C); y+=1
        self.swap=max(1,min(40,self.swap+random.randint(-1,1)))
        sstr(win,y,1,f"SWP {self.swap:3d}%/40% {pbar(self.swap,bw)}",M); y+=1
        self.dsk=max(20,min(90,self.dsk+random.randint(-1,1)))
        du=512.0*self.dsk/100
        sstr(win,y,1,f"DSK {du:5.0f}G/512G {pbar(self.dsk,bw)}",M); y+=1
        self.net_in=max(0.1,self.net_in+random.uniform(-5,5))
        self.net_out=max(0.1,self.net_out+random.uniform(-3,3))
        sstr(win,y,1,f"NET IN:{self.net_in:6.1f}MB/s OUT:{self.net_out:6.1f}MB/s",G); y+=2
        sstr(win,y,1,"PID    USER     CPU%  MEM%  COMMAND",Y); y+=1
        sstr(win,y,1,"\u2500"*min(w-3,40),GD); y+=1
        if frame%6==0 or not self.lines:
            u,c=fake_proc(); pid=random.randint(1000,65534)
            cpu=random.uniform(0.0,30.0); mem=random.uniform(0.0,18.0)
            self.lines.append(f"{pid:>5} {u:<8} {cpu:5.1f} {mem:5.1f}  {c}")
            if len(self.lines)>150: self.lines=self.lines[-150:]
        avail=h-y-1
        if avail>0:
            for line in self.lines[-avail:]:
                sstr(win,y,1,line[:w-3],G); y+=1
                if y>=h-1: break
        win.border()
        sstr(win,0,2," SYSTEM MONITOR",CB)
        us=frame*FRAME_DELAY
        sstr(win,0,max(2,w-16),f"UP {int(us//3600):02d}:{int(us%3600//60):02d}:{int(us%60):02d}",GB)

# ═════════════════════════════════════════
# PANEL 4 — PACKET INTERCEPTOR
# ═════════════════════════════════════════
class PacketInt:
    def __init__(self):
        self.pkts=[]; self.total=0; self.flagged=0
    def draw(self,win,frame):
        win.erase(); h,w=win.getmaxyx()
        if h<6 or w<30: return
        if frame%2==0:
            pr=fake_proto(); src=fake_ip(); dst=fake_ip()
            sp=fake_port(); dp=fake_port(); sz=random.randint(40,1500)
            self.total+=1
            fl=random.random()<0.07
            if fl: self.flagged+=1
            inf=random.choice(['SYN','ACK','PSH,ACK','FIN,ACK','RST',
                'GET /','POST /api','DNS Query','TLS 1.3','QUIC']) if not fl \
                else random.choice(['SUSPICIOUS PAYLOAD','MALWARE SIG',
                'EXFILTRATION DETECTED','BRUTE FORCE','C2 BEACON','SHELLCODE'])
            self.pkts.append({'t':datetime.now().strftime("%H:%M:%S"),
                's':src,'sp':sp,'d':dst,'dp':dp,'p':pr,'sz':sz,'f':fl,'i':inf})
            if len(self.pkts)>300: self.pkts=self.pkts[-300:]
        y=1
        hdr=f"{'TIME':>8} {'SRC':>15} {'DST':>15} {'P':<5} {'SZ':>4} INFO"
        sstr(win,y,1,hdr[:w-3],Y); y+=1
        sstr(win,y,1,'\u2500'*min(w-3,62),GD); y+=1
        avail=h-y-1
        if avail>0:
            for p in self.pkts[-avail:]:
                col=RB if p['f'] else G
                pre='!' if p['f'] else ' '
                ln=f"{p['t']:>8} {p['s']:>15}:{p['sp']:<5} {p['d']:>15}:{p['dp']:<5} {p['p']:<5} {p['sz']:>4} {pre}{p['i']}"
                sstr(win,y,1,ln[:w-3],col); y+=1
                if y>=h-1: break
        win.border()
        sstr(win,0,2," PACKET INTERCEPTOR",CB)
        st=f"PKT:{self.total} FLG:{self.flagged}"
        sstr(win,0,max(2,w-len(st)-2),st,RB if self.flagged else GB)

# ═════════════════════════════════════════
# PANEL 5 — DECRYPTION ENGINE
# ═════════════════════════════════════════
class DecryptEngine:
    SECRETS=[
        "OPERATION DARKSTORM COMMENCES AT 0300 UTC",
        "ACCESS CODE: 7F-3A-9C-2E-8B-1D-4F-6A-0C",
        "TARGET COORDINATES: 48.8566N 2.3522E PARIS",
        "EXTRACT ASSET BEFORE DAWN. BURN AFTER READ",
        "SERVER FARM COMPROMISED. INIT PROTOCOL ZETA",
        "MEETING POINT: BRIDGE SEVEN, 2200 HRS LOCAL",
        "ENCRYPTION KEY ROTATION IN PROGRESS... WAIT",
        "FIREWALL BREACH CONFIRMED. LATERAL MOVEMENT",
        "DATABASE DUMP COMPLETE: 2.4TB EXFILTRATED",
        "ZERO-DAY EXPLOIT DEPLOYED ON TARGET NETWORK",
        "BACKDOOR INSTALLED: PERSISTENCE ENSURED",
        "VPN CREDENTIALS HARVESTED: 847 ACCOUNTS",
    ]
    def __init__(self):
        self.target=random.choice(self.SECRETS)
        self.decoded=0; self.blocks=0; self.ops=0
    def draw(self,win,frame):
        win.erase(); h,w=win.getmaxyx()
        if h<6 or w<20: return
        y=1
        sstr(win,y,1,"CIPHER: AES-256-GCM | MODE: CBC | IV: RANDOM",C); y+=1
        sstr(win,y,1,f"BLOCK: {self.blocks:04d} | OPS: {self.ops:06d} | KEY ROT: ACTIVE",C); y+=2
        dec=self.target[:self.decoded]; rem=self.target[self.decoded:]
        if dec:
            sstr(win,y,1,"[DECODED]",GB); y+=1
            if len(dec)>0 and (frame//4)%2==0:
                sstr(win,y,2,dec[:-1],GB)
                sstr(win,y,2+len(dec)-1,dec[-1],YB)
            else:
                sstr(win,y,2,dec,GB)
            y+=2
        if rem:
            sstr(win,y,1,"[ENCRYPTED]",Y); y+=1
            hx=rem.encode().hex().upper()
            cs=max(6,(w-4)//3)
            for i in range(0,len(hx),cs):
                chunk=hx[i:i+cs]
                fmt=' '.join(chunk[j:j+2] for j in range(0,len(chunk),2))
                if y<h-4:
                    sstr(win,y,2,fmt,Y); y+=1
                else: break
        y=max(y,h-5)
        pct=self.decoded/max(1,len(self.target))*100
        bw=min(30,w-16)
        sstr(win,y,1,f"PROGRESS: {pbar(pct,bw)} {pct:5.1f}%",GB); y+=1
        key=''.join(f'{random.randint(0,255):02X}' for _ in range(16))
        kf=' '.join(key[i:i+4] for i in range(0,16,4))
        sstr(win,y,1,f"KEY: {kf}",M); y+=1
        hs=''.join(f'{random.randint(0,15):X}' for _ in range(32))
        sstr(win,y,1,f"SHA: {hs[:w-7]}",GD)
        if frame%3==0:
            self.decoded+=1; self.ops+=random.randint(1000,9999)
            if self.decoded>len(self.target):
                self.decoded=0; self.target=random.choice(self.SECRETS)
                self.blocks+=1
        win.border()
        sstr(win,0,2," DECRYPTION ENGINE",CB)
        st="DECRYPTING" if pct<100 else "COMPLETE"
        sstr(win,0,max(2,w-len(st)-2),st,YB if pct<100 else GB)

# ═════════════════════════════════════════
# PANEL 6 — RADAR SWEEP
# ═════════════════════════════════════════
class Radar:
    def __init__(self):
        self.blips=[]; self.angle=0
    def draw(self,win,frame):
        win.erase(); h,w=win.getmaxyx()
        if h<10 or w<20: return
        cx,cy=w//2,h//2; mr=min(cx-3,cy-3)
        if mr<4: return
        for rp in [0.25,0.5,0.75,1.0]:
            r=int(mr*rp)
            for ad in range(0,360,4):
                rad=math.radians(ad)
                ry=int(cy+r*math.sin(rad)); rx=int(cx+r*math.cos(rad))
                if 1<ry<h-1 and 1<rx<w-1: sch(win,ry,rx,'\u00b7',GD)
        for d in range(-mr,mr+1):
            if 1<cy<h-1 and 1<cx+d<w-1: sch(win,cy,cx+d,'\u00b7',GD)
            if 1<cy+d<h-1 and 1<cx<w-1: sch(win,cy+d,cx,'\u00b7',GD)
        for lb,dy,dx in [('N',-mr-1,0),('S',mr+1,0),('E',0,mr+1),('W',0,-mr-1)]:
            ny,nx=cy+dy,cx+dx-len(lb)//2
            if 1<ny<h-1 and 1<nx<w-1: sstr(win,ny,nx,lb,CB)
        self.angle=(self.angle+3)%360; sr=math.radians(self.angle)
        for d in range(0,mr):
            sy=int(cy+d*math.sin(sr)); sx=int(cx+d*math.cos(sr))
            if 1<sy<h-1 and 1<sx<w-1:
                if d<mr*0.15: sch(win,sy,sx,'\u2588',GB)
                elif d<mr*0.4: sch(win,sy,sx,'\u2593',GB)
                else: sch(win,sy,sx,'\u2502',G)
        for tr in range(1,20):
            trad=math.radians(self.angle-tr*2)
            for d in range(int(mr*0.2),mr,3):
                sy=int(cy+d*math.sin(trad)); sx=int(cx+d*math.cos(trad))
                if 1<sy<h-1 and 1<sx<w-1 and tr<8: sch(win,sy,sx,'\u00b7',GD)
        if frame%12==0:
            self.blips.append({'a':random.uniform(0,6.283),'d':random.uniform(0.15,0.95),'age':0})
        new=[]
        for b in self.blips:
            b['age']+=1
            if b['age']>45: continue
            new.append(b)
            by=int(cy+mr*b['d']*math.sin(b['a']))
            bx=int(cx+mr*b['d']*math.cos(b['a']))
            if 1<by<h-1 and 1<bx<w-1:
                if b['age']<6: sch(win,by,bx,'\u25a0',GB)
                elif b['age']<25: sch(win,by,bx,'\u25aa',G)
                else: sch(win,by,bx,'\u00b7',GD)
        self.blips=new
        if 1<cy<h-1 and 1<cx<w-1: sch(win,cy,cx,'\u25cf',CB)
        for rp,lb in [(0.25,'250km'),(0.5,'500km'),(0.75,'750km'),(1.0,'1000km')]:
            ry=cy+int(mr*rp)+1
            if 1<ry<h-1 and cx+2<w-1: sstr(win,ry,cx+2,lb,GD)
        win.border()
        sstr(win,0,2," RADAR SWEEP",CB)
        nc=len(self.blips)
        sstr(win,0,max(2,w-18),f"CONTACTS: {nc}",GB if nc<5 else YB)

# ═════════════════════════════════════════
# STATUS BAR
# ═════════════════════════════════════════
def draw_status(scr,frame,pcnt,t0):
    h,w=scr.getmaxyx(); y=h-STATUS_H
    try: scr.addstr(y,0,'\u2550'*w,GD)
    except: pass
    y+=1
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    el=time.time()-t0
    parts=[
        (CB,f" NEXUS-SEC v4.7.2 "),
        (G,f"| {now} "),
        (GB,f"| ENCRYPTED TUNNEL ACTIVE "),
        (G,f"| UP:{int(el//3600):02d}:{int(el%3600//60):02d}:{int(el%60):02d} "),
        (GB,f"| PANELS:{pcnt} "),
        (Y if (frame//25)%2==0 else GB,f"| * SECURE "),
    ]
    x=0
    for a,t in parts:
        if x+len(t)>w: break
        try: scr.addstr(y,x,t,a)
        except: pass
        x+=len(t)
    if x<w:
        try: scr.addstr(y,x,' '*(w-x),0)
        except: pass

# ═════════════════════════════════════════
# GLITCH & ALERT
# ═════════════════════════════════════════
GLITCH_CH='\u2588\u2593\u2592\u2591\u2554\u2557\u255a\u255d\u2551\u2550\u2563\u253c\u2524\u251c\u252c\u2534\u2500\u2502\u2510\u2518\u2514\u250c'

def draw_glitch(scr):
    h,w=scr.getmaxyx()
    for _ in range(random.randint(3,8)):
        gy=random.randint(0,h-1); gh=random.randint(1,4)
        for y in range(gy,min(h,gy+gh)):
            for x in range(w):
                try: scr.addch(y,x,random.choice(GLITCH_CH),random.choice([G,R,Y,C,M]))
                except: pass

ALERTS=[
    "!!  BREACH DETECTED -- SECTOR 7G  !!",
    "!!  INTRUSION ALERT -- NODE 42  !!",
    "!!  MALWARE SIGNATURE MATCH  !!",
    "!!  UNAUTHORIZED ACCESS -- FIREWALL 3  !!",
    "!!  DATA EXFILTRATION IN PROGRESS  !!",
    "!!  C2 SERVER COMMUNICATION DETECTED  !!",
    "!!  ZERO-DAY EXPLOIT ATTEMPT BLOCKED  !!",
    "!!  RANSOMWARE PAYLOAD INTERCEPTED  !!",
]

def draw_alert(scr):
    h,w=scr.getmaxyx()
    alert=random.choice(ALERTS)
    y=random.randint(2,max(2,h-4))
    try:
        for x in range(w):
            scr.addch(y,x,' ',R|curses.A_BOLD)
        x=max(0,(w-len(alert))//2)
        scr.addstr(y,x,alert,RB)
        for x in range(w):
            scr.addch(y-1,x,'\u2550',RB)
            if y+1<h: scr.addch(y+1,x,'\u2550',RB)
    except: pass

# ═════════════════════════════════════════
# MAIN — pakai noutrefresh + doupdate
# ═════════════════════════════════════════
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(0)
    init_colors()
    boot(stdscr)

    h,w=stdscr.getmaxyx()
    if h<20 or w<60:
        stdscr.clear()
        msg=f"Terminal minimal 60x20. Sekarang: {w}x{h}"
        try: stdscr.addstr(h//2,max(0,(w-len(msg))//2),msg,RB)
        except: pass
        stdscr.refresh(); time.sleep(3); return

    renderers=[ThreatMap(),SatelliteTracker(),SysMonitor(),PacketInt(),DecryptEngine(),Radar()]
    titles=[" GLOBAL THREAT MAP "," SATELLITE TRACKER "," SYSTEM MONITOR ",
            " PACKET INTERCEPTOR "," DECRYPTION ENGINE "," RADAR SWEEP "]

    configs=[4,3,2,1]
    ci=0; pcnt=configs[0]
    last_sw=time.time()
    spi=0; last_sp=time.time()
    t0=time.time(); frame=0
    glitching=False; glitch_t=0
    next_alert=time.time()+random.uniform(ALERT_MIN,ALERT_MAX)
    windows=[]; cur_cfg=None

    running=True
    while running:
        try:
            key=stdscr.getch()
            if key in (ord('q'),ord('Q'),27): running=False; break
        except: pass

        now=time.time()
        h,w=stdscr.getmaxyx()
        uh=h-STATUS_H

        if now-last_sw>=PANEL_HOLD:
            last_sw=now; glitching=True; glitch_t=now
            ci=(ci+1)%len(configs); pcnt=configs[ci]

        if pcnt==1 and now-last_sp>=SINGLE_HOLD:
            last_sp=now; spi=(spi+1)%len(renderers)

        alerting = now>=next_alert and now<next_alert+0.6
        if now>=next_alert+0.6:
            next_alert=now+random.uniform(ALERT_MIN,ALERT_MAX)

        # glitch effect — ini boleh refresh langsung karena cuma 0.3 detik
        if glitching and now-glitch_t<GLITCH_DUR:
            stdscr.clear(); draw_glitch(stdscr)
            stdscr.refresh()
            time.sleep(FRAME_DELAY); frame+=1; continue
        else:
            glitching=False

        # hitung layout
        layouts=[]
        if pcnt==4:
            hh=uh//2; hw=w//2
            layouts=[(0,0,hh,hw,0),(0,hw,hh,w-hw,1),(hh,0,uh-hh,hw,2),(hh,hw,uh-hh,w-hw,3)]
        elif pcnt==3:
            th=uh//2; bh=uh-th; hw=w//2
            layouts=[(0,0,th,w,0),(th,0,bh,hw,1),(th,hw,bh,w-hw,2)]
        elif pcnt==2:
            hw=w//2
            layouts=[(0,0,uh,hw,0),(0,hw,uh,w-hw,3)]
        elif pcnt==1:
            layouts=[(0,0,uh,w,spi)]

        # bikin ulang window cuma kalau layout berubah
        cfg=tuple((r,c,ph,pw,ri) for r,c,ph,pw,ri in layouts)
        if cfg!=cur_cfg:
            for wn in windows:
                try: wn.erase()
                except: pass
            windows=[]
            for r,c,ph,pw,ri in layouts:
                try: windows.append(curses.newwin(ph,pw,r,c))
                except: windows.append(None)
            cur_cfg=cfg

        # ─── INI INTI FIX ANTI-JEDAG ───
        # Jangan stdscr.clear() — panel sudah menutupi seluruh area
        # Pakai erase() bukan clear() di dalam draw()
        # Pakai noutrefresh() bukan refresh() — cuma tandai, belum kirim ke terminal
        for i,(r,c,ph,pw,ri) in enumerate(layouts):
            if i<len(windows) and windows[i]:
                try:
                    renderers[ri].draw(windows[i],frame)
                    windows[i].border()
                    tl=titles[ri]
                    if len(tl)>pw-4: tl=tl[:pw-4]
                    sstr(windows[i],0,1,tl,CB)
                    windows[i].noutrefresh()   # <<< TANDAI AJA, JANGAN REFRESH
                except: pass

        # status bar langsung di stdscr
        draw_status(stdscr,frame,pcnt,t0)
        stdscr.noutrefresh()                   # <<< TANDAI AJA

        # alert overlay di stdscr
        if alerting:
            draw_alert(stdscr)
            stdscr.noutrefresh()               # <<< TANDAI AJA

        # SEKALI DONG — kirim semua ke terminal sekaligus
        curses.doupdate()                      # <<< INI YANG MEMBUAT SMOOTH

        time.sleep(FRAME_DELAY); frame+=1

    # exit screen
    stdscr.clear()
    h,w=stdscr.getmaxyx()
    msgs=[
        (RB,"  +-------------------------------------------+"),
        (RB,"  |     CONNECTION TERMINATED                 |"),
        (RB,"  |     SECURE CHANNEL CLOSED                 |"),
        (RB,"  +-------------------------------------------+"),
        (G,""),
        (G,"  Press any key to exit..."),
    ]
    for i,(a,t) in enumerate(msgs):
        y=h//2-3+i
        if 0<=y<h:
            try: stdscr.addstr(y,max(0,(w-len(t))//2),t,a)
            except: pass
    stdscr.refresh()
    stdscr.timeout(-1)
    try: stdscr.getch()
    except: pass

if __name__=='__main__':
    try: curses.wrapper(main)
    except KeyboardInterrupt: pass
