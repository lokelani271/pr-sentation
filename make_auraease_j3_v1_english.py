"""
AuraEase J3 v1 English  |  1080x1920  |  12s  |  30fps  |  no audio
Scene 1 Hook (0-2s) → Scene 2 Solution (2-5.5s) → Scene 3 Proof (5.5-9s) → Scene 4 CTA (9-12s)
All text in English.
"""

import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from functools import lru_cache

try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy import VideoClip

W, H = 1080, 1920
FPS  = 30

NAVY     = (27,  42,  74)
GOLD     = (201, 169, 110)
WHITE    = (255, 255, 255)
ICE_BLUE = (100, 180, 255)
FIRE_RED = (255, 80,  60)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@lru_cache(maxsize=20)
def fb(sz):
    return ImageFont.truetype(_BOLD, sz)

_DD = ImageDraw.Draw(Image.new("RGB", (1, 1)))

# ── Text helpers ───────────────────────────────────────────────────────────────

def _wrap(text, fnt, max_w=880):
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
    lines  = _wrap(text, fnt)
    lh     = fnt.size + 14
    y0     = cy + dy - len(lines) * lh // 2
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

def put_typewriter(img, text, cy, fnt, color, t, start, dur):
    elapsed  = max(0., t - start)
    progress = min(1., elapsed / max(dur, 1e-9))
    n        = int(len(text) * progress)
    visible  = text[:n]
    if not visible:
        return img
    cursor = "|" if int(t * 12) % 2 == 0 and n < len(text) else ""
    return put_text(img, visible + cursor, cy, fnt, color)

def eo(t, d):
    p = max(0., min(1., t / max(d, 1e-9)))
    return 1 - (1 - p) ** 3

def crossfade(a_arr, b_arr, alpha):
    return (a_arr * (1 - alpha) + b_arr * alpha).astype(np.uint8)

# ── SCENE 1 — HOOK (0-2s) ─────────────────────────────────────────────────────
# Thermal particle cloud around a pulsing fire pain zone
# Text: "POV: 3PM at your desk." / "Your back is literally on fire."
# ──────────────────────────────────────────────────────────────────────────────

def scene1_hook(t, width=1080, height=1920, center_x=540, center_y=800):
    img  = Image.new('RGB', (width, height), color=(20, 30, 55))

    # Pain zone — red pulsing glow
    glow_r = 140 + int(30 * math.sin(t * 4))
    glow_a = 0.35 + 0.15 * math.sin(t * 3)
    glow   = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([
        center_x - glow_r * 2, center_y - glow_r * 2,
        center_x + glow_r * 2, center_y + glow_r * 2,
    ], fill=(*FIRE_RED, int(255 * glow_a)))
    glow = glow.filter(ImageFilter.GaussianBlur(45))
    img  = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    draw = ImageDraw.Draw(img)

    # 300-particle orbital cloud (ice blue + gold + white)
    np.random.seed(42)
    for i in range(300):
        angle       = (i / 300) * 2 * math.pi + t * 2
        base_radius = 80 + (i % 5) * 40
        radius      = base_radius + math.sin(t * 3 + i * 0.5) * 20
        px = center_x + math.cos(angle) * radius
        py = center_y + math.sin(angle) * radius
        if i % 3 == 0:
            color = (
                int(ICE_BLUE[0] * (0.6 + 0.4 * math.sin(t + i))),
                int(ICE_BLUE[1] * (0.6 + 0.4 * math.sin(t + i))),
                ICE_BLUE[2],
            )
        elif i % 3 == 1:
            color = (GOLD[0], int(GOLD[1] * (0.7 + 0.3 * math.cos(t + i))),
                     int(GOLD[2] * 0.5))
        else:
            a     = 0.4 + 0.6 * abs(math.sin(t * 2 + i * 0.3))
            color = tuple(int(c * a) for c in WHITE)
        size = 2 + (i % 4)
        draw.ellipse([px - size, py - size, px + size, py + size], fill=color)

    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # English text
    img = put_typewriter(img, "POV: 3PM at your desk.", H // 2 + 260,
                         fb(68), WHITE, t, start=0.05, dur=0.55)
    if t >= 0.85:
        a2  = eo(t - 0.85, 0.25)
        img = put_text(img, "Your back is literally on fire.", H // 2 + 430,
                       fb(54), FIRE_RED, alpha=a2, dy=int((1 - a2) * 40))

    return np.array(img)


