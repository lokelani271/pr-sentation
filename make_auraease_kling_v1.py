"""
auraease_kling_v1.mp4 — 10s, painted Kling-faithful backgrounds + exact text specs
Scene 1 (0-3s):  "Hate ice baths?" fade-in / "Same." at 1s
Scene 2 (3-7s):  "Targeted cold therapy" / "without the freeze." / "$35 for 200+ uses."
Scene 3 (7-10s): "Recover smarter." / "AuraEase™" center / "Link in bio" pulsing
"""
import os, math, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy import VideoClip

W, H, FPS = 1080, 1920, 30
TOTAL = 10.0
XF    = 0.30

GOLD  = (201, 169, 110)
WHITE = (255, 255, 255)
SAFE  = int(W * 0.80)       # 80% safe zone = 864px

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

@lru_cache(maxsize=32)
def fb(size, bold=True):
    for p in (FONT_PATHS if bold else FONT_REG):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def fit_font(txt, max_size, bold=True):
    size = max_size
    while size > 24:
        fnt = fb(size, bold)
        bb = ImageDraw.Draw(Image.new("RGBA",(1,1))).textbbox((0,0),txt,font=fnt)
        if bb[2]-bb[0] <= SAFE:
            return fnt, size
        size -= 3
    return fb(24, bold), 24

def draw_centered(d, txt, y, color, max_size, bold=True, alpha=255):
    fnt, _ = fit_font(txt, max_size, bold)
    bb = d.textbbox((0,0), txt, font=fnt)
    x = (W-(bb[2]-bb[0]))//2
    r,g,b = color
    d.text((x, y), txt, font=fnt, fill=(r,g,b,alpha))

# ══════════════════════════════════════════════════════════════════════
# BACKGROUNDS (painted from Kling reference images)
# ══════════════════════════════════════════════════════════════════════

