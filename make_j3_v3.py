"""
AuraEase J3 v3  |  1080x1920  |  10s  |  30fps  |  no audio
Mystery hook → Invisible patch reveal → Features → CTA loop
"""

import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip, concatenate_videoclips
from functools import lru_cache

W, H   = 1080, 1920
FPS    = 30
SAFE_W = int(W * 0.82)

NAVY      = (27,  42,  74)
WHITE     = (255, 255, 255)
GOLD      = (201, 169, 110)
BLACK     = (0,   0,   0)

_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_OBLIQUE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"
if not os.path.exists(_OBLIQUE):
    _OBLIQUE = _BOLD

@lru_cache(maxsize=30)
def fb(sz):
    return ImageFont.truetype(_BOLD, sz)

@lru_cache(maxsize=30)
def fo(sz):
    return ImageFont.truetype(_OBLIQUE, sz)

_DD = ImageDraw.Draw(Image.new("RGB", (1, 1)))

# ── Helpers ───────────────────────────────────────────────────────────────────
def eo(t, d):
    p = max(0., min(1., t / max(d, 1e-9)))
    return 1 - (1 - p) ** 3

def crossfade(a_img, b_img, alpha):
    a = np.array(a_img, dtype=float)
    b = np.array(b_img, dtype=float)
    return Image.fromarray((a * (1 - alpha) + b * alpha).astype(np.uint8))

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

def put_text(img, text, cy, fnt, color, alpha=1.0, dx=0, dy=0):
    lines = _wrap(text, fnt)
    lh    = fnt.size + 14
    y0    = (cy + dy) - len(lines) * lh // 2
    canvas = img.convert("RGBA")
    layer  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d      = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=fnt)
        tw   = bbox[2] - bbox[0]
        x    = (W - tw) // 2 + dx
        d.text((x, y0 + i * lh), ln, font=fnt, fill=(*color[:3], int(255 * alpha)))
    return Image.alpha_composite(canvas, layer).convert("RGB")

def put_text_left(img, text, x_left, cy, fnt, color, alpha=1.0):
    """Text placed with its left edge at x_left, vertically centered on cy."""
    lh     = fnt.size + 14
    y0     = cy - lh // 2
    canvas = img.convert("RGBA")
    layer  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((x_left, y0), text, font=fnt,
                               fill=(*color[:3], int(255 * alpha)))
    return Image.alpha_composite(canvas, layer).convert("RGB")

def put_typewriter(img, text, cy, fnt, color, t, start, dur):
    elapsed  = max(0., t - start)
    progress = min(1., elapsed / max(dur, 1e-9))
    n        = int(len(text) * progress)
    visible  = text[:n]
    if not visible:
        return img
    cursor = "|" if int(t * 12) % 2 == 0 and n < len(text) else ""
    return put_text(img, visible + cursor, cy, fnt, color, alpha=1.0)

def put_glow(img, text, cy, fnt, txt_col,
             glow_col=GOLD, radius=28, glow_a=0.55, txt_a=1.0):
    bbox = _DD.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y   = (W - tw) // 2, cy - th // 2
    canvas = img.convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).text((x, y), text, font=fnt,
                           fill=(*glow_col, int(255 * glow_a)))
    g = g.filter(ImageFilter.GaussianBlur(radius))
    canvas = Image.alpha_composite(canvas, g)
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(tl).text((x, y), text, font=fnt,
                            fill=(*txt_col, int(255 * txt_a)))
    return Image.alpha_composite(canvas, tl).convert("RGB")

# ── Stick figure (upright) ────────────────────────────────────────────────────
FIG_CX = W // 2
FIG_CY = 1290   # hips; head ≈ y960, feet ≈ y1660

def _fig_pts():
    cx, cy = FIG_CX, FIG_CY
    return dict(
        head        = (cx,       cy - 330),
        neck        = (cx,       cy - 282),
        left_sh     = (cx - 88,  cy - 245),
        right_sh    = (cx + 88,  cy - 245),
        sh_mid      = (cx,       cy - 245),
        mid_spine   = (cx,       cy - 120),
        lower_back  = (cx,       cy -  55),   # between mid_spine and hips
        left_hip    = (cx - 55,  cy),
        right_hip   = (cx + 55,  cy),
        hip_mid     = (cx,       cy),
        left_elbow  = (cx - 128, cy - 110),
        right_elbow = (cx + 128, cy - 110),
        left_hand   = (cx - 115, cy +  30),
        right_hand  = (cx + 115, cy +  30),
        left_knee   = (cx - 55,  cy + 185),
        right_knee  = (cx + 55,  cy + 185),
        left_foot   = (cx - 60,  cy + 370),
        right_foot  = (cx + 60,  cy + 370),
    )

