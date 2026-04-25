"""
AuraEase J3 v2  |  1080x1920  |  10s  |  30fps  |  no audio
Split price slam → Agitation typewriter → Solution silhouette → CTA
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
RED       = (255,  68,  68)
BLACK     = (0,   0,   0)
DEEP_NAVY = (10,  18,  40)

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

def put_text_half(img, text, cy, fnt, color, alpha=1.0, side='left', dx_extra=0):
    """Text centered within left or right half, with optional extra dx offset."""
    hw     = W // 2 - 60
    lines  = _wrap(text, fnt, max_w=hw)
    lh     = fnt.size + 14
    y0     = cy - len(lines) * lh // 2
    cx     = W // 4 if side == 'left' else 3 * W // 4
    canvas = img.convert("RGBA")
    layer  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d      = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=fnt)
        tw   = bbox[2] - bbox[0]
        x    = cx - tw // 2 + dx_extra
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

# ── Stick figure (upright) ────────────────────────────────────────────────────
FIG_CX = W // 2
FIG_CY = 1285   # hips; head ≈ y955, feet ≈ y1655

def _fig_pts():
    cx, cy = FIG_CX, FIG_CY
    return dict(
        head        = (cx,        cy - 330),
        neck        = (cx,        cy - 282),
        left_sh     = (cx - 88,   cy - 245),
        right_sh    = (cx + 88,   cy - 245),
        sh_mid      = (cx,        cy - 245),
        mid_spine   = (cx,        cy - 120),
        left_hip    = (cx - 55,   cy),
        right_hip   = (cx + 55,   cy),
        hip_mid     = (cx,        cy),
        left_elbow  = (cx - 128,  cy - 110),
        right_elbow = (cx + 128,  cy - 110),
        left_hand   = (cx - 115,  cy + 30),
        right_hand  = (cx + 115,  cy + 30),
        left_knee   = (cx - 55,   cy + 185),
        right_knee  = (cx + 55,   cy + 185),
        left_foot   = (cx - 60,   cy + 370),
        right_foot  = (cx + 60,   cy + 370),
    )

def draw_figure(img, color, alpha):
    p   = _fig_pts()
    c   = (*color, int(255 * alpha))
    lw, lwa, hr = 22, 16, 46
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    hx, hy = p['head']
    d.ellipse([(hx - hr, hy - hr), (hx + hr, hy + hr)], fill=c)
    d.line([p['head'],    p['neck']],                     fill=c, width=lw)
    d.line([p['left_sh'], p['right_sh']],                 fill=c, width=lw)
    d.line([p['neck'],    p['sh_mid']],                   fill=c, width=lw)
    d.line([p['sh_mid'],  p['mid_spine'], p['hip_mid']],  fill=c, width=lw)
    d.line([p['left_sh'],  p['left_elbow'],  p['left_hand']],  fill=c, width=lwa)
    d.line([p['right_sh'], p['right_elbow'], p['right_hand']], fill=c, width=lwa)
    d.line([p['left_hip'], p['right_hip']],               fill=c, width=lw)
    d.line([p['left_hip'],  p['left_knee'],  p['left_foot']],  fill=c, width=lw)
    d.line([p['right_hip'], p['right_knee'], p['right_foot']], fill=c, width=lw)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_back_patch(img, alpha, glow_t=0.0):
    p      = _fig_pts()
    mx, my = p['mid_spine']
    pw, ph = 92, 58
    glow_r = int(18 + 7 * (0.5 + 0.5 * math.sin(glow_t * math.pi * 2.5)))
    glow   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [(mx - pw//2 - 10, my - ph//2 - 10), (mx + pw//2 + 10, my + ph//2 + 10)],
        radius=18, fill=(*GOLD, int(255 * alpha * 0.55))
    )
    glow = glow.filter(ImageFilter.GaussianBlur(glow_r))
    rect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rect).rounded_rectangle(
        [(mx - pw//2, my - ph//2), (mx + pw//2, my + ph//2)],
        radius=12, fill=(*GOLD, int(255 * alpha)),
        outline=(*WHITE, int(255 * alpha)), width=4,
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
# SCENE 1 (0-2s): Split-screen price slam
#   Left panel (navy) expands from center divider outward → fills left half
#   Right stays white; both contents appear after panels settle
# ──────────────────────────────────────────────────────────────────────────────
def scene1(t):
    img = Image.new("RGB", (W, H), WHITE)

    # Panel expansion: 0→W//2 in 0.40s
    p  = eo(t, 0.40)
    hw = int(W // 2 * p)

    if hw > 0:
        pan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(pan).rectangle(
            [(W // 2 - hw, 0), (W // 2, H)], fill=(*NAVY, 255)
        )
        img = Image.alpha_composite(img.convert("RGBA"), pan).convert("RGB")

    # Gold divider (always present, 4px)
    div = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(div).rectangle(
        [(W // 2 - 2, 0), (W // 2 + 2, H)], fill=(*GOLD, 255)
    )
    img = Image.alpha_composite(img.convert("RGBA"), div).convert("RGB")

    # Content fades in and slides from their respective sides
    a   = eo(max(0., t - 0.32), 0.45)
    off = int(W // 2 * max(0., 1 - (t / 0.40)))   # slide offset converges to 0

    if a > 0:
        # Left half: "$150" + "Physio" in white, sliding from left
        img = put_text_half(img, "$150",   H // 2 - 140, fb(100), WHITE,
                            alpha=a, side='left',  dx_extra=-off)
        img = put_text_half(img, "Physio", H // 2 + 20,  fb(35),  WHITE,
                            alpha=a, side='left',  dx_extra=-off)
        # Right half: "$35" + "AuraEase(TM)" sliding from right
        img = put_text_half(img, "$35",        H // 2 - 140, fb(100), GOLD,
                            alpha=a, side='right', dx_extra=off)
        img = put_text_half(img, "AuraEase™", H // 2 + 20, fb(35), NAVY,
                            alpha=a, side='right', dx_extra=off)

    # Full-width white band + tagline at bottom
    a_tag = eo(max(0., t - 0.90), 0.50)
    if a_tag > 0:
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(band).rectangle(
            [(0, H - 230), (W, H - 55)], fill=(*WHITE, int(255 * min(1.0, a_tag * 1.6)))
        )
        img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
        img = put_text(img, "Same result. Different price.",
                       H - 142, fb(42), NAVY, alpha=a_tag)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 2 (2-5s, 3s): Agitation — staggered typewriter + big question
# ──────────────────────────────────────────────────────────────────────────────
_S2 = [
    ("$150 + travel time...",   WHITE, 40, 0.10, 0.65),
    ("+ waiting 3 weeks...",    WHITE, 40, 1.00, 0.65),
    ("+ it only lasts 1 hour.", RED,   40, 1.90, 0.65),
]
_S2_CY = [H // 2 - 310, H // 2 - 170, H // 2 - 30]

def scene2(t):
    img = Image.new("RGB", (W, H), NAVY)

    for (text, color, sz, start, dur), cy in zip(_S2, _S2_CY):
        img = put_typewriter(img, text, cy, fb(sz), color, t,
                             start=start, dur=dur)

    if t >= 2.55:
        a = eo(t - 2.55, 0.55)
        img = put_glow(img, "Is that really worth it?",
                       H // 2 + 230, fb(55), GOLD,
                       glow_col=GOLD, radius=20, glow_a=0.28 * a, txt_a=a)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 3 (5-8s, 3s): Solution — upright silhouette + gold back patch + text
# ──────────────────────────────────────────────────────────────────────────────
_S3 = [
    ("Hot for tension.  ★",       NAVY, 55, 0.20),   # ★
    ("Cold for inflammation.  ❄", NAVY, 55, 0.85),   # ❄
    ("12 hours. Drug-free.",            GOLD, 42, 1.60),
]
_S3_CY = [380, 520, 650]

def scene3(t):
    img = Image.new("RGB", (W, H), WHITE)

    # Figure fades in
    img = draw_figure(img, NAVY, eo(t, 0.50))

    # Gold patch on back
    if t >= 0.30:
        img = draw_back_patch(img, eo(t - 0.30, 0.50), glow_t=t)

    # Text slides up (dy: 70→0)
    for (text, color, sz, delay), cy in zip(_S3, _S3_CY):
        lt = t - delay
        if lt < 0:
            continue
        a  = eo(lt, 0.45)
        dy = int((1 - a) * 70)
        img = put_text(img, text, cy, fb(sz), color, alpha=a, dy=dy)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 4 (8-10s, 2s): CTA
# ──────────────────────────────────────────────────────────────────────────────
def scene4(t):
    img = vgrad(NAVY, DEEP_NAVY)

    a1  = eo(t, 1.2)
    img = put_glow(img, "AuraEase™",
                   H // 2 - 130, fb(75), WHITE,
                   glow_col=GOLD, radius=34, glow_a=0.50 * a1, txt_a=a1)

    if t >= 0.40:
        a2 = eo(t - 0.40, 0.70)
        img = put_text(img, "Smart recovery starts here.",
                       H // 2 + 45, fb(38), GOLD, alpha=a2)

    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 2.4))
    img   = put_text(img, "Link in bio  →",
                     H // 2 + 255, fb(32), WHITE, alpha=pulse)

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
        "auraease_j3_v2.mp4"
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