# ── SCENE 2 — SOLUTION (2-5.5s) ───────────────────────────────────────────────
# X-Ray shockwave emanates from gold patch, skeleton illuminates
# Text: "AuraEase™" / "Instant hot & cold relief."
# ──────────────────────────────────────────────────────────────────────────────

def scene2_solution(t, width=1080, height=1920):
    img  = Image.new('RGB', (width, height), color=(15, 25, 50))
    cx, cy = 540, 960

    # Ambient gold glow layers
    for radius, opacity in [(350, 0.08), (250, 0.12), (150, 0.18)]:
        pulse = opacity * (0.85 + 0.15 * math.sin(t * 1.8))
        glow  = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(*GOLD, int(255 * pulse))
        )
        glow = glow.filter(ImageFilter.GaussianBlur(55))
        img  = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Expanding ICE_BLUE shockwave rings
    wave_progress = (t % 2.0) / 2.0
    for ring in range(4):
        rp     = (wave_progress + ring * 0.25) % 1.0
        ring_r = int(rp * 420)
        ring_o = max(0., 1.0 - rp - ring * 0.15)
        ring_c = (int(ICE_BLUE[0] * ring_o),
                  int(ICE_BLUE[1] * ring_o),
                  int(ICE_BLUE[2] * ring_o))
        if ring_r > 0 and any(c > 0 for c in ring_c):
            draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
                         outline=ring_c, width=3)

    # Skeleton illuminated by gold glow
    gi = 0.5 + 0.5 * math.sin(t * math.pi)
    sk = tuple(int(c * gi) for c in GOLD)
    draw.ellipse([490, 550, 590, 650], outline=sk, width=4)
    draw.line([(540, 650), (540, 950)],  fill=sk, width=4)
    draw.line([(380, 720), (700, 720)],  fill=sk, width=4)
    draw.line([(380, 720), (320, 880)],  fill=sk, width=3)
    draw.line([(700, 720), (760, 880)],  fill=sk, width=3)
    draw.line([(420, 950), (660, 950)],  fill=sk, width=4)
    draw.line([(420, 950), (390, 1150)], fill=sk, width=3)
    draw.line([(660, 950), (690, 1150)], fill=sk, width=3)

    # Gold patch on lower back — pulsing
    pp         = 0.7 + 0.3 * math.sin(t * 4)
    pc         = tuple(int(c * pp) for c in GOLD)
    patch_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(patch_glow).rounded_rectangle(
        [440, 865, 640, 945], radius=14,
        fill=(*GOLD, int(255 * pp * 0.5))
    )
    patch_glow = patch_glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img.convert("RGBA"), patch_glow).convert("RGB")
    ImageDraw.Draw(img).rounded_rectangle(
        [440, 865, 640, 945], radius=14,
        fill=pc, outline=(*WHITE, 220), width=3
    )

    # English text
    brand_a = eo(t, 1.2)
    img = put_text(img, "AuraEase™", H // 2 - 260, fb(92), WHITE, alpha=brand_a)
    if t >= 0.7:
        a2  = eo(t - 0.7, 0.8)
        img = put_text(img, "Instant hot & cold relief.", H // 2 - 100,
                       fb(46), GOLD, alpha=a2)

    return np.array(img)


# ── SCENE 3 — PROOF (5.5-9s) ──────────────────────────────────────────────────
# Dark navy BG, 3 checkmarks slam in from left
# Text: checkmarks for Works / Invisible / Price
# ──────────────────────────────────────────────────────────────────────────────

_PROOF_ITEMS = [
    ("Works in 30 seconds",     0.0),
    ("Invisible under clothes", 0.55),
    ("$35 vs $150 physio",      1.1),
]

def scene3_proof(t, width=1080, height=1920):
    img = Image.new("RGB", (width, height), NAVY)

    # Gradient overlay navy → deep blue bottom
    grad = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(0, height, 3):
        p   = y / height
        mix = p * 0.22
        r   = int(NAVY[0] + (ICE_BLUE[0] - NAVY[0]) * mix * 0.3)
        g   = int(NAVY[1] + (ICE_BLUE[1] - NAVY[1]) * mix * 0.3)
        b   = int(NAVY[2] + (ICE_BLUE[2] - NAVY[2]) * mix * 0.4)
        gd.rectangle([(0, y), (width, y + 3)], fill=(r, g, b, 255))
    img = Image.alpha_composite(img.convert("RGBA"), grad).convert("RGB")

    # Subtle radial glow
    cg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(cg).ellipse([240, 580, 840, 1180], fill=(*GOLD, 14))
    cg  = cg.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img.convert("RGBA"), cg).convert("RGB")

    # Section header
    hdr_a = eo(t, 0.5)
    img   = put_text(img, "Why it works:", H // 2 - 430, fb(56), GOLD,
                     alpha=hdr_a, dy=int((1 - hdr_a) * 40))

    # Gold divider
    if t >= 0.3:
        div_a  = eo(t - 0.3, 0.4)
        line_w = int(560 * div_a)
        dl     = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        x0     = (width - line_w) // 2
        ImageDraw.Draw(dl).rectangle(
            [x0, H // 2 - 355, x0 + line_w, H // 2 - 353],
            fill=(*GOLD, int(255 * div_a * 0.55))
        )
        img = Image.alpha_composite(img.convert("RGBA"), dl).convert("RGB")

    # Checkmark rows
    ck_x = 155
    for (text, delay), row in zip(_PROOF_ITEMS, range(3)):
        lt = t - delay
        if lt < 0:
            continue
        a   = eo(lt, 0.32)
        cy_ = H // 2 - 170 + row * 160
        dx  = int((1 - a) * -140)

        badge = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        bd    = ImageDraw.Draw(badge)
        bd.ellipse([ck_x + dx - 38, cy_ - 38, ck_x + dx + 38, cy_ + 38],
                   fill=(*GOLD, int(255 * a)))
        bd.text((ck_x + dx - 19, cy_ - 28), "✓",
                font=fb(46), fill=(*NAVY, int(255 * a)))
        img = Image.alpha_composite(img.convert("RGBA"), badge).convert("RGB")
        img = put_text(img, text, cy_, fb(50), WHITE, alpha=a, dx=58 + dx)

    # Fade-in at scene start
    if t < 0.20:
        black = np.zeros((height, width, 3), dtype=np.uint8)
        return crossfade(black, np.array(img), t / 0.20)

    return np.array(img)


# ── SCENE 4 — CTA (9-12s) ─────────────────────────────────────────────────────
# Brand, tagline, pulsing CTA button
# Text: "AuraEase™" / "Stop the fire. Start the relief." / "Link in bio →"
# ──────────────────────────────────────────────────────────────────────────────

def scene4_cta(t, width=1080, height=1920):
    img = Image.new("RGB", (width, height), NAVY)

    # Gradient: navy → warm gold tint at bottom
    grad = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(0, height, 3):
        p   = y / height
        mix = p * 0.20
        r   = int(NAVY[0] + (GOLD[0] - NAVY[0]) * mix)
        g   = int(NAVY[1] + (GOLD[1] - NAVY[1]) * mix)
        b   = int(NAVY[2] + (GOLD[2] - NAVY[2]) * mix * 0.3)
        gd.rectangle([(0, y), (width, y + 3)], fill=(r, g, b, 255))
    img = Image.alpha_composite(img.convert("RGBA"), grad).convert("RGB")

    # Central radial glow
    cg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(cg).ellipse([290, 550, 790, 1050], fill=(*GOLD, 20))
    cg  = cg.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img.convert("RGBA"), cg).convert("RGB")

    # Brand
    brand_a = eo(t, 0.55)
    img = put_text(img, "AuraEase™", H // 2 - 380, fb(96), WHITE,
                   alpha=brand_a, dy=int((1 - brand_a) * 60))

    # Tagline
    if t >= 0.3:
        tag_a = eo(t - 0.3, 0.50)
        img   = put_text(img, "Stop the fire.", H // 2 - 205, fb(58),
                         GOLD, alpha=tag_a)
    if t >= 0.65:
        tag2_a = eo(t - 0.65, 0.50)
        img    = put_text(img, "Start the relief.", H // 2 - 95, fb(58),
                          GOLD, alpha=tag2_a)

    # Gold divider
    if t >= 0.9:
        div_a  = eo(t - 0.9, 0.35)
        line_w = int(580 * div_a)
        dl     = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        x0     = (width - line_w) // 2
        ImageDraw.Draw(dl).rectangle(
            [x0, H // 2 + 10, x0 + line_w, H // 2 + 12],
            fill=(*GOLD, int(255 * div_a * 0.5))
        )
        img = Image.alpha_composite(img.convert("RGBA"), dl).convert("RGB")

    # CTA button
    if t >= 1.2:
        btn_a  = eo(t - 1.2, 0.55)
        pulse  = 1.0 + 0.028 * math.sin(t * math.pi * 2.8)
        btn_w  = int(700 * pulse)
        btn_h  = 122
        btn_cx = W // 2
        btn_cy = H // 2 + 240
        bx0    = btn_cx - btn_w // 2
        bx1    = btn_cx + btn_w // 2
        by0    = btn_cy - btn_h // 2
        by1    = btn_cy + btn_h // 2

        btn_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(btn_glow).rounded_rectangle(
            [bx0 - 14, by0 - 14, bx1 + 14, by1 + 14],
            radius=68, fill=(*GOLD, int(255 * btn_a * 0.38))
        )
        btn_glow = btn_glow.filter(ImageFilter.GaussianBlur(22))
        img = Image.alpha_composite(img.convert("RGBA"), btn_glow).convert("RGB")

        ImageDraw.Draw(img).rounded_rectangle(
            [bx0, by0, bx1, by1], radius=61,
            fill=GOLD, outline=(*WHITE, int(255 * btn_a * 0.9)), width=3
        )
        img = put_text(img, "Link in bio  →", btn_cy, fb(48),
                       NAVY, alpha=btn_a)

    # Fade-in at scene start
    if t < 0.20:
        black = np.zeros((height, width, 3), dtype=np.uint8)
        return crossfade(black, np.array(img), t / 0.20)

    return np.array(img)


# ── MASTER FRAME ───────────────────────────────────────────────────────────────
# Timing: S1 0-2s | S2 2-5.5s | S3 5.5-9s | S4 9-12s
# ──────────────────────────────────────────────────────────────────────────────

S1, S2, S3, S4 = 2.0, 5.5, 9.0, 12.0
BD = 0.18   # crossfade blend duration (seconds)

def make_frame(t):
    # Scene 1 — Hook
    if t < S1 - BD:
        return scene1_hook(t)
    elif t < S1:
        a = (t - (S1 - BD)) / BD
        return crossfade(scene1_hook(t), scene2_solution(0.0), a)

    # Scene 2 — Solution
    elif t < S2 - BD:
        return scene2_solution(t - S1)
    elif t < S2:
        a = (t - (S2 - BD)) / BD
        return crossfade(scene2_solution(t - S1), scene3_proof(0.0), a)

    # Scene 3 — Proof
    elif t < S3 - BD:
        return scene3_proof(t - S2)
    elif t < S3:
        a = (t - (S3 - BD)) / BD
        return crossfade(scene3_proof(t - S2), scene4_cta(0.0), a)

    # Scene 4 — CTA
    else:
        return scene4_cta(t - S3)


# ── BUILD ──────────────────────────────────────────────────────────────────────

def build():
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "auraease_j3_v1_english.mp4"
    )
    VideoClip(make_frame, duration=12).write_videofile(
        out,
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger="bar",
    )
    print(f"\n✔  Saved → {out}")


if __name__ == "__main__":
    build()
