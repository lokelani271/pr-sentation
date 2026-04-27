"""
AuraEase™ — Video 2.1 "The 9-5 Hunch"
Duration: 16s | Format: 1080x1920 | 30 FPS | H264 | no audio
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
FIRE_RED = (220,  60,  50)
LIGHT_BG = (245, 245, 250)
DARK_BG  = (18,  24,  48)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@lru_cache(maxsize=20)
def fb(sz):
    return ImageFont.truetype(_BOLD, sz)

_DD = ImageDraw.Draw(Image.new("RGB", (1, 1)))

# ── Helpers ────────────────────────────────────────────────────────────────────

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

def put_text(img, text, cy, fnt, color, alpha=1.0, dx=0, dy=0, max_w=880):
    lines  = _wrap(text, fnt, max_w)
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

def crossfade(a, b, alpha):
    return (np.array(a, float) * (1 - alpha) + np.array(b, float) * alpha).astype(np.uint8)

def add_glow(img, cx, cy, color, radius, opacity):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(*color, int(255 * opacity))
    )
    g = g.filter(ImageFilter.GaussianBlur(radius // 2))
    return Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")

# ── Stick figures ──────────────────────────────────────────────────────────────

def draw_figure_hunched(img, color, alpha):
    """Seated figure hunched forward over a desk."""
    cx, cy = W // 2, 1080
    c   = (*color, int(255 * alpha))
    lw, lwa, hr = 20, 14, 40
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)

    # Head: leaning forward
    hx, hy = cx - 70, cy - 310
    d.ellipse([(hx - hr, hy - hr), (hx + hr, hy + hr)], fill=c)

    # Neck → upper back (angled)
    neck  = (cx - 48, cy - 265)
    sh_cx = cx - 20
    sh_cy = cy - 225
    d.line([(hx, hy + hr), neck, (sh_cx, sh_cy)], fill=c, width=lw)

    # Shoulders
    l_sh = (sh_cx - 100, sh_cy + 8)
    r_sh = (sh_cx + 80,  sh_cy + 8)
    d.line([l_sh, r_sh], fill=c, width=lw)

    # Curved spine (hunch: bows backward/up)
    mid_sp = (cx + 25, cy - 115)
    hip_m  = (cx,      cy)
    d.line([(sh_cx, sh_cy), mid_sp, hip_m], fill=c, width=lw)

    # Arms reaching toward desk
    l_elbow = (l_sh[0] - 20, cy - 80)
    r_elbow = (r_sh[0] + 20, cy - 80)
    l_hand  = (cx - 110, cy + 80)
    r_hand  = (cx + 160, cy + 80)
    d.line([l_sh, l_elbow, l_hand], fill=c, width=lwa)
    d.line([r_sh, r_elbow, r_hand], fill=c, width=lwa)

    # Hips (seated)
    l_hip = (cx - 50, cy)
    r_hip = (cx + 50, cy)
    d.line([l_hip, r_hip], fill=c, width=lw)

    # Legs bent (seated)
    l_knee = (cx - 50, cy + 130)
    r_knee = (cx + 50, cy + 130)
    l_foot = (cx - 50, cy + 130)  # feet tucked under chair
    r_foot = (cx + 50, cy + 130)
    d.line([l_hip, l_knee], fill=c, width=lw)
    d.line([r_hip, r_knee], fill=c, width=lw)

    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_desk(img, alpha):
    """Desk surface + laptop screen."""
    desk_y = 1160
    layer  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d      = ImageDraw.Draw(layer)

    # Desk surface
    d.rectangle([80, desk_y, W - 80, desk_y + 18],
                fill=(*NAVY, int(255 * alpha * 0.7)))

    # Laptop base
    lap_cx = W // 2 + 100
    d.rectangle([lap_cx - 90, desk_y - 12, lap_cx + 90, desk_y],
                fill=(*NAVY, int(255 * alpha * 0.5)))

    # Laptop screen
    d.rectangle([lap_cx - 80, desk_y - 130, lap_cx + 80, desk_y - 14],
                fill=(*DARK_BG, int(255 * alpha * 0.8)),
                outline=(*GOLD, int(255 * alpha * 0.6)), width=3)

    # Screen glow (blue light)
    screen_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(screen_glow).rectangle(
        [lap_cx - 74, desk_y - 124, lap_cx + 74, desk_y - 20],
        fill=(80, 130, 255, int(255 * alpha * 0.25))
    )
    layer = Image.alpha_composite(layer, screen_glow)

    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_figure_straight(img, color, alpha):
    """Standard upright stick figure."""
    cx, cy = W // 2, 1260
    c = (*color, int(255 * alpha))
    lw, lwa, hr = 22, 16, 46
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    hx, hy = cx, cy - 330
    d.ellipse([(hx - hr, hy - hr), (hx + hr, hy + hr)], fill=c)
    d.line([(cx, cy - 284), (cx, cy - 245)],           fill=c, width=lw)
    d.line([(cx - 88, cy - 245), (cx + 88, cy - 245)], fill=c, width=lw)
    d.line([(cx, cy - 245), (cx, cy)],                 fill=c, width=lw)
    d.line([(cx - 88, cy - 245), (cx - 128, cy - 110), (cx - 115, cy + 30)],
           fill=c, width=lwa)
    d.line([(cx + 88, cy - 245), (cx + 128, cy - 110), (cx + 115, cy + 30)],
           fill=c, width=lwa)
    d.line([(cx - 55, cy), (cx + 55, cy)],                         fill=c, width=lw)
    d.line([(cx - 55, cy), (cx - 60, cy + 185), (cx - 60, cy + 370)], fill=c, width=lw)
    d.line([(cx + 55, cy), (cx + 60, cy + 185), (cx + 60, cy + 370)], fill=c, width=lw)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_neck_patch(img, alpha, pulse_t=0.0):
    """Gold patch on upper back / neck area."""
    cx, cy = W // 2, 1260
    # upper back = between shoulders and mid-spine
    px, py = cx + 10, cy - 190
    pw, ph = 90, 56
    pulse  = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(pulse_t * math.pi * 2.5))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [(px - pw//2 - 14, py - ph//2 - 14),
         (px + pw//2 + 14, py + ph//2 + 14)],
        radius=20, fill=(*GOLD, int(255 * alpha * 0.5))
    )
    glow = glow.filter(ImageFilter.GaussianBlur(22))

    rect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rect).rounded_rectangle(
        [(px - pw//2, py - ph//2), (px + pw//2, py + ph//2)],
        radius=12, fill=(*GOLD, int(255 * alpha)),
        outline=(*WHITE, int(255 * alpha * 0.9)), width=4
    )
    canvas = img.convert("RGBA")
    canvas = Image.alpha_composite(canvas, glow)
    canvas = Image.alpha_composite(canvas, rect)
    return canvas.convert("RGB")

def draw_pain_zone(img, cx, cy, alpha, t):
    """Pulsing red pain zone."""
    pulse = alpha * (0.55 + 0.35 * math.sin(t * math.pi * 3))
    for r, op in [(180, 0.08), (120, 0.14), (70, 0.22)]:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(*FIRE_RED, int(255 * op * pulse))
        )
        g   = g.filter(ImageFilter.GaussianBlur(r // 3))
        img = Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")
    return img

# ── HOOK (0-2s) ───────────────────────────────────────────────────────────────

def scene_hook(t):
    img = Image.new("RGB", (W, H), NAVY)
    img = add_glow(img, W//2, H//2, GOLD, 550, 0.07)

    # Line 1
    a1  = eo(t, 0.40)
    img = put_text(img, "Your 9-5 shouldn't", H//2 - 160, fb(88), WHITE,
                   alpha=a1, dy=int((1 - a1) * 60))

    # Line 2 — gold, delayed
    if t >= 0.35:
        a2  = eo(t - 0.35, 0.45)
        img = put_text(img, "hurt this much.", H//2 + 20, fb(88), GOLD,
                       alpha=a2, dy=int((1 - a2) * 50))

    # Sub-hook
    if t >= 0.9:
        a3  = eo(t - 0.9, 0.4)
        img = put_text(img, "Sound familiar?", H//2 + 260, fb(50),
                       (200, 210, 230), alpha=a3)

    fi = min(1.0, t / 0.14)
    if fi < 1.0:
        return crossfade(np.zeros((H, W, 3), np.uint8), np.array(img), fi)
    return np.array(img)


# ── SCENE 1 (2-5s) — HUNCHED AT DESK ─────────────────────────────────────────

def scene_hunched(t):
    img = Image.new("RGB", (W, H), DARK_BG)

    # Pain zone: upper back (where hunch hurts)
    pain_cx, pain_cy = W//2 + 10, 870
    if t >= 0.2:
        img = draw_pain_zone(img, pain_cx, pain_cy, eo(t - 0.2, 0.5), t)

    # Desk + figure
    desk_a = eo(t, 0.35)
    img    = draw_desk(img, desk_a)
    fig_a  = eo(t, 0.50)
    img    = draw_figure_hunched(img, WHITE, fig_a)

    # Typewriter text
    img = put_typewriter(img, "POV: Your back is screaming at 3 PM.",
                         220, fb(62), WHITE, t, start=0.4, dur=0.9)

    # Label on pain zone
    if t >= 1.1:
        la  = eo(t - 1.1, 0.4)
        img = put_text(img, "← upper back tension", 870, fb(36),
                       FIRE_RED, alpha=la, dx=160)

    return np.array(img)


# ── SCENE 2 (5-9s) — GOLD PATCH REVEAL ───────────────────────────────────────

def scene_patch(t):
    img = Image.new("RGB", (W, H), LIGHT_BG)

    fig_a   = eo(t, 0.45)
    patch_a = eo(max(0., t - 0.35), 0.55)

    img = draw_figure_straight(img, NAVY, fig_a)
    if patch_a > 0:
        img = draw_neck_patch(img, patch_a, pulse_t=t)

    # Arrow label
    if t >= 0.55:
        arr_a  = eo(t - 0.55, 0.4)
        bounce = int(7 * math.sin((t - 0.55) * math.pi * 3.5))
        al = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(al).text(
            (W//2 + 68 + bounce, 1060),
            "← AuraEase™ patch",
            font=fb(34), fill=(*NAVY, int(255 * arr_a))
        )
        img = Image.alpha_composite(img.convert("RGBA"), al).convert("RGB")

    # Main text
    if t >= 0.5:
        a1 = eo(t - 0.5, 0.45)
        img = put_text(img, "The $35 desk worker", 310, fb(72), NAVY, alpha=a1)
    if t >= 0.85:
        a2 = eo(t - 0.85, 0.45)
        img = put_text(img, "cheat code.", 420, fb(72), GOLD, alpha=a2)

    # Benefits
    if t >= 1.5:
        a3 = eo(t - 1.5, 0.4)
        img = put_text(img, "Hot therapy  ·  Cold therapy", 530, fb(40),
                       (80, 100, 140), alpha=a3)
    if t >= 2.0:
        a4 = eo(t - 2.0, 0.4)
        img = put_text(img, "Invisible under your shirt.", 620, fb(40),
                       (80, 100, 140), alpha=a4)

    return np.array(img)


# ── SCENE 3 (9-14s) — STRAIGHTENED + BENEFITS ────────────────────────────────

_BENEFITS = [
    ("Dual-action thermal therapy",  0.3),
    ("Works while you type",         0.9),
    ("No wires. No prescription.",   1.5),
]

def scene_straight(t):
    img = Image.new("RGB", (W, H), NAVY)

    # Gradient
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(0, H, 3):
        mix = (y / H) * 0.16
        r   = int(NAVY[0] + (GOLD[0] - NAVY[0]) * mix)
        g_  = int(NAVY[1] + (GOLD[1] - NAVY[1]) * mix)
        b   = int(NAVY[2])
        gd.rectangle([(0, y), (W, y + 3)], fill=(r, g_, b, 255))
    img = Image.alpha_composite(img.convert("RGBA"), grad).convert("RGB")

    fig_a   = eo(t, 0.50)
    patch_a = eo(max(0., t - 0.3), 0.55)
    img     = draw_figure_straight(img, WHITE, fig_a)
    if patch_a > 0:
        img = draw_neck_patch(img, patch_a, pulse_t=t)
        img = add_glow(img, W//2 + 10, 1070, GOLD, 180,
                       0.14 * (0.8 + 0.2 * math.sin(t * math.pi * 2)))

    # Section header
    ha = eo(t, 0.45)
    img = put_text(img, "While you type.", 260, fb(76), WHITE, alpha=ha)

    # Benefits
    ck_x = 140
    for (text, delay), row in zip(_BENEFITS, range(3)):
        lt = t - delay
        if lt < 0:
            continue
        a   = eo(lt, 0.35)
        cy_ = 380 + row * 120
        dx  = int((1 - a) * -120)
        badge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd    = ImageDraw.Draw(badge)
        bd.ellipse([ck_x + dx - 32, cy_ - 32, ck_x + dx + 32, cy_ + 32],
                   fill=(*GOLD, int(255 * a)))
        bd.text((ck_x + dx - 17, cy_ - 25), "✓",
                font=fb(40), fill=(*NAVY, int(255 * a)))
        img = Image.alpha_composite(img.convert("RGBA"), badge).convert("RGB")
        img = put_text(img, text, cy_, fb(44), WHITE, alpha=a, dx=50 + dx)

    # Price reminder
    if t >= 2.5:
        pa = eo(t - 2.5, 0.4)
        img = put_text(img, "Only $35. Ships tomorrow.", 740, fb(42),
                       GOLD, alpha=pa)

    return np.array(img)


# ── SCENE 4 (14-16s) — CTA ────────────────────────────────────────────────────

def scene_cta(t):
    img = Image.new("RGB", (W, H), NAVY)
    img = add_glow(img, W//2, H//2 - 100,
                   GOLD, 500, 0.09 + 0.04 * math.sin(t * math.pi * 1.8))

    # Big headline
    a1 = eo(t, 0.42)
    img = put_text(img, "Stop the hunch.", H//2 - 220, fb(110), GOLD,
                   alpha=a1, dy=int((1 - a1) * 70))

    if t >= 0.35:
        a2 = eo(t - 0.35, 0.4)
        img = put_text(img, "AuraEase™", H//2 - 60, fb(58), WHITE, alpha=a2 * 0.85)

    # Pulsing CTA button
    if t >= 0.7:
        btn_a  = eo(t - 0.7, 0.5)
        pulse  = 1.0 + 0.028 * math.sin(t * math.pi * 3.0)
        btn_w  = int(700 * pulse)
        btn_h  = 120
        btn_cy = H//2 + 220
        bx0    = W//2 - btn_w//2
        bx1    = W//2 + btn_w//2
        by0    = btn_cy - btn_h//2
        by1    = btn_cy + btn_h//2

        bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(bg).rounded_rectangle(
            [bx0 - 14, by0 - 14, bx1 + 14, by1 + 14],
            radius=68, fill=(*GOLD, int(255 * btn_a * 0.35))
        )
        bg = bg.filter(ImageFilter.GaussianBlur(22))
        img = Image.alpha_composite(img.convert("RGBA"), bg).convert("RGB")
        ImageDraw.Draw(img).rounded_rectangle(
            [bx0, by0, bx1, by1], radius=60,
            fill=GOLD, outline=(*WHITE, int(255 * btn_a * 0.9)), width=3
        )
        img = put_text(img, "Link in bio  →", btn_cy, fb(48), NAVY, alpha=btn_a)

    if t < 0.18:
        return crossfade(np.zeros((H, W, 3), np.uint8), np.array(img), t / 0.18)
    return np.array(img)


# ── MASTER FRAME ───────────────────────────────────────────────────────────────

CUT = [0.0, 2.0, 5.0, 9.0, 14.0, 16.0]
BD  = 0.20

_SCENES = [scene_hook, scene_hunched, scene_patch, scene_straight, scene_cta]

def make_frame(t):
    for i in range(len(_SCENES)):
        s_start, s_end = CUT[i], CUT[i + 1]
        if t < s_end - BD:
            if t >= s_start:
                return _SCENES[i](t - s_start)
        elif t < s_end:
            if i + 1 < len(_SCENES):
                alpha  = (t - (s_end - BD)) / BD
                fr_cur = _SCENES[i](t - s_start)
                fr_nxt = _SCENES[i + 1](0.0)
                return crossfade(fr_cur, fr_nxt, alpha)
    return _SCENES[-1](t - CUT[-2])


# ── BUILD ──────────────────────────────────────────────────────────────────────

def build():
    os.makedirs("output", exist_ok=True)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "v2_1_final.mp4")
    VideoClip(make_frame, duration=16).write_videofile(
        out, fps=FPS, codec="libx264", audio=False,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        logger="bar",
    )
    print(f"\n✔  Saved → {out}")

if __name__ == "__main__":
    build()
