"""
auraease_script1_1.mp4
12s, 4 scenes, 1080x1920, 30fps, no audio
Scene 1 (0-3s):  Split-screen reference design (gray/navy diagonal, prices)
Scene 2 (3-6s):  Navy bg, typewriter "Stop overpaying for 1 hour."
Scene 3 (6-9s):  White bg, 3 benefit lines slide in from left
Scene 4 (9-12s): Navy bg, AuraEase™ glow + gold italic + pulsing CTA
"""

import math, os
import numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from moviepy.editor import VideoClip, concatenate_videoclips
except ImportError:
    from moviepy import VideoClip, concatenate_videoclips

# ── canvas ─────────────────────────────────────────────────────────────────
W, H = 1080, 1920
FPS  = 30

# ── palette ────────────────────────────────────────────────────────────────
NAVY      = (27,  42,  74)
WHITE     = (255, 255, 255)
GRAY_BG   = (185, 185, 185)
GREEN     = (0,   200,  80)
GREEN_TXT = (10,  30,   10)
GOLD      = (197, 158,  68)
GOLD2     = (232, 192, 100)
RED_DARK  = (130,  10,  10)
BLACK     = (0,    0,   0)

# ── fonts ───────────────────────────────────────────────────────────────────
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_ITALIC_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf",
]

@lru_cache(maxsize=32)
def font(size, italic=False):
    paths = FONT_ITALIC_PATHS if italic else FONT_PATHS
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def text_size(draw, txt, fnt):
    bb = draw.textbbox((0, 0), txt, font=fnt)
    return bb[2]-bb[0], bb[3]-bb[1]

def draw_text_centered(draw, txt, cy, fnt, color, alpha=1.0):
    w, h = text_size(draw, txt, fnt)
    x = (W - w) // 2
    y = cy - h // 2
    if alpha >= 1.0:
        draw.text((x, y), txt, font=fnt, fill=color)
    else:
        r, g, b = color
        a = int(alpha * 255)
        draw.text((x, y), txt, font=fnt, fill=(r, g, b, a))

# ── easing ──────────────────────────────────────────────────────────────────
def eo(t, d):
    p = min(max(t / d, 0), 1)
    return 1 - (1 - p) ** 3

def ei(t, d):
    p = min(max(t / d, 0), 1)
    return p ** 3

def fade(t, dur, f=0.25):
    return min(t / f, 1.0, (dur - t) / f)


# ══════════════════════════════════════════════════════════════════════════
# SCENE 1 — Split-screen reference recreation (0-3s)
# ══════════════════════════════════════════════════════════════════════════
def _draw_split_bg(img):
    """Diagonal gray-left / navy-right background."""
    d = ImageDraw.Draw(img)
    # gray left
    d.rectangle([0, 0, W, H], fill=GRAY_BG)
    # navy right polygon (diagonal edge)
    nav_poly = [(int(W * 0.52), 0), (W, 0), (W, H), (int(W * 0.38), H)]
    d.polygon(nav_poly, fill=NAVY)

