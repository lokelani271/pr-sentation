"""
AuraEase TikTok — script2  |  1080x1920  |  12s  |  30fps  |  no audio
Scenes: Split-screen Hook → Agitation → Solution → Loop CTA
"""

import os
import math
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
GRAY      = (160, 160, 170)
DARK_GRAY = (80,  80,  90)
BLACK     = (0,   0,   0)
DEEP_NAVY = (12,  20,  48)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Font cache ─────────────────────────────────────────────────────────────────
@lru_cache(maxsize=30)
def fb(sz):
    return ImageFont.truetype(_BOLD, sz)

@lru_cache(maxsize=30)
def fr(sz):
    return ImageFont.truetype(_REG, sz)

# ── Animation helpers ──────────────────────────────────────────────────────────
def eo(t, d):
    """Cubic ease-out: 0 → 1 over d seconds."""
    p = max(0.0, min(1.0, t / max(d, 1e-9)))
    return 1 - (1 - p) ** 3

def crossfade_imgs(a_img, b_img, alpha):
    """Blend two RGB PIL images; alpha=0 → a_img, alpha=1 → b_img."""
    a = np.array(a_img, dtype=float)
    b = np.array(b_img, dtype=float)
    return Image.fromarray((a * (1 - alpha) + b * alpha).astype(np.uint8))

def vgrad(c1, c2):
    """Vertical gradient PIL image: c1 at top, c2 at bottom."""
    ratio = np.linspace(0, 1, H).reshape(H, 1)
    arr   = (np.array(c1) * (1 - ratio) + np.array(c2) * ratio).astype(np.uint8)
    arr   = arr.reshape(H, 1, 3)
    return Image.fromarray(np.broadcast_to(arr, (H, W, 3)).copy())

# ── Text helpers ───────────────────────────────────────────────────────────────
_DUMMY_DRAW = ImageDraw.Draw(Image.new("RGB", (1, 1)))

def _wrap(text, fnt):
    words = text.split()
    lines, line = [], ""
    for w in words:
        cand = f"{line} {w}".strip()
        if _DUMMY_DRAW.textbbox((0, 0), cand, font=fnt)[2] <= SAFE_W:
            line = cand
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines or [text]

def put_text(img, text, cy, fnt, color, dx=0, alpha=1.0, dy=0):
    """Draw centered, wrapped text block at vertical center cy+dy."""
    lines  = _wrap(text, fnt)
    sz     = fnt.size
    lh     = sz + 14
    y0     = (cy + dy) - (len(lines) * lh) // 2

    canvas = img.convert("RGBA")
    layer  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d      = ImageDraw.Draw(layer)

    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=fnt)
        tw   = bbox[2] - bbox[0]
        x    = (W - tw) // 2 + dx
        y    = y0 + i * lh
        d.text((x, y), ln, font=fnt, fill=(*color[:3], int(255 * alpha)))

    return Image.alpha_composite(canvas, layer).convert("RGB")

def put_glow(img, text, cy, fnt, txt_col, glow_col=GOLD,
             radius=22, glow_a=0.6, txt_a=1.0):
    """Text with soft gaussian glow halo centered at cy."""
    bbox  = _DUMMY_DRAW.textbbox((0, 0), text, font=fnt)
    tw    = bbox[2] - bbox[0]
    th    = bbox[3] - bbox[1]
    x     = (W - tw) // 2
    y     = cy - th // 2

    canvas = img.convert("RGBA")

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((x, y), text, font=fnt,
                              fill=(*glow_col, int(255 * glow_a)))
    glow = glow.filter(ImageFilter.GaussianBlur(radius))
    canvas = Image.alpha_composite(canvas, glow)

    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(txt).text((x, y), text, font=fnt,
                             fill=(*txt_col, int(255 * txt_a)))
    return Image.alpha_composite(canvas, txt).convert("RGB")

# ── Fade-through-black wrapper ─────────────────────────────────────────────────
_BLACK = Image.new("RGB", (W, H), BLACK)

def wf(scene_fn, dur, fd=0.3):
    """Wrap scene_fn(t)->ndarray with fade-in/out through black."""
    def make_frame(t):
        img = Image.fromarray(scene_fn(t))
        if t < fd:
            img = crossfade_imgs(_BLACK, img, max(0.0, t / fd))
        elif t > dur - fd:
            img = crossfade_imgs(_BLACK, img, max(0.0, (dur - t) / fd))
        return np.array(img)
    return make_frame

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 1 (0-3s) — SPLIT SCREEN HOOK
# ──────────────────────────────────────────────────────────────────────────────