def draw_figure(img, color, alpha):
    p   = _fig_pts()
    c   = (*color, int(255 * alpha))
    lw, lwa, hr = 22, 16, 46
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    hx, hy = p['head']
    d.ellipse([(hx - hr, hy - hr), (hx + hr, hy + hr)], fill=c)
    d.line([p['head'],    p['neck']],                    fill=c, width=lw)
    d.line([p['left_sh'], p['right_sh']],                fill=c, width=lw)
    d.line([p['neck'],    p['sh_mid']],                  fill=c, width=lw)
    d.line([p['sh_mid'],  p['mid_spine'], p['hip_mid']], fill=c, width=lw)
    d.line([p['left_sh'],  p['left_elbow'],  p['left_hand']],  fill=c, width=lwa)
    d.line([p['right_sh'], p['right_elbow'], p['right_hand']], fill=c, width=lwa)
    d.line([p['left_hip'], p['right_hip']],              fill=c, width=lw)
    d.line([p['left_hip'],  p['left_knee'],  p['left_foot']],  fill=c, width=lw)
    d.line([p['right_hip'], p['right_knee'], p['right_foot']], fill=c, width=lw)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_lower_back_patch(img, alpha, glow_t=0.0):
    p        = _fig_pts()
    lbx, lby = p['lower_back']
    pw, ph   = 100, 62
    gr       = int(18 + 8 * (0.5 + 0.5 * math.sin(glow_t * math.pi * 2.5)))
    glow     = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [(lbx - pw//2 - 10, lby - ph//2 - 10),
         (lbx + pw//2 + 10, lby + ph//2 + 10)],
        radius=18, fill=(*GOLD, int(255 * alpha * 0.55))
    )
    glow = glow.filter(ImageFilter.GaussianBlur(gr))
    rect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rect).rounded_rectangle(
        [(lbx - pw//2, lby - ph//2), (lbx + pw//2, lby + ph//2)],
        radius=12, fill=(*GOLD, int(255 * alpha)),
        outline=(*WHITE, int(255 * alpha * 0.9)), width=4,
    )
    canvas = img.convert("RGBA")
    canvas = Image.alpha_composite(canvas, glow)
    canvas = Image.alpha_composite(canvas, rect)
    return canvas.convert("RGB")

# ── Fade wrapper ──────────────────────────────────────────────────────────────
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
# SCENE 1 (0-2s): Mystery hook — fast letter-by-letter on navy
# ──────────────────────────────────────────────────────────────────────────────
_S1A = "Nobody knows..."
_S1B = "I'm doing therapy right now ~"

def scene1(t):
    img = Image.new("RGB", (W, H), NAVY)
    img = put_typewriter(img, _S1A, H//2 - 200, fb(65), WHITE,
                         t, start=0.05, dur=0.55)
    img = put_typewriter(img, _S1B, H//2 - 40,  fb(50), GOLD,
                         t, start=0.75, dur=0.95)
    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 2 (2-5s, 3s): Reveal — upright silhouette, gold patch, bouncing label
# ──────────────────────────────────────────────────────────────────────────────
def scene2(t):
    img = Image.new("RGB", (W, H), WHITE)

    # Silhouette fades in
    img = draw_figure(img, NAVY, eo(t, 0.55))

    # Gold patch on lower back
    if t >= 0.40:
        img = draw_lower_back_patch(img, eo(t - 0.40, 0.50), glow_t=t)

    # Arrow label — left edge anchored just right of the patch, bounces
    if t >= 0.65:
        a_arr   = eo(t - 0.65, 0.45)
        # bounce: ±8px horizontal nudge (3.5 Hz) simulates pointing motion
        bounce  = int(8 * math.sin((t - 0.65) * math.pi * 3.5))
        lbx, lby = _fig_pts()['lower_back']
        # patch right edge = lbx + 50; start text 20px further right
        img = put_text_left(img, "← AuraEase™ patch",
                            lbx + 70 + bounce, lby, fb(34), NAVY, alpha=a_arr)

    # Feature text in upper region (above figure head ≈ y960)
    a1 = eo(max(0., t - 0.90), 0.50)
    img = put_text(img, "Invisible under any outfit.",
                   430, fb(48), NAVY, alpha=a1, dy=int((1 - a1) * 50))

    if t >= 1.65:
        a2 = eo(t - 1.65, 0.50)
        img = put_text(img, "No wires. No bulk. No smell.",
                       570, fb(40), GOLD, alpha=a2)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 3 (5-8s, 3s): Features — icon + text lines fade+slide in sequence
#   ❄ (U+2744), ★ (U+2605), ● (U+25CF) as emoji substitutes
# ──────────────────────────────────────────────────────────────────────────────
_S3_LINES = [
    ("❄  Cold therapy for inflammation", WHITE, 42, 0.15),
    ("★  Hot therapy for tension",        WHITE, 42, 1.05),
    ("●  Works in 30 seconds",            GOLD,  42, 1.95),
]
_S3_CY = [H//2 - 190, H//2 - 10, H//2 + 170]

def scene3(t):
    img = Image.new("RGB", (W, H), NAVY)
    for (text, color, sz, delay), cy in zip(_S3_LINES, _S3_CY):
        lt = t - delay
        if lt < 0:
            continue
        a  = eo(lt, 0.45)
        dy = int((1 - a) * 42)
        img = put_text(img, text, cy, fb(sz), color, alpha=a, dy=dy)
    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 4 (8-10s, 2s): CTA — navy matches Scene 1 for seamless loop
# ──────────────────────────────────────────────────────────────────────────────
def scene4(t):
    img = Image.new("RGB", (W, H), NAVY)

    a1  = eo(t, 1.1)
    img = put_glow(img, "AuraEase™",
                   H//2 - 130, fb(75), WHITE,
                   glow_col=GOLD, radius=34, glow_a=0.50 * a1, txt_a=a1)

    if t >= 0.40:
        a2 = eo(t - 0.40, 0.65)
        img = put_text(img, "Your secret weapon ~",
                       H//2 + 45, fo(40), GOLD, alpha=a2)

    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 2.4))
    img   = put_text(img, "Link in bio  →",
                     H//2 + 255, fb(32), WHITE, alpha=pulse)

    return np.array(img)

# ── BUILD ─────────────────────────────────────────────────────────────────────
def build():
    FD    = 0.3
    clips = [
        VideoClip(wf(scene1, 2.0, FD), duration=2.0),
        VideoClip(wf(scene2, 3.0, FD), duration=3.0),
        VideoClip(wf(scene3, 3.0, FD), duration=3.0),
        VideoClip(wf(scene4, 2.0, FD), duration=2.0),
    ]
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "auraease_j3_v3.mp4"
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
