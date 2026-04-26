"""
AuraEase Premium v1  |  1080x1920  |  12s  |  30fps  |  no audio
Hook (0-2s) → Slow Reveal (2-7s) → Fast CTA (7-12s)
"""

import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from functools import lru_cache

# moviepy.editor removed in v2 — use direct import
try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy import VideoClip

W, H = 1080, 1920
FPS  = 30

# ── Palette ────────────────────────────────────────────────────────────────────
NAVY     = (27,  42,  74)
GOLD     = (201, 169, 110)
WHITE    = (255, 255, 255)
ICE_BLUE = (100, 180, 255)
FIRE_RED = (255, 80,  60)
BG_WHITE = (245, 245, 250)

# ── Fonts ──────────────────────────────────────────────────────────────────────
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
    """Ease-out cubic."""
    p = max(0., min(1., t / max(d, 1e-9)))
    return 1 - (1 - p) ** 3

def crossfade(a_arr, b_arr, alpha):
    return (a_arr * (1 - alpha) + b_arr * alpha).astype(np.uint8)

# ── TECHNIQUE 1 — THERMAL PARTICLE CLOUD ──────────────────────────────────────
# Hundreds of blue/gold particles orbit a pulsing pain zone
# ──────────────────────────────────────────────────────────────────────────────
def create_thermal_particle_frame(t, width=1080, height=1920,
                                  center_x=540, center_y=800):
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

    # Particle cloud
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
            color = (
                GOLD[0],
                int(GOLD[1] * (0.7 + 0.3 * math.cos(t + i))),
                int(GOLD[2] * 0.5),
            )
        else:
            a     = 0.4 + 0.6 * abs(math.sin(t * 2 + i * 0.3))
            color = tuple(int(c * a) for c in WHITE)

        size = 2 + (i % 4)
        draw.ellipse([px - size, py - size, px + size, py + size], fill=color)

    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # Text: typewriter hook
    img = put_typewriter(img, "POV : 15h30.", H // 2 + 280,
                         fb(72), WHITE, t, start=0.05, dur=0.50)
    if t >= 0.8:
        a2  = eo(t - 0.8, 0.25)
        img = put_text(img, "Ton dos te brule.", H // 2 + 450,
                       fb(58), FIRE_RED, alpha=a2, dy=int((1 - a2) * 40))
    if t >= 1.4:
        a3  = eo(t - 1.4, 0.35)
        img = put_text(img, "Encore.", H // 2 + 590,
                       fb(50), (200, 200, 220), alpha=a3)

    return np.array(img)


