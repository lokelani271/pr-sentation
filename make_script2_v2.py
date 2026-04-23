"""
AuraEase — script2_v2  |  1080x1920  |  12s  |  30fps  |  no audio
Scenes: Split-screen → Agitation → Solution → Loop CTA
"""

import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip, concatenate_videoclips
from functools import lru_cache

# ── Constants ──────────────────────────────────────────────────────────────────
W, H   = 1080, 1920
FPS    = 30
SAFE_W = int(W * 0.82)

NAVY      = (27,  42,  74)
WHITE     = (255, 255, 255)
GOLD      = (201, 169, 110)
GRAY      = (150, 150, 160)
DARK_GRAY = (80,  80,  90)
BLACK     = (0,   0,   0)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ── Font cache ─────────────────────────────────────────────────────────────────
@lru_cache(maxsize=30)
def fb(sz):
    return ImageFont.truetype(_BOLD, sz)

# ── Helpers ────────────────────────────────────────────────────────────────────
_DD = ImageDraw.Draw(Image.new("RGB", (1, 1)))

def eo(t, d):
    p = max(0., min(1., t / max(d, 1e-9)))
    return 1 - (1 - p) ** 3

def crossfade(a_img, b_img, alpha):
    a = np.array(a_img, dtype=float)
    b = np.array(b_img, dtype=float)
    return Image.fromarray((a * (1 - alpha) + b * alpha).astype(np.uint8))

def vgrad(c1, c2):
    ratio = np.linspace(0, 1, H).reshape(H, 1, 1)
    arr   = (np.array(c1) * (1 - ratio) + np.array(c2) * ratio).astype(np.uint8)
    return Image.fromarray(np.broadcast_to(arr, (H, W, 3)).copy())

def _wrap(text, fnt, max_w=None):
    max_w = max_w or SAFE_W
    words = text.split()
    lines, line = [], ""
    for w in words:
        c = f"{line} {w}".strip()
        if _DD.textbbox((0, 0), c, font=fnt)[2] <= max_w:
            line = c
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines or [text]

def put_text(img, text, cy, fnt, color, dx=0, dy=0, alpha=1.0, max_w=None):
    lines = _wrap(text, fnt, max_w)
    lh    = fnt.size + 12
    y0    = (cy + dy) - len(lines) * lh // 2

    canvas = img.convert("RGBA")
    layer  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d      = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=fnt)
        tw   = bbox[2] - bbox[0]
        x    = (W - tw) // 2 + dx
        d.text((x, y0 + i * lh), ln, font=fnt,
               fill=(*color[:3], int(255 * alpha)))
    return Image.alpha_composite(canvas, layer).convert("RGB")

def put_glow(img, text, cy, fnt, txt_col,
             glow_col=GOLD, radius=24, glow_a=0.55, txt_a=1.0):
    bbox = _DD.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y   = (W - tw) // 2, cy - th // 2

    canvas = img.convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).text((x, y), text, font=fnt,
                           fill=(*glow_col, int(255 * glow_a)))
    g = g.filter(ImageFilter.GaussianBlur(radius))
    canvas = Image.alpha_composite(canvas, g)

    t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((x, y), text, font=fnt,
                           fill=(*txt_col, int(255 * txt_a)))
    return Image.alpha_composite(canvas, t).convert("RGB")

# ── Fade-through-black wrapper ─────────────────────────────────────────────────
_BLK = Image.new("RGB", (W, H), BLACK)

def wf(fn, dur, fd=0.3):
    def frame(t):
        img = Image.fromarray(fn(t))
        if t < fd:
            img = crossfade(_BLK, img, max(0., t / fd))
        elif t > dur - fd:
            img = crossfade(_BLK, img, max(0., (dur - t) / fd))
        return np.array(img)
    return frame

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 1 (0-3s) — SPLIT SCREEN HOOK
# ──────────────────────────────────────────────────────────────────────────────

