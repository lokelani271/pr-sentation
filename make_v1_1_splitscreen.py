"""
AuraEase™ — Video v1_1 Split Screen
Recreates the reference image design as an animated 10s video.
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from functools import lru_cache
try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy import VideoClip

W, H, FPS = 1080, 1920, 30

NAVY      = (27,  42,  74)
NAVY_DARK = (18,  28,  55)
GRAY_L    = (180, 180, 182)
GRAY_LT   = (210, 210, 212)
GOLD      = (201, 169, 110)
WHITE     = (255, 255, 255)
GREEN     = ( 34, 197,  94)
RED_DARK  = (120,  20,  20)
BLACK     = (  0,   0,   0)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

@lru_cache(maxsize=20)
def fb(sz): return ImageFont.truetype(_BOLD, sz)
@lru_cache(maxsize=20)
def fr(sz): return ImageFont.truetype(_REG,  sz)

def ctext(draw, text, cx, cy, fnt, color):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text((cx - tw//2, cy - th//2), text, font=fnt, fill=color)

def eo(t, d):
    p = max(0., min(1., t / max(d, 1e-9)))
    return 1 - (1-p)**3

def make_frame(t):
    # ── Background: split left=gray, right=navy ──────────────────────────────
    img = Image.new("RGB", (W, H), GRAY_LT)
    d   = ImageDraw.Draw(img)

    # Right navy panel (diagonal cut from top-right to bottom-left)
    # Diagonal edge: top at x=W*0.52, bottom at x=W*0.38
    nav_poly = [
        (int(W * 0.52), 0),
        (W, 0),
        (W, H),
        (int(W * 0.38), H),
    ]
    d.polygon(nav_poly, fill=NAVY)

    # Subtle diagonal light accent on gray side
    for i in range(3):
        accent_poly = [
            (int(W*(0.38 + i*0.08)), H),
            (int(W*(0.52 + i*0.08)), 0),
            (int(W*(0.54 + i*0.08)), 0),
            (int(W*(0.40 + i*0.08)), H),
        ]
        d.polygon(accent_poly, fill=(*WHITE, 30) if i == 0 else (*WHITE, 15))

    # Re-draw with RGBA for layering
    canvas = img.convert("RGBA")

    # ── Animations ────────────────────────────────────────────────────────────
    # Overall entrance: slide + fade everything in 0-0.6s
    enter = eo(min(t, 0.6), 0.6)

    # ── TOP BADGE: "AuraEase Wellness" green pill ─────────────────────────────
    badge_a = eo(t, 0.4)
    badge_y = 110 + int((1-badge_a)*-40)
    badge_w, badge_h = 430, 72
    badge_x = W//2
    badge_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    bd = ImageDraw.Draw(badge_layer)
    bd.rounded_rectangle(
        [badge_x - badge_w//2, badge_y - badge_h//2,
         badge_x + badge_w//2, badge_y + badge_h//2],
        radius=8, fill=(*GREEN, int(255*badge_a))
    )
    bbox = bd.textbbox((0,0), "AuraEase Wellness", font=fb(36))
    tw = bbox[2]-bbox[0]
    bd.text((badge_x - tw//2, badge_y - 20), "AuraEase Wellness",
            font=fb(36), fill=(*BLACK, int(255*badge_a)))
    canvas = Image.alpha_composite(canvas, badge_layer)

    # ── SUBTITLE ──────────────────────────────────────────────────────────────
    sub_a = eo(max(0., t-0.2), 0.45)
    sub_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    sd = ImageDraw.Draw(sub_layer)
    sub_text = "Affordable Wellness Solutions"
    bbox = sd.textbbox((0,0), sub_text, font=fb(38))
    tw = bbox[2]-bbox[0]
    sd.text((W//2 - tw//2, 200), sub_text,
            font=fb(38), fill=(*WHITE, int(255*sub_a)))
    canvas = Image.alpha_composite(canvas, sub_layer)

    # ── HEADLINE: "Discover Your Balance" ────────────────────────────────────
    h1_a = eo(max(0., t-0.15), 0.5)
    h1_dy = int((1-h1_a)*60)
    h1_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    hd = ImageDraw.Draw(h1_layer)
    for line, yoff in [("Discover Your", 340), ("Balance", 470)]:
        bbox = hd.textbbox((0,0), line, font=fb(118))
        tw = bbox[2]-bbox[0]
        hd.text((W//2 - tw//2, yoff + h1_dy), line,
                font=fb(118), fill=(*WHITE, int(255*h1_a)))
    canvas = Image.alpha_composite(canvas, h1_layer)

    # ── LEFT PRICE: $150 PHYSIO ───────────────────────────────────────────────
    p1_a  = eo(max(0., t-0.3), 0.45)
    p1_dx = int((1-p1_a)*-120)
    p1_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    pd = ImageDraw.Draw(p1_layer)
    bbox = pd.textbbox((0,0), "$150", font=fb(140))
    tw = bbox[2]-bbox[0]
    cx_left = W//4
    pd.text((cx_left - tw//2 + p1_dx, 700), "$150",
            font=fb(140), fill=(*RED_DARK, int(255*p1_a)))
    bbox = pd.textbbox((0,0), "PHYSIO", font=fb(52))
    tw = bbox[2]-bbox[0]
    pd.text((cx_left - tw//2 + p1_dx, 860), "PHYSIO",
            font=fb(52), fill=(*BLACK, int(255*p1_a)))
    canvas = Image.alpha_composite(canvas, p1_layer)

    # ── RIGHT PRICE: $35 AURAEASE™ ────────────────────────────────────────────
    p2_a  = eo(max(0., t-0.4), 0.45)
    p2_dx = int((1-p2_a)*120)
    p2_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    pd2 = ImageDraw.Draw(p2_layer)
    cx_right = W*3//4
    bbox = pd2.textbbox((0,0), "$35", font=fb(140))
    tw = bbox[2]-bbox[0]
    pd2.text((cx_right - tw//2 + p2_dx, 700), "$35",
             font=fb(140), fill=(*GOLD, int(255*p2_a)))
    bbox = pd2.textbbox((0,0), "AURAEASE™", font=fb(48))
    tw = bbox[2]-bbox[0]
    pd2.text((cx_right - tw//2 + p2_dx, 865), "AURAEASE™",
             font=fb(48), fill=(*WHITE, int(255*p2_a)))
    canvas = Image.alpha_composite(canvas, p2_layer)

    # ── BOTTOM URL ────────────────────────────────────────────────────────────
    url_a = eo(max(0., t-0.6), 0.4)
    url_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    ud = ImageDraw.Draw(url_layer)
    url_text = "reallygreatsite.com"
    bbox = ud.textbbox((0,0), url_text, font=fr(40))
    tw = bbox[2]-bbox[0]
    ud.text((W//2 - tw//2, H - 130), url_text,
            font=fr(40), fill=(*WHITE, int(255*url_a*0.75)))
    canvas = Image.alpha_composite(canvas, url_layer)

    # ── Pulse glow on $35 (after 1s) ─────────────────────────────────────────
    if t >= 1.0:
        pulse = 0.10 + 0.06*math.sin((t-1.0)*math.pi*2.2)
        glow  = Image.new("RGBA", (W, H), (0,0,0,0))
        ImageDraw.Draw(glow).ellipse(
            [cx_right-130, 700, cx_right+130, 920],
            fill=(*GOLD, int(255*pulse))
        )
        glow   = glow.filter(ImageFilter.GaussianBlur(40))
        canvas = Image.alpha_composite(canvas, glow)

    return np.array(canvas.convert("RGB"))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "output", "v1_1_splitscreen.mp4")
os.makedirs(os.path.dirname(out), exist_ok=True)
VideoClip(make_frame, duration=6).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf","18","-pix_fmt","yuv420p","-movflags","+faststart"],
    logger="bar"
)
print(f"\n✔  Saved → {out}")
