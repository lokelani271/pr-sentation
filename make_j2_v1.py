"""
AuraEase J2 v1  |  1080x1920  |  12s  |  30fps  |  no audio
Scenes: Typewriter Pain → Patch Reveal → Checkmarks → CTA
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
GRAY      = (150, 150, 160)
BLACK     = (0,   0,   0)
PAIN_RED  = (210,  55,  55)
DEEP_NAVY = (10,  18,  40)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@lru_cache(maxsize=30)
def fb(sz):
    return ImageFont.truetype(_BOLD, sz)

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

def put_text(img, text, cy, fnt, color, alpha=1.0, dx=0, dy=0, max_w=None):
    lines = _wrap(text, fnt, max_w)
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

def put_typewriter(img, full_text, cy, fnt, color, t, start=0.3, duration=2.2):
    """Reveal full_text character-by-character over `duration` seconds after `start`."""
    elapsed  = max(0., t - start)
    progress = min(1., elapsed / duration)
    n_chars  = int(len(full_text) * progress)
    # Keep whole words so wrapping is stable
    visible = full_text[:n_chars]
    if not visible:
        return img
    # Add blinking cursor while typing
    cursor = "|" if (int(t * 8) % 2 == 0 and n_chars < len(full_text)) else ""
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

    t_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(t_layer).text((x, y), text, font=fnt,
                                 fill=(*txt_col, int(255 * txt_a)))
    return Image.alpha_composite(canvas, t_layer).convert("RGB")

def draw_circle_alpha(img, cx, cy, r, color, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(
        [(cx - r, cy - r), (cx + r, cy + r)],
        fill=(*color, int(255 * alpha))
    )
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_rect_alpha(img, x0, y0, x1, y1, fill_col, border_col, border_w, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        [(x0, y0), (x1, y1)], radius=24,
        fill=(*fill_col, int(255 * alpha)),
        outline=(*border_col, int(255 * alpha)),
        width=border_w
    )
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

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

# ── SCENE 1 (0-3s): Typewriter pain text + pulsing circle ────────────────────
_S1_TEXT = "POV: Your neck is on fire after back-to-back meetings."

def scene1(t):
    img = Image.new("RGB", (W, H), WHITE)

    # Pulsing red circle
    pulse  = 0.5 + 0.5 * math.sin(t * math.pi * 2.0)
    r      = int(115 + 20 * pulse)
    a_circ = min(1.0, t / 0.3)
    img = draw_circle_alpha(img, W // 2, H // 2 + 120, r, PAIN_RED, a_circ)
    img = draw_circle_alpha(img, W // 2, H // 2 + 120, r + 40, PAIN_RED,
                            a_circ * (0.20 + 0.15 * pulse))

    # Typewriter text above circle
    img = put_typewriter(img, _S1_TEXT, H // 2 - 200, fb(50), NAVY,
                         t, start=0.2, duration=2.3)

    return np.array(img)

# ── SCENE 2 (3-6s): Patch reveal, red fades ──────────────────────────────────
def scene2(t):
    img = Image.new("RGB", (W, H), NAVY)

    # Red circle fades out over 1.4s
    a_red = max(0., 1.0 - t / 1.4)
    if a_red > 0:
        img = draw_circle_alpha(img, W // 2, H // 2, 125, PAIN_RED, a_red)

    # Patch grows in from 0.3s
    if t >= 0.3:
        a_p  = eo(t - 0.3, 0.6)
        pw   = int(520 * a_p)
        ph   = int(270 * a_p)
        cx, cy = W // 2, H // 2
        img = draw_rect_alpha(img,
                              cx - pw // 2, cy - ph // 2,
                              cx + pw // 2, cy + ph // 2,
                              (40, 65, 110), GOLD, 6, a_p)
        if a_p > 0.55:
            al = (a_p - 0.55) * 2.22
            img = put_text(img, "HOT  |  COLD", H // 2, fb(36), GOLD, alpha=al)

    # Title
    a_txt = eo(max(0., t - 0.4), 0.6)
    img = put_text(img, "AuraEase™ — Instant Relief",
                   H // 2 - 240, fb(50), WHITE, alpha=a_txt)

    return np.array(img)

# ── SCENE 3 (6-9s): Checkmarks slide in ──────────────────────────────────────
_CHECKS = [
    ("✓  Works in 30 seconds",     NAVY, 45, 0.0),
    ("✓  Hot & Cold dual action",  NAVY, 45, 0.6),
    ("✓  Invisible under clothes", GOLD, 45, 1.2),
]
_CHECK_CY = [H // 2 - 140, H // 2 + 20, H // 2 + 180]

def scene3(t):
    img = Image.new("RGB", (W, H), WHITE)
    for (text, color, sz, delay), cy in zip(_CHECKS, _CHECK_CY):
        lt = t - delay
        if lt < 0:
            continue
        a  = eo(lt, 0.45)
        dx = int((1 - a) * -90)
        img = put_text(img, text, cy, fb(sz), color, alpha=a, dx=dx)
    return np.array(img)

# ── SCENE 4 (9-12s): CTA ─────────────────────────────────────────────────────
def scene4(t):
    img = vgrad(NAVY, DEEP_NAVY)

    a1  = eo(t, 1.5)
    img = put_glow(img, "AuraEase™",
                   H // 2 - 120, fb(80), WHITE,
                   glow_col=GOLD, radius=32, glow_a=0.5 * a1, txt_a=a1)

    if t >= 0.5:
        a2  = eo(t - 0.5, 0.8)
        img = put_text(img, "$35 vs $150 physio",
                       H // 2 + 40, fb(45), GOLD, alpha=a2)

    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 2.2))
    img   = put_text(img, "Link in bio  →",
                     H // 2 + 300, fb(35), WHITE, alpha=pulse)

    return np.array(img)

# ── BUILD ─────────────────────────────────────────────────────────────────────
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
        "auraease_j2_v1.mp4"
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
