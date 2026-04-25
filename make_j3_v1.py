"""
AuraEase J3 v1  |  1080x1920  |  10s  |  30fps  |  no audio
Hook → Solution → Proof → CTA (seamless loop back to Scene 1)
"""

import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip, concatenate_videoclips
from functools import lru_cache

W, H   = 1080, 1920
FPS    = 30
SAFE_W = int(W * 0.82)

NAVY  = (27,  42,  74)
WHITE = (255, 255, 255)
GOLD  = (201, 169, 110)
RED   = (255,  68,  68)
BLACK = (0,   0,   0)
DEEP_NAVY = (10, 18, 40)
GOLD_FILL = (55,  72, 110)  # dark blue-ish fill inside patch

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@lru_cache(maxsize=30)
def fb(sz):
    return ImageFont.truetype(_BOLD, sz)

_DD = ImageDraw.Draw(Image.new("RGB", (1, 1)))

# ── Helpers ───────────────────────────────────────────────────────────────────
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

def put_typewriter(img, text, cy, fnt, color, t, start, dur):
    elapsed  = max(0., t - start)
    progress = min(1., elapsed / max(dur, 1e-9))
    n        = int(len(text) * progress)
    visible  = text[:n]
    if not visible:
        return img
    cursor = "|" if int(t * 10) % 2 == 0 and n < len(text) else ""
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

def draw_circle(img, cx, cy, r, color, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(
        [(cx-r, cy-r), (cx+r, cy+r)], fill=(*color, int(255 * alpha))
    )
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_patch(img, cy, alpha, glow_t=0.0):
    """Gold rectangle centered at cy, slides from off-screen bottom."""
    pw, ph = 540, 290
    cx     = W // 2
    x0, y0 = cx - pw//2, cy - ph//2
    x1, y1 = cx + pw//2, cy + ph//2

    # Glow pulse
    glow_r  = int(22 + 8 * (0.5 + 0.5 * math.sin(glow_t * math.pi * 2.5)))
    glow    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [(x0-12, y0-12), (x1+12, y1+12)], radius=36,
        fill=(*GOLD, int(255 * alpha * 0.45))
    )
    glow = glow.filter(ImageFilter.GaussianBlur(glow_r))

    rect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rect).rounded_rectangle(
        [(x0, y0), (x1, y1)], radius=26,
        fill=(*GOLD_FILL, int(255 * alpha)),
        outline=(*GOLD, int(255 * alpha)),
        width=7,
    )
    canvas = img.convert("RGBA")
    canvas = Image.alpha_composite(canvas, glow)
    canvas = Image.alpha_composite(canvas, rect)
    return canvas.convert("RGB")