def _draw_highlight_stripe(img):
    """Light diagonal reflection stripe on the gray side."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    pts = [(int(W*0.28), 0), (int(W*0.45), 0), (int(W*0.38), H), (int(W*0.20), H)]
    d.polygon(pts, fill=(255, 255, 255, 35))
    img.alpha_composite(overlay)

def _draw_green_badge(img):
    """Green rounded rectangle badge at top center."""
    bw, bh = 340, 72
    bx = (W - bw) // 2
    by = 68
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([bx, by, bx+bw, by+bh], radius=14, fill=(*GREEN, 255))
    img.alpha_composite(overlay)
    d2 = ImageDraw.Draw(img)
    fnt = font(32)
    draw_text_centered(d2, "AuraEase Wellness", by + bh//2, fnt, GREEN_TXT)

def _draw_headlines(img):
    d = ImageDraw.Draw(img)
    fnt_sub = font(36)
    draw_text_centered(d, "Affordable Wellness Solutions", 270, fnt_sub, WHITE)
    fnt_big = font(110)
    draw_text_centered(d, "Discover Your", 440, fnt_big, WHITE)
    draw_text_centered(d, "Balance", 570, fnt_big, WHITE)

def _draw_prices(img, t, left_x_offset=0, right_x_offset=0, glow_alpha=0.0):
    """Draw $150 PHYSIO (left) and $35 AURAEASE™ (right) with slide-in."""
    d = ImageDraw.Draw(img)

    # $150 — red, left panel center ~x=270
    lx = 270 + int(left_x_offset)
    fnt150 = font(130)
    w150, _ = text_size(d, "$150", fnt150)
    d.text((lx - w150//2, 730), "$150", font=fnt150, fill=RED_DARK)
    fnt_physio = font(44)
    wp, _ = text_size(d, "PHYSIO", fnt_physio)
    d.text((lx - wp//2, 875), "PHYSIO", font=fnt_physio, fill=BLACK)

    # $35 glow
    if glow_alpha > 0:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        rx = 740 + int(right_x_offset)
        fnt35 = font(130)
        w35, _ = text_size(gd, "$35", fnt35)
        for radius in [30, 20, 12]:
            ga = int(glow_alpha * 80 * (30 / (radius + 5)))
            gd.text((rx - w35//2, 730), "$35", font=fnt35,
                    fill=(*GOLD2, min(ga, 255)))
        blurred = glow.filter(ImageFilter.GaussianBlur(radius=radius))
        img.alpha_composite(blurred)

    # $35 — gold, right panel center ~x=740
    rx = 740 + int(right_x_offset)
    fnt35 = font(130)
    d2 = ImageDraw.Draw(img)
    w35, _ = text_size(d2, "$35", fnt35)
    d2.text((rx - w35//2, 730), "$35", font=fnt35, fill=GOLD)
    fnt_brand = font(44)
    wb, _ = text_size(d2, "AURAEASE™", fnt_brand)
    d2.text((rx - wb//2, 878), "AURAEASE™", font=fnt_brand, fill=WHITE)

def _draw_footer(img):
    d = ImageDraw.Draw(img)
    fnt = font(34)
    draw_text_centered(d, "reallygreatsite.com", H - 90, fnt, WHITE)

def scene1_frame(t):
    dur = 3.0
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    _draw_split_bg(img)
    _draw_highlight_stripe(img)
    _draw_green_badge(img)
    _draw_headlines(img)

    # Prices slide in during first 0.7s
    slide_dur = 0.65
    left_off  = int((1 - eo(t, slide_dur)) * -350)
    right_off = int((1 - eo(t, slide_dur)) *  350)
    glow_a    = max(0, eo(t - 0.9, 0.5)) if t > 0.9 else 0.0
    # Glow pulses gently after appearing
    if t > 1.4:
        pulse = 0.5 + 0.5 * math.sin((t - 1.4) * math.pi * 1.8)
        glow_a = 0.5 + 0.5 * pulse

    _draw_prices(img, t, left_x_offset=left_off, right_x_offset=right_off,
                 glow_alpha=glow_a)
    _draw_footer(img)
    return np.array(img.convert("RGB"))


# ══════════════════════════════════════════════════════════════════════════
# SCENE 2 — Typewriter "Stop overpaying for 1 hour." (3-6s)
# ══════════════════════════════════════════════════════════════════════════
_S2_TEXT = "Stop overpaying\nfor 1 hour."

def scene2_frame(t):
    dur = 3.0
    img = Image.new("RGBA", (W, H), (*NAVY, 255))
    d   = ImageDraw.Draw(img)

    fnt = font(62)
    full = _S2_TEXT.replace("\n", " ")
    # Reveal chars over first 1.8s
    reveal_dur = 1.8
    n = int(eo(t, reveal_dur) * len(full))
    visible = full[:n]

    # Word-wrap at 18 chars per line (simple split on space near midpoint)
    line1 = "Stop overpaying"
    line2 = "for 1 hour."
    n1 = len(line1) + 1  # +1 for space

    if n <= len(line1):
        lines = [visible, ""]
    elif n <= n1:
        lines = [line1, ""]
    else:
        lines = [line1, full[n1:n]]

    fa = fade(t, dur, f=0.3)
    line_h = 80
    cy_start = H // 2 - line_h // 2
    for i, line in enumerate(lines):
        if not line:
            continue
        w, h = text_size(d, line, fnt)
        x = (W - w) // 2
        y = cy_start + i * line_h
        r, g, b = WHITE
        d.text((x, y), line, font=fnt, fill=(r, g, b, int(fa * 255)))

    # Blinking cursor
    if n < len(full) or (int(t * 3) % 2 == 0):
        cx_line = lines[1] if n > len(line1) else lines[0]
        idx = 1 if n > len(line1) else 0
        cw, _ = text_size(d, cx_line, fnt) if cx_line else (0, 0)
        cx = (W - text_size(d, line1, fnt)[0]) // 2 + cw if idx == 0 else \
             (W - text_size(d, line2, fnt)[0]) // 2 + cw
        cy_cur = cy_start + idx * line_h
        d.rectangle([cx + 6, cy_cur + 8, cx + 10, cy_cur + 55],
                    fill=(255, 255, 255, int(fa * 200)))

    return np.array(img.convert("RGB"))


# ══════════════════════════════════════════════════════════════════════════
# SCENE 3 — White bg, 3 benefit lines slide in from left (6-9s)
# ══════════════════════════════════════════════════════════════════════════
_BENEFITS = [
    ("✅ Works in 30 seconds", NAVY,   0.15),
    ("✅ Drug-free",           NAVY,   0.55),
    ("✅ $35 one time",        GOLD,   0.95),
]

def scene3_frame(t):
    dur = 3.0
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d   = ImageDraw.Draw(img)

    fa    = fade(t, dur, f=0.25)
    fnt   = font(50)
    line_h = 115
    cy_start = H // 2 - line_h

    for i, (txt, color, delay) in enumerate(_BENEFITS):
        prog = eo(max(t - delay, 0), 0.40)
        x_off = int((1 - prog) * -W)
        w, h = text_size(d, txt, fnt)
        x = (W - w) // 2 + x_off
        y = cy_start + i * line_h
        r, g, b = color
        alpha = int(prog * fa * 255)
        d.text((x, y), txt, font=fnt, fill=(r, g, b, alpha))

    return np.array(img.convert("RGB"))


# ══════════════════════════════════════════════════════════════════════════
# SCENE 4 — Navy, AuraEase™ glow + gold italic + pulsing CTA (9-12s)
# ══════════════════════════════════════════════════════════════════════════
def _draw_glow_text(img, txt, cy, fnt, color, glow_color, glow_r, alpha=1.0):
    d_tmp = ImageDraw.Draw(img)
    w, h  = text_size(d_tmp, txt, fnt)
    x = (W - w) // 2
    y = cy - h // 2
    # Glow layer
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    for r in [glow_r, glow_r*2//3, glow_r//3]:
        ga = int(alpha * 80 * (glow_r / (r + 1)))
        gd.text((x, y), txt, font=fnt, fill=(*glow_color, min(ga, 255)))
    blurred = glow.filter(ImageFilter.GaussianBlur(radius=glow_r))
    img.alpha_composite(blurred)
    # Solid text
    d2 = ImageDraw.Draw(img)
    r, g, b = color
    d2.text((x, y), txt, font=fnt, fill=(r, g, b, int(alpha * 255)))

def scene4_frame(t):
    dur = 3.0
    img = Image.new("RGBA", (W, H), (*NAVY, 255))

    fa = fade(t, dur, f=0.3)

    # "AuraEase™" white with glow — slam in at t=0.05
    prog1 = eo(max(t - 0.05, 0), 0.35)
    fnt1  = font(90)
    _draw_glow_text(img, "AuraEase™", H//2 - 130, fnt1,
                    WHITE, WHITE, 22, alpha=prog1 * fa)

    # "The math is mathing." gold italic — appears at t=0.5
    prog2 = eo(max(t - 0.50, 0), 0.35)
    fnt2  = font(48, italic=True)
    d2    = ImageDraw.Draw(img)
    txt2  = "The math is mathing."
    w2, h2 = text_size(d2, txt2, fnt2)
    x2 = (W - w2) // 2
    y2 = H//2 - 30
    r, g, b = GOLD
    d2.text((x2, y2), txt2, font=fnt2,
            fill=(r, g, b, int(prog2 * fa * 255)))

    # "Link in bio 🔗" pulsing white — appears at t=1.0
    if t > 1.0:
        pulse = 0.65 + 0.35 * math.sin((t - 1.0) * math.pi * 2.5)
        prog3 = eo(t - 1.0, 0.35)
        fnt3  = font(36)
        d3    = ImageDraw.Draw(img)
        txt3  = "Link in bio \U0001f517"
        w3, h3 = text_size(d3, txt3, fnt3)
        x3 = (W - w3) // 2
        y3 = H//2 + 110
        d3.text((x3, y3), txt3, font=fnt3,
                fill=(255, 255, 255, int(prog3 * pulse * fa * 255)))

    return np.array(img.convert("RGB"))


# ══════════════════════════════════════════════════════════════════════════
# Crossfade helper
# ══════════════════════════════════════════════════════════════════════════
BD = 0.18  # blend duration in seconds

def crossfade(a, b, alpha):
    return (a.astype(float) * (1 - alpha) + b.astype(float) * alpha).astype(np.uint8)

# Scene durations
S1_DUR = 3.0
S2_DUR = 3.0
S3_DUR = 3.0
S4_DUR = 3.0
TOTAL  = S1_DUR + S2_DUR + S3_DUR + S4_DUR  # 12s

CUT = [0.0, S1_DUR, S1_DUR+S2_DUR, S1_DUR+S2_DUR+S3_DUR, TOTAL]

def make_frame(t):
    # Find current scene
    sc = 0
    for i in range(len(CUT)-1):
        if CUT[i] <= t < CUT[i+1]:
            sc = i
            break
    else:
        sc = len(CUT) - 2

    scene_funcs = [scene1_frame, scene2_frame, scene3_frame, scene4_frame]
    local_t = t - CUT[sc]
    local_dur = CUT[sc+1] - CUT[sc]

    frame_a = scene_funcs[sc](local_t)

    # Crossfade into next scene near the cut
    blend_start = local_dur - BD
    if local_t >= blend_start and sc < len(scene_funcs) - 1:
        alpha = (local_t - blend_start) / BD
        alpha = min(max(alpha, 0), 1)
        frame_b = scene_funcs[sc + 1](0.0)
        return crossfade(frame_a, frame_b, alpha)

    return frame_a

# ══════════════════════════════════════════════════════════════════════════
# Render
# ══════════════════════════════════════════════════════════════════════════
os.makedirs("output", exist_ok=True)
out = "output/auraease_script1_1.mp4"

clip = VideoClip(make_frame, duration=TOTAL)
clip.write_videofile(
    out,
    fps=FPS,
    codec="libx264",
    audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    logger=None,
)
print(f"\nDone → {out}")