# ── TECHNIQUE 2 — X-RAY GLOW SHOCKWAVE ────────────────────────────────────────
# Expanding rings emanate from patch contact point,
# illuminating the stick-figure skeleton in gold
# ──────────────────────────────────────────────────────────────────────────────
def create_xray_glow_frame(t, width=1080, height=1920):
    img  = Image.new('RGB', (width, height), color=(15, 25, 50))
    cx, cy = 540, 960

    # Ambient glow layers around patch
    for radius, opacity in [(350, 0.08), (250, 0.12), (150, 0.18)]:
        pulse = opacity * (0.85 + 0.15 * math.sin(t * 1.8))
        glow  = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([
            cx - radius, cy - radius, cx + radius, cy + radius,
        ], fill=(*GOLD, int(255 * pulse)))
        glow = glow.filter(ImageFilter.GaussianBlur(55))
        img  = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Expanding shockwave rings
    wave_progress = (t % 2.0) / 2.0
    for ring in range(4):
        rp     = (wave_progress + ring * 0.25) % 1.0
        ring_r = int(rp * 420)
        ring_o = max(0., 1.0 - rp - ring * 0.15)
        ring_c = (
            int(ICE_BLUE[0] * ring_o),
            int(ICE_BLUE[1] * ring_o),
            int(ICE_BLUE[2] * ring_o),
        )
        if ring_r > 0 and any(c > 0 for c in ring_c):
            draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
                         outline=ring_c, width=3)

    # Skeleton illuminated by gold glow
    gi = 0.5 + 0.5 * math.sin(t * math.pi)
    sk = tuple(int(c * gi) for c in GOLD)
    draw.ellipse([490, 550, 590, 650], outline=sk, width=4)          # head
    draw.line([(540, 650), (540, 950)],             fill=sk, width=4)  # spine
    draw.line([(380, 720), (700, 720)],             fill=sk, width=4)  # shoulders
    draw.line([(380, 720), (320, 880)],             fill=sk, width=3)  # left arm
    draw.line([(700, 720), (760, 880)],             fill=sk, width=3)  # right arm
    draw.line([(420, 950), (660, 950)],             fill=sk, width=4)  # hips
    draw.line([(420, 950), (390, 1150)],            fill=sk, width=3)  # left leg
    draw.line([(660, 950), (690, 1150)],            fill=sk, width=3)  # right leg

    # AuraEase gold patch — pulsing glow
    pp     = 0.7 + 0.3 * math.sin(t * 4)
    pc     = tuple(int(c * pp) for c in GOLD)
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

    # Text
    brand_a = eo(t, 1.2)
    img = put_text(img, "AuraEase™", H // 2 - 250, fb(88), WHITE, alpha=brand_a)
    if t >= 0.8:
        a2  = eo(t - 0.8, 0.8)
        img = put_text(img, "Hot & Cold Therapy", H // 2 - 100, fb(44), GOLD, alpha=a2)
    if t >= 2.0:
        a3  = eo(t - 2.0, 1.0)
        img = put_text(img, "Invisible sous vos vetements.", H // 2 + 80,
                       fb(38), (200, 220, 255), alpha=a3)
    if t >= 3.2:
        a4  = eo(t - 3.2, 0.8)
        img = put_text(img, "0 medicaments. 100% naturel.", H // 2 + 210,
                       fb(36), (180, 210, 255), alpha=a4)

    return np.array(img)


# ── TECHNIQUE 3 — CINEMATIC RHYTHM CTA ────────────────────────────────────────
# Fast hook (0-2s) → Slow reveal (2-7s) → Accelerating CTA (7-12s)
# Checkmarks slam in, CTA button pulses
# ──────────────────────────────────────────────────────────────────────────────
_CTA_ITEMS = [
    ("Soulage en 30 secondes",  0.0),
    ("Sans medicaments",         0.55),
    ("Discret et invisible",     1.1),
]

def create_cta_frame(t, width=1080, height=1920):
    img = Image.new("RGB", (width, height), NAVY)

    # Animated gradient overlay (navy → gold tint, bottom)
    grad = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(0, height, 3):
        p   = y / height
        mix = p * 0.18
        r   = int(NAVY[0] + (GOLD[0] - NAVY[0]) * mix)
        g   = int(NAVY[1] + (GOLD[1] - NAVY[1]) * mix)
        b   = int(NAVY[2] + (GOLD[2] - NAVY[2]) * mix * 0.3)
        gd.rectangle([(0, y), (width, y + 3)], fill=(r, g, b, 255))
    img = Image.alpha_composite(img.convert("RGBA"), grad).convert("RGB")

    # Subtle radial glow center
    center_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(center_glow).ellipse(
        [340, 600, 740, 1000], fill=(*GOLD, 18)
    )
    center_glow = center_glow.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img.convert("RGBA"), center_glow).convert("RGB")

    # Brand title
    brand_a = eo(t, 0.55)
    img = put_text(img, "AuraEase™", H // 2 - 420, fb(90), WHITE,
                   alpha=brand_a, dy=int((1 - brand_a) * 60))
    tag_a = eo(max(0., t - 0.3), 0.45)
    img   = put_text(img, "Ton secret bien-etre.", H // 2 - 270, fb(44),
                     GOLD, alpha=tag_a)

    # Divider line
    if t >= 0.5:
        div_a = eo(t - 0.5, 0.4)
        line_w = int(600 * div_a)
        div_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        x0 = (width - line_w) // 2
        ImageDraw.Draw(div_layer).rectangle(
            [x0, H // 2 - 180, x0 + line_w, H // 2 - 178],
            fill=(*GOLD, int(255 * div_a * 0.6))
        )
        img = Image.alpha_composite(img.convert("RGBA"), div_layer).convert("RGB")

    # Checkmark benefits — slam in from left
    ck_x = 155
    for (text, delay), row in zip(_CTA_ITEMS, range(3)):
        lt = t - delay
        if lt < 0:
            continue
        a    = eo(lt, 0.30)
        cy_  = H // 2 - 60 + row * 135
        dx   = int((1 - a) * -140)

        # Circle badge with checkmark
        badge = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        bd    = ImageDraw.Draw(badge)
        bd.ellipse([ck_x + dx - 36, cy_ - 36, ck_x + dx + 36, cy_ + 36],
                   fill=(*GOLD, int(255 * a)))
        bd.text((ck_x + dx - 18, cy_ - 26), "✓",
                font=fb(44), fill=(*NAVY, int(255 * a)))
        img = Image.alpha_composite(img.convert("RGBA"), badge).convert("RGB")

        img = put_text(img, text, cy_, fb(46), WHITE, alpha=a, dx=55 + dx)

    # CTA button — pulses after 2s
    if t >= 2.0:
        btn_a   = eo(t - 2.0, 0.55)
        pulse   = 1.0 + 0.025 * math.sin(t * math.pi * 2.8)
        btn_w   = int(680 * pulse)
        btn_h   = 118
        btn_cx  = W // 2
        btn_cy  = H // 2 + 370
        bx0     = btn_cx - btn_w // 2
        bx1     = btn_cx + btn_w // 2
        by0     = btn_cy - btn_h // 2
        by1     = btn_cy + btn_h // 2

        # Glow behind button
        btn_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(btn_glow).rounded_rectangle(
            [bx0 - 12, by0 - 12, bx1 + 12, by1 + 12],
            radius=66, fill=(*GOLD, int(255 * btn_a * 0.35))
        )
        btn_glow = btn_glow.filter(ImageFilter.GaussianBlur(20))
        img = Image.alpha_composite(img.convert("RGBA"), btn_glow).convert("RGB")

        ImageDraw.Draw(img).rounded_rectangle(
            [bx0, by0, bx1, by1], radius=59,
            fill=GOLD, outline=(*WHITE, int(255 * btn_a * 0.9)), width=3
        )
        img = put_text(img, "Lien en bio  →", btn_cy, fb(46), NAVY, alpha=btn_a)

    # Fade-in at scene start
    if t < 0.22:
        alpha_in = t / 0.22
        black    = np.zeros((height, width, 3), dtype=np.uint8)
        return crossfade(black, np.array(img), alpha_in)

    return np.array(img)


# ── MASTER FRAME ───────────────────────────────────────────────────────────────

_BLEND_DUR = 0.18   # seconds for scene crossfades

def make_frame(t):
    # Scene 1: Thermal particle cloud (0-2s)
    if t < 2.0 - _BLEND_DUR:
        return create_thermal_particle_frame(t, center_x=540, center_y=800)

    # Crossfade 1→2
    elif t < 2.0:
        a   = (t - (2.0 - _BLEND_DUR)) / _BLEND_DUR
        fr1 = create_thermal_particle_frame(t, center_x=540, center_y=800)
        fr2 = create_xray_glow_frame(0.0, 1080, 1920)
        return crossfade(fr1, fr2, a)

    # Scene 2: X-Ray glow reveal (2-7s)
    elif t < 7.0 - _BLEND_DUR:
        return create_xray_glow_frame(t - 2.0, 1080, 1920)

    # Crossfade 2→3
    elif t < 7.0:
        a   = (t - (7.0 - _BLEND_DUR)) / _BLEND_DUR
        fr2 = create_xray_glow_frame(t - 2.0, 1080, 1920)
        fr3 = create_cta_frame(0.0, 1080, 1920)
        return crossfade(fr2, fr3, a)

    # Scene 3: Fast CTA (7-12s)
    else:
        return create_cta_frame(t - 7.0, 1080, 1920)


# ── BUILD ──────────────────────────────────────────────────────────────────────

def build():
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "auraease_premium_v1.mp4"
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
