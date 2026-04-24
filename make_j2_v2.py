"""
AuraEase J2 v2  |  1080x1920  |  15s  |  30fps  |  no audio
Silhouette posture: hunched → straightening → upright → CTA
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
PAIN_RED  = (210,  55,  55)
DEEP_NAVY = (10,  18,  40)
FIG_LIGHT = (160, 200, 230)   # silhouette colour on navy bg

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

def put_typewriter(img, full_text, cy, fnt, color, t, start=0.2, duration=2.5):
    elapsed  = max(0., t - start)
    progress = min(1., elapsed / duration)
    n_chars  = int(len(full_text) * progress)
    visible  = full_text[:n_chars]
    if not visible:
        return img
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

# ── Figure skeleton ───────────────────────────────────────────────────────────
FIG_CX = W // 2
FIG_CY = 1050   # hip-level anchor

def get_pose(hunch):
    """hunch: 0.0 = fully hunched, 1.0 = fully upright."""
    cx, cy = FIG_CX, FIG_CY
    h = hunch

    fwd   = int((1 - h) * 62)   # horizontal lean
    droop = int((1 - h) * 32)   # head droops
    sh_d  = int((1 - h) * 18)   # shoulders sink

    head    = (cx + fwd,           cy - 330 + droop)
    neck    = (cx + int(fwd*.65),  cy - 282 + int(droop*.55))
    sh_off  = int(fwd * .4)
    sh_cy   = cy - 245 + sh_d
    left_sh  = (cx - 88 + sh_off, sh_cy)
    right_sh = (cx + 88 + sh_off, sh_cy)
    sh_mid   = ((left_sh[0]+right_sh[0])//2, sh_cy)
    mid_spine = (cx + int(fwd*.2), cy - 120)
    left_hip  = (cx - 55, cy)
    right_hip = (cx + 55, cy)
    hip_mid   = (cx, cy)

    af = int((1 - h) * 38)
    left_elbow  = (cx - 128 + sh_off + af, cy - 110 + sh_d)
    right_elbow = (cx + 128 + sh_off + af, cy - 110 + sh_d)
    left_hand   = (cx - 115 + sh_off + af, cy + 30  + sh_d)
    right_hand  = (cx + 115 + sh_off + af, cy + 30  + sh_d)

    left_knee  = (cx - 55, cy + 185)
    right_knee = (cx + 55, cy + 185)
    left_foot  = (cx - 60, cy + 370)
    right_foot = (cx + 60, cy + 370)

    return dict(
        head=head, neck=neck,
        left_sh=left_sh, right_sh=right_sh, sh_mid=sh_mid,
        mid_spine=mid_spine,
        left_hip=left_hip, right_hip=right_hip, hip_mid=hip_mid,
        left_elbow=left_elbow, right_elbow=right_elbow,
        left_hand=left_hand, right_hand=right_hand,
        left_knee=left_knee, right_knee=right_knee,
        left_foot=left_foot, right_foot=right_foot,
    )

def draw_figure(img, hunch, color, alpha):
    p   = get_pose(hunch)
    c   = (*color, int(255 * alpha))
    lw  = 22
    lwa = 16   # arms thinner
    hr  = 46

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)

    hx, hy = p['head']
    d.ellipse([(hx-hr, hy-hr), (hx+hr, hy+hr)], fill=c)
    d.line([p['head'],    p['neck']],                    fill=c, width=lw)
    d.line([p['left_sh'], p['right_sh']],                fill=c, width=lw)
    d.line([p['neck'],    p['sh_mid']],                  fill=c, width=lw)
    d.line([p['sh_mid'],  p['mid_spine'], p['hip_mid']], fill=c, width=lw)
    d.line([p['left_sh'], p['left_elbow'],  p['left_hand']],  fill=c, width=lwa)
    d.line([p['right_sh'],p['right_elbow'], p['right_hand']], fill=c, width=lwa)
    d.line([p['left_hip'], p['right_hip']],              fill=c, width=lw)
    d.line([p['left_hip'],  p['left_knee'],  p['left_foot']],  fill=c, width=lw)
    d.line([p['right_hip'], p['right_knee'], p['right_foot']], fill=c, width=lw)

    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_neck_glow(img, hunch, pulse, alpha):
    p      = get_pose(hunch)
    nx, ny = p['neck']
    r      = int(58 + 18 * pulse)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    d.ellipse([(nx-r-28, ny-r-28), (nx+r+28, ny+r+28)],
              fill=(*PAIN_RED, int(255 * alpha * 0.28)))
    d.ellipse([(nx-r, ny-r), (nx+r, ny+r)],
              fill=(*PAIN_RED, int(255 * alpha * 0.65)))
    layer = layer.filter(ImageFilter.GaussianBlur(20))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_patch(img, hunch, alpha):
    p      = get_pose(hunch)
    nx, ny = p['neck']
    pw, ph = 96, 56

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    d.rounded_rectangle(
        [(nx - pw//2, ny - ph//2), (nx + pw//2, ny + ph//2)],
        radius=12,
        fill=(*GOLD,  int(255 * alpha)),
        outline=(*WHITE, int(255 * alpha * 0.9)),
        width=4,
    )
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

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
# SCENE 1 (0-3s): Hunched silhouette + red neck glow
# ──────────────────────────────────────────────────────────────────────────────
def scene1(t):
    img   = Image.new("RGB", (W, H), WHITE)
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2.2)
    a_in  = min(1.0, t / 0.45)

    img = draw_neck_glow(img, 0.0, pulse, a_in)
    img = draw_figure(img, 0.0, NAVY, a_in)

    a_txt = eo(max(0., t - 0.4), 0.6)
    img = put_text(img, "Your 9-5 shouldn't hurt this much.",
                   390, fb(48), NAVY, alpha=a_txt)
    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 2 (3-7s, 4s): Silhouette straightens, patch appears, pain fades
# ──────────────────────────────────────────────────────────────────────────────
def scene2(t):
    img   = Image.new("RGB", (W, H), NAVY)
    hunch = eo(t, 3.5)
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2.2)

    a_red = max(0., 1.0 - t / 1.5)
    if a_red > 0:
        img = draw_neck_glow(img, hunch, pulse, a_red * 0.8)

    img = draw_figure(img, hunch, FIG_LIGHT, 1.0)

    if t >= 0.5:
        a_patch = eo(t - 0.5, 0.6)
        img = draw_patch(img, hunch, a_patch)

    a_txt = eo(max(0., t - 0.3), 0.6)
    img = put_text(img, "The $35 desk worker cheat code.",
                   390, fb(50), WHITE, alpha=a_txt)
    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 3 (7-11s, 4s): Upright gold figure + typewriter + subtext
# ──────────────────────────────────────────────────────────────────────────────
_S3_MAIN = "Dual-action therapy while you type."
_S3_SUB  = "Hot for knots  ★   Cold for aches  ❄"

def scene3(t):
    img = Image.new("RGB", (W, H), WHITE)

    img = draw_figure(img, 1.0, GOLD, min(1.0, t / 0.4))

    img = put_typewriter(img, _S3_MAIN, 390, fb(45), NAVY,
                         t, start=0.2, duration=2.0)

    if t >= 2.6:
        a_sub = eo(t - 2.6, 0.5)
        img = put_text(img, _S3_SUB, 1620, fb(38), GOLD, alpha=a_sub)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 4 (11-15s, 4s): CTA — ghost silhouette + glow text + pulse
# ──────────────────────────────────────────────────────────────────────────────
def scene4(t):
    img = vgrad(NAVY, DEEP_NAVY)

    # Faint ghost of hunched figure — reference to scene 1 "loop"
    img = draw_figure(img, 0.0, WHITE, 0.07)

    a1  = eo(t, 1.5)
    img = put_glow(img, "AuraEase™",
                   H // 2 - 125, fb(80), WHITE,
                   glow_col=GOLD, radius=34, glow_a=0.50 * a1, txt_a=a1)

    if t >= 0.5:
        a2  = eo(t - 0.5, 0.8)
        img = put_text(img, "Stop the hunch.",
                       H // 2 + 55, fb(45), GOLD, alpha=a2)

    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 2.2))
    img   = put_text(img, "Link in bio  →",
                     H // 2 + 280, fb(35), WHITE, alpha=pulse)

    return np.array(img)

# ── BUILD ─────────────────────────────────────────────────────────────────────
def build():
    FD    = 0.3
    clips = [
        VideoClip(wf(scene1, 3.0, FD), duration=3.0),
        VideoClip(wf(scene2, 4.0, FD), duration=4.0),
        VideoClip(wf(scene3, 4.0, FD), duration=4.0),
        VideoClip(wf(scene4, 4.0, FD), duration=4.0),
    ]
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "auraease_j2_v2.mp4"
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