def scene1(t):
    img = Image.new("RGB", (W, H), WHITE)
    img.paste(Image.new("RGB", (W, H // 2), NAVY), (0, 0))
    ImageDraw.Draw(img).rectangle([(0, H // 2 - 2), (W, H // 2 + 2)], fill=GOLD)

    a = eo(max(0., t - 0.3), 0.4)

    # TOP half
    top = H // 4
    img = put_text(img, "Physio appointment",     top - 95,  fb(55), WHITE,     alpha=a)
    img = put_text(img, "$150",                   top + 25,  fb(90), WHITE,     alpha=a)
    img = put_text(img, "Per session. Every week.", top + 118, fb(30), GRAY,    alpha=a)

    # BOTTOM half
    bot = H * 3 // 4
    img = put_text(img, "AuraEase™",               bot - 95,  fb(55), NAVY,      alpha=a)
    img = put_text(img, "$35",                          bot + 25,  fb(90), GOLD,      alpha=a)
    img = put_text(img, "One time. Zero appointment.",  bot + 118, fb(30), DARK_GRAY, alpha=a)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 2 (3-6s) — AGITATION
# ──────────────────────────────────────────────────────────────────────────────

_COST_LINES = [
    ("$150 + travel time",      0.0),
    ("+ waiting room",          0.5),
    ("+ booking 3 weeks ahead", 1.0),
]

def scene2(t):
    img = Image.new("RGB", (W, H), NAVY)

    base_y = H // 2 - 200
    for i, (text, delay) in enumerate(_COST_LINES):
        lt = t - delay
        if lt < 0:
            continue
        a   = eo(lt, 0.4)
        dx  = int((1 - a) * -620)
        img = put_text(img, text, base_y + i * 92, fb(40), WHITE, dx=dx, alpha=a)

    if t >= 1.5:
        a2  = eo(t - 1.5, 0.5)
        img = put_text(img, "Just to get 1 hour of relief?",
                       H // 2 + 130, fb(55), GOLD, alpha=a2)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 3 (6-9s) — SOLUTION
# ──────────────────────────────────────────────────────────────────────────────

# Unicode subs: ★ = fire energy, ❄ = cold/ice
_SOL = [
    ("Hot for the tension.  ★",         NAVY, 58, 0.0),
    ("Cold for the inflammation.  ❄",   NAVY, 58, 0.5),
    ("12 hours. Under your shirt.",          GOLD, 42, 1.0),
]
_SOL_CY = [H // 2 - 155, H // 2 + 20, H // 2 + 185]

def scene3(t):
    img = Image.new("RGB", (W, H), WHITE)

    for (text, color, sz, delay), cy in zip(_SOL, _SOL_CY):
        lt = t - delay
        if lt < 0:
            continue
        a  = eo(lt, 0.45)
        dy = int((1 - a) * 70)
        img = put_text(img, text, cy, fb(sz), color, alpha=a, dy=dy)

    if t >= 1.5:
        a3  = eo(t - 1.5, 0.4)
        img = put_text(img, "Drug-free. Reusable 200+ times.",
                       H // 2 + 340, fb(32), GRAY, alpha=a3)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 4 (9-12s) — LOOP CTA
# ──────────────────────────────────────────────────────────────────────────────

def scene4(t):
    img = vgrad(NAVY, (10, 18, 40))

    a1  = eo(t, 1.5)
    img = put_glow(img, "AuraEase™", H // 2 - 115, fb(80), WHITE,
                   glow_col=GOLD, radius=30, glow_a=0.45 * a1, txt_a=a1)

    if t >= 0.6:
        a2  = eo(t - 0.6, 1.0)
        img = put_text(img, "Same result. No waiting room.",
                       H // 2 + 40, fb(45), GOLD, alpha=a2)

    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 2.2))
    img   = put_text(img, "Link in bio  →",
                     H // 2 + 300, fb(35), WHITE, alpha=pulse)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# BUILD
# ──────────────────────────────────────────────────────────────────────────────

def build():
    FD    = 0.3
    clips = [
        VideoClip(wf(scene1, 3.0, FD), duration=3.0),
        VideoClip(wf(scene2, 3.0, FD), duration=3.0),
        VideoClip(wf(scene3, 3.0, FD), duration=3.0),
        VideoClip(wf(scene4, 3.0, FD), duration=3.0),
    ]
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "auraease_script2_v2.mp4"
    )
    concatenate_videoclips(clips).write_videofile(
        out, fps=FPS, codec="libx264", audio=False,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger="bar",
    )
    print(f"\n✔  Saved → {out}")

if __name__ == "__main__":
    build()
