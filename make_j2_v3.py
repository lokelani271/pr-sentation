"""
AuraEase J2 v3  |  1080x1920  |  14s  |  30fps  |  no audio
Countdown → Split particles → Ouch→Ahhh wave → CTA
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
DEEP_NAVY = (10,  18,  40)
RED_PAIN  = (220,  60,  60)
ICE_BLUE  = (168, 216, 234)
WARM_ORA  = (255, 140,  66)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@lru_cache(maxsize=30)
def fb(sz):
    return ImageFont.truetype(_BOLD, sz)

_DD = ImageDraw.Draw(Image.new("RGB", (1, 1)))

# ── Core helpers ──────────────────────────────────────────────────────────────
def eo(t, d):
    p = max(0., min(1., t / max(d, 1e-9)))
    return 1 - (1 - p) ** 3

def lerp_col(c1, c2, t):
    t = max(0., min(1., t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

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

def put_text_scaled(img, text, cy, fnt, color, alpha=1.0, scale=1.0):
    """Draw centered text with optional uniform scale (for heartbeat pulse)."""
    lines = _wrap(text, fnt)
    lh    = fnt.size + 14
    y0    = cy - len(lines) * lh // 2
    tmp   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(tmp)
    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=fnt)
        tw   = bbox[2] - bbox[0]
        x    = (W - tw) // 2
        d.text((x, y0 + i * lh), ln, font=fnt, fill=(*color[:3], int(255 * alpha)))
    if abs(scale - 1.0) > 0.002:
        nw, nh  = int(W * scale), int(H * scale)
        scaled  = tmp.resize((nw, nh), Image.LANCZOS)
        result  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        px, py  = (W - nw) // 2, (H - nh) // 2
        result.paste(scaled, (px, py), mask=scaled)
        tmp = result
    return Image.alpha_composite(img.convert("RGBA"), tmp).convert("RGB")

def put_glow(img, text, cy, fnt, txt_col,
             glow_col=GOLD, radius=28, glow_a=0.55, txt_a=1.0):
    bbox = _DD.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y   = (W - tw) // 2, cy - th // 2
    canvas = img.convert("RGBA")
    g      = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).text((x, y), text, font=fnt,
                           fill=(*glow_col, int(255 * glow_a)))
    g = g.filter(ImageFilter.GaussianBlur(radius))
    canvas = Image.alpha_composite(canvas, g)
    t_l    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(t_l).text((x, y), text, font=fnt,
                             fill=(*txt_col, int(255 * txt_a)))
    return Image.alpha_composite(canvas, t_l).convert("RGB")

# ── Heartbeat scale ───────────────────────────────────────────────────────────
def heartbeat(t, rate=1.4):
    """Two quick peaks per cycle, then silence — like a real heartbeat."""
    phase = (t * rate) % 1.0
    if phase < 0.12:
        return 1.0 + 0.20 * math.sin(phase / 0.12 * math.pi)
    elif phase < 0.24:
        return 1.0 + 0.11 * math.sin((phase - 0.12) / 0.12 * math.pi)
    return 1.0

# ── Particles (precomputed with fixed seeds for determinism) ──────────────────
N_P    = 22
RECT_CY = H // 2 + 80
RW, RH  = 520, 280

_rL = np.random.RandomState(42)
_lx0 = _rL.uniform(40,   W//2 - 60, N_P).astype(float)
_ly0 = _rL.uniform(H//4, 3*H//4,    N_P).astype(float)
_lr  = _rL.randint(9, 20, N_P)

_rR = np.random.RandomState(77)
_rx0 = _rR.uniform(W//2 + 60, W - 40, N_P).astype(float)
_ry0 = _rR.uniform(H//4, 3*H//4,      N_P).astype(float)
_rr  = _rR.randint(9, 20, N_P)

_rLF = np.random.RandomState(11)
_lxf = _rLF.uniform(W//2 - RW//2 + 10, W//2 - 20, N_P).astype(float)
_lyf = _rLF.uniform(RECT_CY - RH//2 + 10, RECT_CY + RH//2 - 10, N_P).astype(float)

_rRF = np.random.RandomState(33)
_rxf = _rRF.uniform(W//2 + 20, W//2 + RW//2 - 10, N_P).astype(float)
_ryf = _rRF.uniform(RECT_CY - RH//2 + 10, RECT_CY + RH//2 - 10, N_P).astype(float)

def draw_particles(img, t):
    conv    = eo(max(0., t - 1.2), 2.8)        # converge 1.2→4s
    p_alpha = max(0., 1.0 - max(0., (t - 4.2) / 1.2))  # fade from 4.2s

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)

    for i in range(N_P):
        osc_l = math.sin(t * 2.8 + i * 0.9)  * 18 * (1 - conv)
        px = _lx0[i] + (_lxf[i] - _lx0[i]) * conv
        py = _ly0[i] + (_lyf[i] - _ly0[i]) * conv + osc_l
        r  = _lr[i]
        c  = (*ICE_BLUE, int(255 * p_alpha))
        d.ellipse([(px-r, py-r), (px+r, py+r)], fill=c)
        d.line([(px-r, py), (px+r, py)], fill=c, width=3)
        d.line([(px, py-r), (px, py+r)], fill=c, width=3)

        osc_r = math.sin(t * 2.8 + i * 1.2 + 1.6) * 18 * (1 - conv)
        qx = _rx0[i] + (_rxf[i] - _rx0[i]) * conv
        qy = _ry0[i] + (_ryf[i] - _ry0[i]) * conv + osc_r
        s  = _rr[i]
        c2 = (*WARM_ORA, int(255 * p_alpha))
        d.ellipse([(qx-s, qy-s), (qx+s, qy+s)], fill=c2)
        d.line([(qx-s, qy), (qx+s, qy)], fill=c2, width=3)
        d.line([(qx, qy-s), (qx, qy+s)], fill=c2, width=3)
        sd = int(s * 0.7)
        d.line([(qx-sd, qy-sd), (qx+sd, qy+sd)], fill=c2, width=2)
        d.line([(qx+sd, qy-sd), (qx-sd, qy+sd)], fill=c2, width=2)

    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_gold_rect(img, t):
    a = eo(max(0., t - 3.5), 1.2)
    if a <= 0:
        return img
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    cx, cy = W // 2, RECT_CY
    hw, hh = RW // 2, RH // 2
    d.rounded_rectangle(
        [(cx - hw, cy - hh), (cx + hw, cy + hh)],
        radius=28,
        fill=(*GOLD,  int(255 * a * 0.88)),
        outline=(*WHITE, int(255 * a)),
        width=6,
    )
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    # Labels centered in each half
    if a > 0.55:
        al = (a - 0.55) * 2.22
        img = put_text(img, "HOT",  cy, fb(44), WARM_ORA, alpha=al, dx=-130)
        img = put_text(img, "COLD", cy, fb(44), ICE_BLUE, alpha=al, dx=+130)
    return img

# ── Wave drawing ──────────────────────────────────────────────────────────────
def draw_wave(img, t, cy, amp, freq, spd, jagged, color, alpha, thick=6):
    pts = []
    for x in range(0, W + 4, 4):
        xf = x / W
        ph = spd * t
        base = amp * math.sin(2 * math.pi * freq * xf + ph)
        if jagged > 0:
            rough = (0.55 * amp * math.sin(2 * math.pi * freq * 5  * xf + ph * 3.1) +
                     0.30 * amp * math.sin(2 * math.pi * freq * 11 * xf + ph * 5.3))
            y = int(cy + base * (1 - jagged) + (base + rough) * jagged)
        else:
            y = int(cy + base)
        pts.append((x, y))
    if len(pts) < 2:
        return img
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).line(pts, fill=(*color, int(255 * alpha)), width=thick)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

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
# SCENE 1 (0-2s): Countdown 30→0, heartbeat pulse, red→gold color shift
# ──────────────────────────────────────────────────────────────────────────────
def scene1(t):
    img  = Image.new("RGB", (W, H), NAVY)
    num  = max(0, int(30 * (1 - t / 2.0)))
    prog = 1.0 - num / 30.0
    col  = lerp_col(RED_PAIN, GOLD, prog)
    sc   = heartbeat(t, rate=1.4)

    img = put_text_scaled(img, str(num), H // 2 - 60, fb(260), col,
                          alpha=1.0, scale=sc)

    a_txt = eo(max(0., t - 0.15), 0.5)
    img = put_text(img, "30 seconds to relief.",
                   H // 2 + 290, fb(45), WHITE, alpha=a_txt)
    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 2 (2-8s, 6s): Split bg, converging particles, gold rectangle forms
# ──────────────────────────────────────────────────────────────────────────────
def scene2(t):
    img = Image.new("RGB", (W, H), WHITE)
    img.paste(Image.new("RGB", (W // 2, H), ICE_BLUE),  (0,      0))
    img.paste(Image.new("RGB", (W // 2, H), WARM_ORA),  (W // 2, 0))

    # Divider fades as rect takes over
    d_a = max(0., 1.0 - t / 1.8)
    if d_a > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).line([(W//2, 0), (W//2, H)],
                                   fill=(*WHITE, int(255 * d_a * 0.45)), width=3)
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

    img = draw_particles(img, t)
    img = draw_gold_rect(img, t)

    a_txt = eo(max(0., t - 0.25), 0.7)
    img = put_text(img, "Feel the thermal dual-action start.",
                   350, fb(42), WHITE, alpha=a_txt)
    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 3 (8-11s, 3s): White bg — Ouch→Ahhh + wave transitions
# ──────────────────────────────────────────────────────────────────────────────
def scene3(t):
    img = Image.new("RGB", (W, H), WHITE)

    a1 = eo(t, 0.6)
    img = put_text(img, "From Ouch...", H // 2 - 130, fb(65), RED_PAIN, alpha=a1)

    if t >= 0.7:
        a2 = eo(t - 0.7, 0.6)
        img = put_text(img, "...to Ahhh.", H // 2 + 30, fb(65), GOLD, alpha=a2)

    # Wave: starts jagged (pain), smooths over 2s (relief)
    jagged = max(0., 1.0 - t / 2.0)
    wcy    = H // 2 + 340
    img = draw_wave(img, t,          wcy,      58, 2, 3.5, jagged,     NAVY, 0.75, thick=8)
    img = draw_wave(img, max(0,t-.35), wcy+50, 36, 2, 3.5, jagged*.55, NAVY, 0.35, thick=4)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCENE 4 (11-14s, 3s): CTA — ghost "30" + glow brand + pulse link
# ──────────────────────────────────────────────────────────────────────────────
def scene4(t):
    img = vgrad(NAVY, DEEP_NAVY)

    # Ghost "30" — loop signal, fades in softly
    a30 = eo(t, 1.0) * 0.18
    img = put_text(img, "30", H // 2 - 380, fb(200), GOLD, alpha=a30)

    a1  = eo(t, 1.5)
    img = put_glow(img, "AuraEase™",
                   H // 2 - 120, fb(80), WHITE,
                   glow_col=GOLD, radius=34, glow_a=0.50 * a1, txt_a=a1)

    if t >= 0.5:
        a2 = eo(t - 0.5, 0.8)
        img = put_text(img, "Start your 30 seconds now.",
                       H // 2 + 55, fb(40), GOLD, alpha=a2)

    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * math.pi * 2.2))
    img   = put_text(img, "Link in bio  →",
                     H // 2 + 270, fb(35), WHITE, alpha=pulse)

    return np.array(img)

# ── BUILD ─────────────────────────────────────────────────────────────────────
def build():
    FD    = 0.3
    clips = [
        VideoClip(wf(scene1, 2.0, FD), duration=2.0),
        VideoClip(wf(scene2, 6.0, FD), duration=6.0),
        VideoClip(wf(scene3, 3.0, FD), duration=3.0),
        VideoClip(wf(scene4, 3.0, FD), duration=3.0),
    ]
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "auraease_j2_v3.mp4"
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
