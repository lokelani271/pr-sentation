"""
auraease_ice_bath_v2.mp4 — 10s, 3 scenes with 0.3s crossfades
Scene 1 (0-3s):  Dark gym + red pain glow bg  | "Hate ice baths? / Same."
Scene 2 (3-7s):  Clean white product bg        | "Targeted cold therapy / without the freeze / $35..."
Scene 3 (7-10s): Dark gym relief bg            | "Recover smarter. / AuraEase™ / Link in bio"

Kling AI images can be substituted by renaming them:
  kling_pain.png / kling_patch.png / kling_relief.png → place in same folder
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

NAVY  = (27,  42,  74)
GOLD  = (201, 169, 110)
WHITE = (255, 255, 255)
RED   = (220,  60,  30)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_PATHS_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

@lru_cache(maxsize=32)
def fb(size, bold=True):
    paths = FONT_PATHS if bold else FONT_PATHS_REG
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

MAX_W = W - 120

def fit_font(txt, max_size, bold=True):
    size = max_size
    while size > 28:
        fnt = fb(size, bold)
        bb = ImageDraw.Draw(Image.new("RGBA", (1,1))).textbbox((0,0), txt, font=fnt)
        if bb[2]-bb[0] <= MAX_W:
            return fnt, size
        size -= 3
    return fb(28, bold), 28

def draw_text(d, txt, cy_or_y, color, max_size, bold=True, center=True, alpha=255, fixed_y=False):
    fnt, sz = fit_font(txt, max_size, bold)
    bb = d.textbbox((0,0), txt, font=fnt)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    x = (W - tw)//2 if center else 60
    y = cy_or_y if fixed_y else cy_or_y - th//2
    r,g,b = color
    d.text((x, y), txt, font=fnt, fill=(r,g,b,alpha))

# ── Background generators ────────────────────────────────────────────────

def bg_gym_pain():
    """Dark gym feel with red pain glow at lower center — like the knee pain shot."""
    img = Image.new("RGB", (W, H), (18, 18, 22))
    d = ImageDraw.Draw(img)
    # subtle dark gradient
    for y in range(H):
        brightness = int(10 + 30 * (1 - y/H))
        d.line([(0,y),(W,y)], fill=(brightness, brightness-2, brightness-5))
    # red pain glow bottom area
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for r in [320, 220, 130, 60]:
        a = int(120 * (60/(r+10)))
        gd.ellipse([(W//2-r, H*3//4-r//2), (W//2+r, H*3//4+r//2)],
                   fill=(220, 50, 20, min(a,200)))
    blurred = glow.filter(ImageFilter.GaussianBlur(radius=40))
    img.paste(blurred.convert("RGB"), mask=blurred.split()[3])
    return img

def bg_product():
    """Clean off-white / light gray — product shot feel."""
    img = Image.new("RGB", (W, H), (242, 240, 238))
    d = ImageDraw.Draw(img)
    # soft vignette
    for r in range(500, 0, -20):
        a = int(15 * (1 - r/500))
        d.ellipse([(W//2-r, H//2-r), (W//2+r, H//2+r)],
                  outline=(200,198,196), width=0)
    return img

def bg_gym_relief():
    """Dark gym but slightly lighter/warmer — post-relief feel."""
    img = Image.new("RGB", (W, H), (22, 20, 28))
    d = ImageDraw.Draw(img)
    for y in range(H):
        br = int(8 + 25 * (1 - y/H))
        d.line([(0,y),(W,y)], fill=(br, br-1, br+2))
    # soft warm glow top-center (ceiling light)
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for r in [280, 180, 90]:
        a = int(60 * (90/(r+10)))
        gd.ellipse([(W//2-r, 60-r//3), (W//2+r, 60+r//3+r)],
                   fill=(255, 240, 200, min(a,150)))
    blurred = glow.filter(ImageFilter.GaussianBlur(radius=35))
    img.paste(blurred.convert("RGB"), mask=blurred.split()[3])
    return img

# Pre-render backgrounds (static, applied once)
_BG = {
    "pain":    bg_gym_pain(),
    "product": bg_product(),
    "relief":  bg_gym_relief(),
}

def load_bg_override(name):
    """Allow kling_pain.png / kling_patch.png / kling_relief.png if present."""
    mapping = {"pain": "kling_pain", "product": "kling_patch", "relief": "kling_relief"}
    for ext in [".mp4", ".png", ".jpg"]:
        path = mapping[name] + ext
        if os.path.exists(path):
            if ext == ".mp4":
                try:
                    from moviepy.editor import VideoFileClip
                except ImportError:
                    from moviepy import VideoFileClip
                frames = list(VideoFileClip(path).iter_frames())
                return Image.fromarray(frames[len(frames)//2]).resize((W,H), Image.LANCZOS)
            else:
                return Image.open(path).convert("RGB").resize((W,H), Image.LANCZOS)
    return _BG[name]

BG1 = load_bg_override("pain")
BG2 = load_bg_override("product")
BG3 = load_bg_override("relief")

# ── Scene renderers ────────────────────────────────────────────────────────

def dark_overlay(img, strength=0.45):
    """Semi-transparent dark layer so white text is readable on any bg."""
    dark = Image.new("RGBA", (W,H), (0,0,0, int(strength*255)))
    base = img.convert("RGBA")
    base.alpha_composite(dark)
    return base.convert("RGB")

def scene1(t, dur=3.0):
    """Hate ice baths? / Same. — top overlay captions."""
    p = min(t/0.3, 1.0)
    img = dark_overlay(BG1, 0.42)
    overlay = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(overlay)

    a1 = int(min(t/0.3, 1.0) * 255)
    a2 = int(min(max(t-0.2,0)/0.3, 1.0) * 255)

    draw_text(d, "Hate ice baths?", 150, WHITE, 80,  alpha=a1, fixed_y=True)
    draw_text(d, "Same.",           270, WHITE, 95,  alpha=a2, fixed_y=True)

    img.paste(overlay.convert("RGB"), mask=overlay.split()[3])
    return np.array(img)

def scene2(t, dur=4.0):
    """Targeted cold therapy / without the freeze / $35 bottom."""
    img = dark_overlay(BG2, 0.20)
    overlay = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(overlay)

    a1 = int(min(t/0.3, 1.0) * 255)
    a2 = int(min(max(t-0.2,0)/0.3, 1.0) * 255)
    a3 = int(min(max(t-0.4,0)/0.3, 1.0) * 255)

    draw_text(d, "Targeted cold therapy",   150, WHITE, 65, alpha=a1, fixed_y=True)
    draw_text(d, "without the freeze. \U0001f9ca", 255, GOLD,  60, alpha=a2, fixed_y=True)
    draw_text(d, "$35 for 200+ uses.",      1600, WHITE, 52, bold=False, alpha=a3, fixed_y=True)

    img.paste(overlay.convert("RGB"), mask=overlay.split()[3])
    return np.array(img)

def scene3(t, dur=3.0):
    """Recover smarter. / AuraEase™ center / Link in bio bottom."""
    fade_out = min((dur - t) / 0.30, 1.0)
    img = dark_overlay(BG3, 0.45)
    overlay = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(overlay)

    a1 = int(min(t/0.3, 1.0) * fade_out * 255)
    a2 = int(min(max(t-0.2,0)/0.3, 1.0) * fade_out * 255)
    a3 = int(min(max(t-0.4,0)/0.3, 1.0) * fade_out * 255)

    draw_text(d, "Recover smarter.",  150,  WHITE, 82, alpha=a1, fixed_y=True)
    draw_text(d, "AuraEase™",    800,  GOLD,  90, alpha=a2, fixed_y=True)
    draw_text(d, "Link in bio \U0001f517", 1700, WHITE, 50, bold=False, alpha=a3, fixed_y=True)

    img.paste(overlay.convert("RGB"), mask=overlay.split()[3])
    return np.array(img)

# ── Scene timing ────────────────────────────────────────────────────────────
CUT = [0.0, 3.0, 7.0, 10.0]
SCENE_FNS = [scene1, scene2, scene3]
SCENE_DURS = [3.0, 4.0, 3.0]

def crossfade(a, b, alpha):
    return (a.astype(float)*(1-alpha) + b.astype(float)*alpha).astype(np.uint8)

def make_frame(t):
    sc = 0
    for i in range(len(CUT)-1):
        if CUT[i] <= t < CUT[i+1]:
            sc = i; break
    else:
        sc = len(SCENE_FNS)-1

    local_t   = t - CUT[sc]
    scene_dur = SCENE_DURS[sc]
    frame_a   = SCENE_FNS[sc](local_t, scene_dur)

    if sc < len(SCENE_FNS)-1 and local_t >= scene_dur - XF:
        xf = min(max((local_t - (scene_dur-XF)) / XF, 0), 1)
        frame_b = SCENE_FNS[sc+1](0.0, SCENE_DURS[sc+1])
        return crossfade(frame_a, frame_b, xf)

    return frame_a

os.makedirs("output", exist_ok=True)
out = "output/auraease_ice_bath_v2.mp4"
VideoClip(make_frame, duration=TOTAL).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf","18","-pix_fmt","yuv420p",
                   "-movflags","+faststart","-preset","medium"],
    logger=None,
)
print(f"\nDone → {out}")