def make_bg1():
    """Scene 1: Man's back, white t-shirt, beige gym — kling_pain"""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y/H
        r = int(232-18*t); g = int(224-16*t); b = int(210-18*t)
        d.line([(0,y),(W,y)], fill=(r,g,b))
    # Floor
    for y in range(int(H*0.82), H):
        t=(y-H*0.82)/(H*0.18); c=int(60+30*t)
        d.line([(0,y),(W,y)], fill=(c,c-2,c-5))
    # Gym equipment blurred
    eq=Image.new("RGBA",(W,H),(0,0,0,0)); ed=ImageDraw.Draw(eq)
    ed.rectangle([55,int(H*0.18),95,int(H*0.78)], fill=(80,75,72,160))
    ed.rectangle([W-115,int(H*0.22),W-75,int(H*0.72)], fill=(85,80,77,130))
    img_rgba=img.convert("RGBA"); img_rgba.alpha_composite(eq.filter(ImageFilter.GaussianBlur(9)))
    img=img_rgba.convert("RGB"); d=ImageDraw.Draw(img)
    # Neck
    d.ellipse([W//2-55,int(H*0.12),W//2+55,int(H*0.28)], fill=(210,170,140))
    # Hair
    d.ellipse([W//2-148,int(H*0.05),W//2+148,int(H*0.20)], fill=(28,22,18))
    d.ellipse([W//2-80,int(H*0.055),W//2+42,int(H*0.12)], fill=(45,36,30))
    # White shirt
    d.rounded_rectangle([int(W*0.11),int(H*0.20),int(W*0.89),int(H*0.68)],radius=90,fill=(248,248,248))
    d.ellipse([W//2-82,int(H*0.19),W//2+82,int(H*0.26)], fill=(240,240,240))
    # Sleeves & arms
    d.ellipse([int(W*0.03),int(H*0.26),int(W*0.22),int(H*0.46)], fill=(246,246,246))
    d.ellipse([int(W*0.78),int(H*0.26),int(W*0.97),int(H*0.46)], fill=(246,246,246))
    d.ellipse([int(W*0.04),int(H*0.40),int(W*0.19),int(H*0.65)], fill=(205,168,138))
    d.ellipse([int(W*0.81),int(H*0.40),int(W*0.96),int(H*0.65)], fill=(205,168,138))
    # Blue shorts
    d.rectangle([int(W*0.13),int(H*0.66),int(W*0.87),H], fill=(40,80,160))
    # Ceiling lights
    for lx in [int(W*0.22),int(W*0.78)]:
        d.ellipse([lx-46,18,lx+46,64], fill=(255,250,235))
        gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
        for r in [90,60,35]: gd.ellipse([lx-r,15-r//3,lx+r,64+r//3],fill=(255,248,220,min(int(40*(35/(r+1))),120)))
        img_rgba=img.convert("RGBA"); img_rgba.alpha_composite(gl.filter(ImageFilter.GaussianBlur(12))); img=img_rgba.convert("RGB")
    return img.filter(ImageFilter.GaussianBlur(0.5))

def make_bg2():
    """Scene 2: Hands applying navy patch — kling_patch"""
    img = Image.new("RGB", (W, H), (250,248,246))
    SKIN=(225,185,155); SKIN_D=(200,160,128)
    cx,cy = W//2+30, H//2+60
    # Leg ellipse diagonal
    leg=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(leg)
    ld.ellipse([cx-170,cy-450,cx+170,cy+450], fill=(*SKIN,255))
    rotated=leg.rotate(-18,center=(cx,cy),expand=False)
    img_rgba=img.convert("RGBA"); img_rgba.alpha_composite(rotated); img=img_rgba.convert("RGB"); d=ImageDraw.Draw(img)
    # Navy patch (cross shape)
    px,py=cx-40,cy-100; ps=190
    d.rectangle([px-ps//3,py-ps//2,px+ps//3,py+ps//2], fill=(28,48,100))
    d.rectangle([px-ps//2,py-ps//3,px+ps//2,py+ps//3], fill=(28,48,100))
    for offs in [(-40,-100,40,-20),(-40,20,40,100),(-100,-40,-20,40),(20,-40,100,40)]:
        d.ellipse([px+offs[0],py+offs[1],px+offs[2],py+offs[3]], fill=(28,48,100))
    # Top hand
    h1=Image.new("RGBA",(W,H),(0,0,0,0)); h1d=ImageDraw.Draw(h1)
    h1d.ellipse([px-60,py-265,px+205,py-78], fill=(*SKIN,255))
    for fx1,fy1,fx2,fy2 in [(px+130,py-325,px+168,py-178),(px+70,py-355,px+112,py-188),(px+10,py-345,px+58,py-183),(px-48,py-305,px+3,py-168)]:
        h1d.ellipse([fx1,fy1,fx2,fy2], fill=(*SKIN,255))
    img_rgba=img.convert("RGBA"); img_rgba.alpha_composite(h1.filter(ImageFilter.GaussianBlur(1.5))); img=img_rgba.convert("RGB")
    # Bottom hand
    h2=Image.new("RGBA",(W,H),(0,0,0,0)); h2d=ImageDraw.Draw(h2)
    h2d.ellipse([px-225,py+98,px+62,py+282], fill=(*SKIN,255))
    for fx1,fy1,fx2,fy2 in [(px-252,py+118,px-205,py+262),(px-202,py+78,px-154,py+232),(px-148,py+58,px-96,py+212),(px-88,py+68,px-36,py+222)]:
        h2d.ellipse([fx1,fy1,fx2,fy2], fill=(*SKIN,255))
    img_rgba=img.convert("RGBA"); img_rgba.alpha_composite(h2.filter(ImageFilter.GaussianBlur(1.5))); img=img_rgba.convert("RGB")
    return img

def make_bg3():
    """Scene 3: Dark gym, man holding knee with red pain glow — kling_relief"""
    img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; r=int(30-12*t); g=int(28-10*t); b=int(32-12*t)
        d.line([(0,y),(W,y)], fill=(max(r,8),max(g,8),max(b,8)))
    # Gym rack
    rack=Image.new("RGBA",(W,H),(0,0,0,0)); rd=ImageDraw.Draw(rack)
    rd.rectangle([int(W*0.55),int(H*0.02),int(W*0.60),int(H*0.70)], fill=(42,40,38,220))
    rd.rectangle([int(W*0.78),int(H*0.02),int(W*0.83),int(H*0.70)], fill=(42,40,38,200))
    for bar_y in [0.12,0.30,0.48]: rd.rectangle([int(W*0.55),int(H*bar_y),int(W*0.83),int(H*(bar_y+0.04))], fill=(46,44,41,190))
    img_rgba=img.convert("RGBA"); img_rgba.alpha_composite(rack.filter(ImageFilter.GaussianBlur(3))); img=img_rgba.convert("RGB"); d=ImageDraw.Draw(img)
    # Reflective floor
    for y in range(int(H*0.80),H):
        t=(y-H*0.80)/(H*0.20); c=int(22+15*t); d.line([(0,y),(W,y)],fill=(c,c-2,c+2))
    # Bench
    d.rounded_rectangle([int(W*0.18),int(H*0.70),int(W*0.72),int(H*0.76)],radius=12,fill=(35,32,30))
    # Man body
    d.ellipse([int(W*0.18),int(H*0.28),int(W*0.65),int(H*0.60)], fill=(18,17,16))
    d.rectangle([int(W*0.21),int(H*0.40),int(W*0.64),int(H*0.70)], fill=(18,17,16))
    d.ellipse([int(W*0.32),int(H*0.15),int(W*0.60),int(H*0.32)], fill=(28,22,18))
    d.ellipse([int(W*0.37),int(H*0.26),int(W*0.56),int(H*0.38)], fill=(165,128,100))
    d.ellipse([int(W*0.28),int(H*0.60),int(W*0.60),int(H*0.82)], fill=(20,18,16))
    d.ellipse([int(W*0.25),int(H*0.72),int(W*0.52),int(H*0.92)], fill=(155,118,90))
    d.ellipse([int(W*0.22),int(H*0.48),int(W*0.40),int(H*0.75)], fill=(18,17,16))
    d.ellipse([int(W*0.35),int(H*0.55),int(W*0.55),int(H*0.78)], fill=(18,17,16))
    d.ellipse([int(W*0.24),int(H*0.70),int(W*0.46),int(H*0.83)], fill=(160,122,95))
    d.rounded_rectangle([int(W*0.18),int(H*0.88),int(W*0.50),int(H*0.95)],radius=18,fill=(15,13,12))
    d.rectangle([int(W*0.22),int(H*0.920),int(W*0.28),int(H*0.940)], fill=(200,160,20))
    # Red pain glow
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    kx,ky=int(W*0.36),int(H*0.775)
    for r in [160,110,70,40,20]: gd.ellipse([kx-r,ky-r//2,kx+r,ky+r//2],fill=(220,60,15,min(int(180*(20/(r+5))),230)))
    img_rgba=img.convert("RGBA"); img_rgba.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18))); img=img_rgba.convert("RGB")
    return img

print("Rendering backgrounds..."); BG1=make_bg1(); BG2=make_bg2(); BG3=make_bg3(); print("Done.")

# ══════════════════════════════════════════════════════════════════════
# Scene renderers
# ══════════════════════════════════════════════════════════════════════

def dark_ov(img, s=0.45):
    ov=Image.new("RGBA",(W,H),(0,0,0,int(s*255)))
    b=img.convert("RGBA"); b.alpha_composite(ov); return b.convert("RGB")

def scene1(t):
    base = dark_ov(BG1, 0.36)
    ov = Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    # "Hate ice baths?" — fade in 0-0.4s
    a1 = int(min(t/0.40,1.0)*255)
    # "Same." — appears at t=1s, fades in over 0.3s
    a2 = int(min(max(t-1.0,0)/0.30,1.0)*255)
    draw_centered(d,"Hate ice baths?", 148, WHITE, 70, alpha=a1)
    draw_centered(d,"Same.",           275, WHITE, 85, alpha=a2)
    base.paste(ov.convert("RGB"), mask=ov.split()[3])
    return np.array(base)

def scene2(t):
    base = dark_ov(BG2, 0.16)
    ov = Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    a1 = int(min(t/0.30,1.0)*255)
    a2 = int(min(max(t-0.20,0)/0.30,1.0)*255)
    a3 = int(min(max(t-0.40,0)/0.30,1.0)*255)
    draw_centered(d,"Targeted cold therapy",       148, WHITE, 62, alpha=a1)
    draw_centered(d,"without the freeze. \U0001f9ca", 252, GOLD,  58, alpha=a2)
    draw_centered(d,"$35 for 200+ uses.",          1610, WHITE, 45, bold=False, alpha=a3)
    base.paste(ov.convert("RGB"), mask=ov.split()[3])
    return np.array(base)

def scene3(t, dur=3.0):
    fo = min((dur-t)/0.30, 1.0)
    base = dark_ov(BG3, 0.38)
    ov = Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    a1 = int(min(t/0.30,1.0)*fo*255)
    a2 = int(min(max(t-0.20,0)/0.30,1.0)*fo*255)
    # Pulsing for "Link in bio" — sine wave between 0.6 and 1.0
    pulse = 0.60 + 0.40*math.sin(t*math.pi*2.5)
    a3 = int(min(max(t-0.40,0)/0.30,1.0)*fo*pulse*255)
    draw_centered(d,"Recover smarter.",      148, WHITE, 75, alpha=a1)
    draw_centered(d,"AuraEase™",   H//2-50,  GOLD,  85, alpha=a2)
    draw_centered(d,"Link in bio \U0001f517",1710, WHITE, 48, bold=False, alpha=a3)
    base.paste(ov.convert("RGB"), mask=ov.split()[3])
    return np.array(base)

# ── Master / crossfade ───────────────────────────────────────────────
CUT=[0.0,3.0,7.0,10.0]; DURS=[3.0,4.0,3.0]
FNS=[scene1,scene2,scene3]

def xfade(a,b,p): return (a.astype(float)*(1-p)+b.astype(float)*p).astype(np.uint8)

def make_frame(t):
    sc=max(i for i,c in enumerate(CUT[:-1]) if c<=t)
    lt=t-CUT[sc]; sd=DURS[sc]
    fa = FNS[sc](lt) if sc<2 else FNS[sc](lt,sd)
    if sc<len(FNS)-1 and lt>=sd-XF:
        p=min(max((lt-(sd-XF))/XF,0),1)
        fb_= FNS[sc+1](0.0) if sc+1<2 else FNS[sc+1](0.0,DURS[sc+1])
        return xfade(fa,fb_,p)
    return fa

os.makedirs("output",exist_ok=True)
out="output/auraease_kling_v1.mp4"
VideoClip(make_frame,duration=TOTAL).write_videofile(
    out,fps=FPS,codec="libx264",audio=False,
    ffmpeg_params=["-crf","18","-pix_fmt","yuv420p","-movflags","+faststart","-preset","medium"],
    logger=None)
print(f"\nDone → {out}")