# ── Scene 1 at t=0 (used for seamless loop frame) ─────────────────────────────
def _s1_loop_frame():
    img   = Image.new("RGB", (W, H), WHITE)
    pulse = abs(math.sin(0))   # = 0, small circle at start
    r     = int(105 + 50 * max(pulse, 0.25))
    img   = draw_circle(img, W//2, H//2 + 60, r, RED, 0.82)
    img   = draw_circle(img, W//2, H//2 + 60, r + 45, RED, 0.18)
    return img

_LOOP_FRAME = _s1_loop_frame()

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

def wf_loop(fn, dur, fd=0.3):
    """Like wf but fades TO Scene 1 at the end instead of black."""
    def frame(t):
        img = Image.fromarray(fn(t))
        if t < fd:
            img = crossfade(_BLK, img, max(0., t / fd))
        elif t > dur - fd:
            frac = max(0., (dur - t) / fd)   # 1→0 as we reach end
            img  = crossfade(_LOOP_FRAME, img, frac)
        return np.array(img)
    return frame

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 1 (0-2s): Hook — rapid 3× pulse + fast typewriter
# ──────────────────────────────────────────────────────────────────────────────
_S1A = "POV: 3PM at your desk."
_S1B = "Your back is literally on fire ★"

def scene1(t):
    img   = Image.new("RGB", (W, H), WHITE)

    # 3 full pulses in 2s = 1.5 Hz → abs(sin(t*π*1.5)) gives 3 peaks
    pulse = abs(math.sin(t * math.pi * 1.5))
    r     = int(105 + 50 * pulse)
    a_c   = min(1.0, t / 0.2)

    img = draw_circle(img, W//2, H//2 + 60, r, RED, a_c * 0.85)
    img = draw_circle(img, W//2, H//2 + 60, r + 45, RED, a_c * (0.12 + 0.12 * pulse))

    # Fast typewriter — line 1 starts immediately, line 2 at 0.75s
    img = put_typewriter(img, _S1A, H//2 - 290, fb(55), NAVY, t, start=0.05, dur=0.65)
    img = put_typewriter(img, _S1B, H//2 - 195, fb(50), RED,  t, start=0.75, dur=0.70)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 2 (2-5s, 3s): Solution — patch slides up, red fades, glow
# ──────────────────────────────────────────────────────────────────────────────
def scene2(t):
    img = Image.new("RGB", (W, H), NAVY)

    # Red circle fades out over 1.1s
    a_red = max(0., 1.0 - t / 1.1)
    if a_red > 0:
        img = draw_circle(img, W//2, H//2 + 60, 140, RED, a_red * 0.75)

    # Gold patch slides in from below
    slide    = eo(t, 0.7)
    target_y = H // 2 + 60
    patch_y  = int((H + 200) * (1 - slide) + target_y * slide)
    a_patch  = eo(t, 0.6)
    img = draw_patch(img, patch_y, a_patch, glow_t=t)

    # Text fades in
    a_brand = eo(max(0., t - 0.5), 0.7)
    img = put_glow(img, "AuraEase™",
                   H//2 - 260, fb(70), WHITE,
                   glow_col=GOLD, radius=34, glow_a=0.5 * a_brand, txt_a=a_brand)

    if t >= 0.9:
        a_sub = eo(t - 0.9, 0.6)
        img = put_text(img, "Instant hot & cold relief.",
                       H//2 - 155, fb(42), GOLD, alpha=a_sub)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 3 (5-8s, 3s): Proof — 3 checkmarks slide rapidly from left
# ──────────────────────────────────────────────────────────────────────────────
_CHECKS = [
    ("✓  Works in 30 seconds",    NAVY, 48, 0.0),
    ("✓  Invisible under clothes", NAVY, 48, 0.3),
    ("✓  $35 vs $150 physio",      GOLD, 48, 0.6),
]
_CHECK_CY = [H//2 - 120, H//2 + 40, H//2 + 200]

def scene3(t):
    img = Image.new("RGB", (W, H), WHITE)
    for (text, color, sz, delay), cy in zip(_CHECKS, _CHECK_CY):
        lt = t - delay
        if lt < 0:
            continue
        a  = eo(lt, 0.30)
        dx = int((1 - a) * -120)
        img = put_text(img, text, cy, fb(sz), color, alpha=a, dx=dx)
    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 4 (8-10s, 2s): CTA → fades to Scene 1 loop frame at the end
# ──────────────────────────────────────────────────────────────────────────────
def scene4(t):
    img = vgrad(NAVY, DEEP_NAVY)

    a1  = eo(t, 1.2)
    img = put_glow(img, "AuraEase™",
                   H//2 - 130, fb(75), WHITE,
                   glow_col=GOLD, radius=34, glow_a=0.5 * a1, txt_a=a1)

    if t >= 0.35:
        a2 = eo(t - 0.35, 0.7)
        img = put_text(img, "Stop the fire. Start the relief.",
                       H//2 + 40, fb(38), GOLD, alpha=a2)

    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 2.4))
    img   = put_text(img, "Link in bio  →",
                     H//2 + 250, fb(32), WHITE, alpha=pulse)

    return np.array(img)

# ── BUILD ─────────────────────────────────────────────────────────────────────
def build():
    FD = 0.3
    clips = [
        VideoClip(wf(scene1,       2.0, FD), duration=2.0),
        VideoClip(wf(scene2,       3.0, FD), duration=3.0),
        VideoClip(wf(scene3,       3.0, FD), duration=3.0),
        VideoClip(wf_loop(scene4,  2.0, FD), duration=2.0),  # ends on loop frame
    ]
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "auraease_j3_v1.mp4"
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