def scene1(t):
    # Base: white frame
    img = Image.new("RGB", (W, H), WHITE)

    # Navy top half
    img.paste(Image.new("RGB", (W, H // 2), NAVY), (0, 0))

    # Gold divider (4px)
    ImageDraw.Draw(img).rectangle(
        [(0, H // 2 - 2), (W, H // 2 + 2)], fill=GOLD
    )

    a = eo(max(0.0, t - 0.3), 0.4)

    # TOP: white text on navy
    img = put_text(img, "$120 Massage",                H // 4 - 30, fb(80), WHITE,     alpha=a)
    img = put_text(img, "Per session + tip + travel",  H // 4 + 68, fb(34), GRAY,      alpha=a)

    # BOTTOM: navy text on white
    img = put_text(img, "$1.50 AuraEase™",        H * 3 // 4 - 30, fb(80), NAVY,      alpha=a)
    img = put_text(img, "Per patch. Same relief.",      H * 3 // 4 + 68, fb(34), DARK_GRAY, alpha=a)

    # Gold "$" marker pulses into center at 2.5s
    if t >= 2.5:
        ca = eo(t - 2.5, 0.3)
        img = put_text(img, "($)", H // 2, fb(52), GOLD, alpha=ca)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 2 (3-6s) — AGITATION  |  typewriter + headline
# ──────────────────────────────────────────────────────────────────────────────

_TW_WORDS = "$120 + Tip + Travel time + Waiting room...".split()

def scene2(t):
    img = Image.new("RGB", (W, H), NAVY)

    # Typewriter: reveal words over 1.5s
    n = max(1, int(len(_TW_WORDS) * min(t / 1.5, 1.0)))
    img = put_text(img, " ".join(_TW_WORDS[:n]),
                   H // 2 - 270, fb(40), WHITE, alpha=0.9)

    # Main headline slides in from slight offset at 1.0s
    if t >= 1.0:
        a1 = eo(t - 1.0, 0.55)
        dx = int((1 - a1) * -80)
        img = put_text(img, "Why pay for 1 hour",
                       H // 2 - 30, fb(65), WHITE, dx=dx, alpha=a1)

    # Gold answer line at 1.5s
    if t >= 1.5:
        a2 = eo(t - 1.5, 0.55)
        img = put_text(img, "when you can have 12 hours of relief?",
                       H // 2 + 115, fb(46), GOLD, alpha=a2)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 3 (6-9s) — SOLUTION  |  3 lines slide up
# ──────────────────────────────────────────────────────────────────────────────

# Unicode substitutes: ★ (fire energy), ❄ (cold), no emoji needed
_S3 = [
    ("Hot for the knots.  ★",         NAVY, 60),
    ("Cold for the inflammation.  ❄", NAVY, 60),
    ("One patch. Dual action. Discreet.",   GOLD, 40),
]
_S3_CY     = [H // 2 - 180, H // 2 + 10, H // 2 + 185]
_S3_DELAYS = [0.0, 0.5, 1.0]

def scene3(t):
    img = Image.new("RGB", (W, H), WHITE)
    for (text, color, sz), cy, delay in zip(_S3, _S3_CY, _S3_DELAYS):
        lt = t - delay
        if lt < 0:
            continue
        a  = eo(lt, 0.45)
        dy = int((1 - a) * 70)     # slide up 70px
        img = put_text(img, text, cy, fb(sz), color, alpha=a, dy=dy)
    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 4 (9-12s) — LOOP CTA
# ──────────────────────────────────────────────────────────────────────────────

def scene4(t):
    img = vgrad(NAVY, DEEP_NAVY)

    # "The best $1.50" — slow fade + gold glow
    a1 = eo(t, 1.5)
    img = put_glow(img, "The best $1.50",
                   H // 2 - 115, fb(75), WHITE,
                   glow_col=GOLD, radius=30,
                   glow_a=0.45 * a1, txt_a=a1)

    # "I ever spent..." gold italic at 0.5s
    if t >= 0.5:
        a2 = eo(t - 0.5, 1.0)
        img = put_text(img, "I ever spent...",
                       H // 2 + 50, fb(55), GOLD, alpha=a2)

    # Pulsing link CTA (0.6 – 1.0 opacity)
    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 2.2))
    img   = put_text(img, "Link in bio  →",
                     H // 2 + 310, fb(34), WHITE, alpha=pulse)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# BUILD
# ──────────────────────────────────────────────────────────────────────────────

def build():
    FD = 0.3
    clips = [
        VideoClip(wf(scene1, 3.0, FD), duration=3.0),
        VideoClip(wf(scene2, 3.0, FD), duration=3.0),
        VideoClip(wf(scene3, 3.0, FD), duration=3.0),
        VideoClip(wf(scene4, 3.0, FD), duration=3.0),
    ]

    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "auraease_tiktok_script2.mp4"
    )

    final = concatenate_videoclips(clips)
    final.write_videofile(
        out, fps=FPS, codec="libx264", audio=False,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger="bar",
    )
    print(f"\n✔  Saved → {out}")


if __name__ == "__main__":
    build()
