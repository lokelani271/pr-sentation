"""
AuraEase™ — Video 1.1 "The Math is Mathing"
Duration: 16s | Format: 1080x1920 | 30 FPS | H264 | no audio
All visuals generated programmatically — no external assets required.

Scene structure:
  Hook    0-2s   "$150 vs $35. You choose."
  Scene 1 2-5s   Split screen  "Same problem. Different price."
  Scene 2 5-9s   Clock compare "1 hour vs. Unlimited relief."
  Scene 3 9-14s  Body + patch  "Stop overpaying. Manage your tension daily."
  Scene 4 14-16s Logo CTA      "The math is mathing."
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
FIRE_RED = (220, 60,  50)
LIGHT_BG = (245, 245, 250)
DARK_BG  = (15,  22,  45)

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

def put_text_left(img, text, x0, cy, fnt, color, alpha=1.0, max_w=460):
    lines = _wrap(text, fnt, max_w)
    lh    = fnt.size + 14
    y0_   = cy - len(lines) * lh // 2
    canvas = img.convert("RGBA")
    layer  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d      = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        d.text((x0, y0_ + i * lh), ln, font=fnt,
               fill=(*color[:3], int(255 * alpha)))
    return Image.alpha_composite(canvas, layer).convert("RGB")

def eo(t, d):
    p = max(0., min(1., t / max(d, 1e-9)))
    return 1 - (1 - p) ** 3

def crossfade(a, b, alpha):
    return (np.array(a, float) * (1 - alpha) + np.array(b, float) * alpha).astype(np.uint8)

def glow_layer(img, cx, cy, color, radius, opacity):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(*color, int(255 * opacity))
    )
    g = g.filter(ImageFilter.GaussianBlur(radius // 2))
    return Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")

# ── Stick figure (reused from other AuraEase videos) ──────────────────────────

FIG_CX, FIG_CY = W // 2, 1290

def _fig_pts():
    cx, cy = FIG_CX, FIG_CY
    return dict(
        head        = (cx,      cy - 330),
        neck        = (cx,      cy - 282),
        left_sh     = (cx - 88, cy - 245),
        right_sh    = (cx + 88, cy - 245),
        sh_mid      = (cx,      cy - 245),
        mid_spine   = (cx,      cy - 120),
        lower_back  = (cx,      cy -  55),
        left_hip    = (cx - 55, cy),
        right_hip   = (cx + 55, cy),
        hip_mid     = (cx,      cy),
        left_elbow  = (cx - 128,cy - 110),
        right_elbow = (cx + 128,cy - 110),
        left_hand   = (cx - 115,cy +  30),
        right_hand  = (cx + 115,cy +  30),
        left_knee   = (cx - 55, cy + 185),
        right_knee  = (cx + 55, cy + 185),
        left_foot   = (cx - 60, cy + 370),
        right_foot  = (cx + 60, cy + 370),
    )

def draw_figure(img, color, alpha):
    p  = _fig_pts()
    c  = (*color, int(255 * alpha))
    lw, lwa, hr = 22, 16, 46
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    hx, hy = p['head']
    d.ellipse([(hx - hr, hy - hr), (hx + hr, hy + hr)], fill=c)
    d.line([p['head'],   p['neck']],                    fill=c, width=lw)
    d.line([p['left_sh'],p['right_sh']],                fill=c, width=lw)
    d.line([p['neck'],   p['sh_mid']],                  fill=c, width=lw)
    d.line([p['sh_mid'], p['mid_spine'], p['hip_mid']], fill=c, width=lw)
    d.line([p['left_sh'],  p['left_elbow'],  p['left_hand']],  fill=c, width=lwa)
    d.line([p['right_sh'], p['right_elbow'], p['right_hand']], fill=c, width=lwa)
    d.line([p['left_hip'], p['right_hip']],              fill=c, width=lw)
    d.line([p['left_hip'],  p['left_knee'],  p['left_foot']],  fill=c, width=lw)
    d.line([p['right_hip'], p['right_knee'], p['right_foot']], fill=c, width=lw)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_patch(img, alpha, pulse_t=0.0):
    p        = _fig_pts()
    lbx, lby = p['lower_back']
    pw, ph   = 104, 64
    pulse    = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(pulse_t * math.pi * 2.5))
    glow     = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [(lbx - pw//2 - 12, lby - ph//2 - 12),
         (lbx + pw//2 + 12, lby + ph//2 + 12)],
        radius=20, fill=(*GOLD, int(255 * alpha * 0.5))
    )
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    rect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rect).rounded_rectangle(
        [(lbx - pw//2, lby - ph//2), (lbx + pw//2, lby + ph//2)],
        radius=13, fill=(*GOLD, int(255 * alpha)),
        outline=(*WHITE, int(255 * alpha * 0.9)), width=4,
    )
    canvas = img.convert("RGBA")
    canvas = Image.alpha_composite(canvas, glow)
    canvas = Image.alpha_composite(canvas, rect)
    return canvas.convert("RGB")

# ── HOOK (0-2s) ───────────────────────────────────────────────────────────────
# Navy BG · "$150" red slams left · "vs" fades center · "$35" gold slams right
# Bottom: "You choose." fades in
# ──────────────────────────────────────────────────────────────────────────────

def scene_hook(t):
    img = Image.new("RGB", (W, H), NAVY)

    # Subtle background glow
    img = glow_layer(img, W//2, H//2, GOLD, 500, 0.06)

    mid_y = H // 2 - 60

    # "$150" — slides from left, red
    a1  = eo(t, 0.35)
    dx1 = int((1 - a1) * -220)
    img = put_text(img, "$150", mid_y - 60, fb(180), FIRE_RED, alpha=a1, dx=dx1 - 240)

    # "vs" — fades center
    a_vs = eo(max(0., t - 0.2), 0.4)
    img  = put_text(img, "vs", mid_y + 10, fb(60), (180, 190, 210), alpha=a_vs)

    # "$35" — slides from right, gold
    a2  = eo(max(0., t - 0.1), 0.35)
    dx2 = int((1 - a2) * 220)
    img = put_text(img, "$35", mid_y - 60, fb(180), GOLD, alpha=a2, dx=dx2 + 240)

    # Sub-labels
    if t >= 0.3:
        al = eo(t - 0.3, 0.35)
        img = put_text(img, "Physio", mid_y + 120, fb(46), (200, 100, 90),
                       alpha=al, dx=-240)
        img = put_text(img, "AuraEase™", mid_y + 120, fb(46), GOLD,
                       alpha=al, dx=240)

    # Gold divider line (vertical, center)
    if t >= 0.15:
        div_h = int(min(1.0, (t - 0.15) / 0.4) * 260)
        dl    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(dl).rectangle(
            [W//2 - 3, mid_y - 130, W//2 + 3, mid_y - 130 + div_h],
            fill=(*GOLD, 200)
        )
        img = Image.alpha_composite(img.convert("RGBA"), dl).convert("RGB")

    # "You choose." tagline
    if t >= 0.8:
        a3  = eo(t - 0.8, 0.45)
        img = put_text(img, "You choose.", H // 2 + 320, fb(68), WHITE, alpha=a3)

    # Fade-in
    fi = min(1.0, t / 0.15)
    if fi < 1.0:
        black = np.zeros((H, W, 3), dtype=np.uint8)
        return crossfade(black, img, fi)

    return np.array(img)


# ── SCENE 1 (2-5s) — SPLIT SCREEN ────────────────────────────────────────────
# Left half: dark navy, "$150 / session" in red
# Right half: white/frost, "$35 / patch" in gold
# Top: "Same problem." | Bottom: "Different price."
# ──────────────────────────────────────────────────────────────────────────────

def scene_split(t):
    img = Image.new("RGB", (W, H), LIGHT_BG)

    # Left panel — dark navy, slides in from left
    panel_w = int(W // 2 * eo(t, 0.45))
    if panel_w > 0:
        panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(panel).rectangle([(0, 0), (panel_w, H)],
                                        fill=(*NAVY, 255))
        img = Image.alpha_composite(img.convert("RGBA"), panel).convert("RGB")

    # Gold divider
    div_h = int(H * min(1.0, t / 0.5))
    dl    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(dl).rectangle(
        [W//2 - 4, (H - div_h)//2, W//2 + 4, (H + div_h)//2],
        fill=(*GOLD, 220)
    )
    img = Image.alpha_composite(img.convert("RGBA"), dl).convert("RGB")

    # LEFT SIDE text: "$150" + labels
    la = eo(max(0., t - 0.35), 0.45)
    if la > 0:
        img = put_text(img, "$150", H//2 - 120, fb(140), FIRE_RED,
                       alpha=la, dx=-270)
        img = put_text(img, "per session", H//2 + 50, fb(40), (200, 170, 170),
                       alpha=la, dx=-270)
        img = put_text(img, "1 hour only", H//2 + 130, fb(36), (180, 150, 150),
                       alpha=la, dx=-270)

    # RIGHT SIDE text: "$35" + labels
    ra = eo(max(0., t - 0.5), 0.45)
    if ra > 0:
        img = put_text(img, "$35", H//2 - 120, fb(140), GOLD,
                       alpha=ra, dx=260)
        img = put_text(img, "one patch", H//2 + 50, fb(40), (120, 100, 60),
                       alpha=ra, dx=260)
        img = put_text(img, "unlimited use", H//2 + 130, fb(36), (140, 115, 70),
                       alpha=ra, dx=260)

    # Top banner
    ta = eo(max(0., t - 0.6), 0.4)
    img = put_text(img, "Same problem.", 260, fb(64), NAVY, alpha=ta)

    # Bottom banner
    ba = eo(max(0., t - 0.9), 0.4)
    img = put_text(img, "Different price.", H - 280, fb(64), GOLD, alpha=ba)

    return np.array(img)


# ── SCENE 2 (5-9s) — TIME COMPARISON ─────────────────────────────────────────
# Dark BG, animated clock icon on left fades out
# Infinity/star icon on right glows in
# Text: "1 hour vs. Unlimited relief."
# ──────────────────────────────────────────────────────────────────────────────

def _draw_clock(img, cx, cy, radius, color, alpha, minute_angle_deg):
    """Draw a simple clock face with hour hand at 12 and minute hand animated."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    c     = (*color, int(255 * alpha))
    # face
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              outline=c, width=5)
    # hour hand (points up)
    d.line([(cx, cy), (cx, cy - int(radius * 0.5))], fill=c, width=7)
    # minute hand (rotates)
    rad = math.radians(minute_angle_deg - 90)
    mx  = cx + int(math.cos(rad) * radius * 0.75)
    my  = cy + int(math.sin(rad) * radius * 0.75)
    d.line([(cx, cy), (mx, my)], fill=c, width=5)
    # center dot
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=c)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def _draw_infinity(img, cx, cy, radius, color, alpha):
    """Draw an ∞ symbol using two overlapping circles."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    c     = (*color, int(255 * alpha))
    r2    = int(radius * 0.6)
    offset = int(radius * 0.65)
    d.ellipse([cx - offset - r2, cy - r2, cx - offset + r2, cy + r2],
              outline=c, width=7)
    d.ellipse([cx + offset - r2, cy - r2, cx + offset + r2, cy + r2],
              outline=c, width=7)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def scene_time(t):
    img = Image.new("RGB", (W, H), DARK_BG)

    # Ambient glow
    img = glow_layer(img, W//2, H//2, GOLD, 600, 0.06)

    icon_y  = H // 2 - 100
    text_y  = H // 2 + 250

    # LEFT — Clock (fades out after 1.5s)
    clock_a = eo(t, 0.5) * max(0., 1 - eo(max(0., t - 1.8), 0.6))
    if clock_a > 0.01:
        minute_angle = (t * 180) % 360   # spins during scene
        img = _draw_clock(img, W//4, icon_y, 120, FIRE_RED, clock_a, minute_angle)
        img = put_text(img, "1 hour", icon_y + 170, fb(58), FIRE_RED,
                       alpha=clock_a, dx=-W//4)

    # "X" cross-out on left
    if t >= 1.0:
        xa  = eo(t - 1.0, 0.35)
        xl  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        xd  = ImageDraw.Draw(xl)
        xc  = (*FIRE_RED, int(255 * xa))
        xd.line([(W//4 - 90, icon_y - 90), (W//4 + 90, icon_y + 90)],
                fill=xc, width=10)
        xd.line([(W//4 + 90, icon_y - 90), (W//4 - 90, icon_y + 90)],
                fill=xc, width=10)
        img = Image.alpha_composite(img.convert("RGBA"), xl).convert("RGB")

    # RIGHT — Infinity (fades in at 0.8s)
    inf_a = eo(max(0., t - 0.8), 0.6)
    if inf_a > 0.01:
        pulse = 0.85 + 0.15 * math.sin(t * math.pi * 2)
        img   = glow_layer(img, 3 * W // 4, icon_y, GOLD, 160, 0.18 * inf_a * pulse)
        img   = _draw_infinity(img, 3 * W // 4, icon_y, 120, GOLD, inf_a)
        img   = put_text(img, "Unlimited", icon_y + 170, fb(58), GOLD,
                         alpha=inf_a, dx=W//4)

    # Center divider "vs"
    vs_a = eo(max(0., t - 0.4), 0.4)
    img  = put_text(img, "vs", icon_y, fb(52), (160, 170, 200), alpha=vs_a)

    # Main tagline
    if t >= 1.0:
        tag_a = eo(t - 1.0, 0.5)
        img   = put_text(img, "1 session vs.", text_y - 60, fb(60),
                         WHITE, alpha=tag_a)
    if t >= 1.5:
        tag2  = eo(t - 1.5, 0.5)
        img   = put_text(img, "Unlimited relief.", text_y + 60, fb(60),
                         GOLD, alpha=tag2)

    return np.array(img)


# ── SCENE 3 (9-12s) — BODY + PATCH ───────────────────────────────────────────
# White BG, stick figure with glowing gold patch
# Text: "Stop overpaying." / "Manage your tension daily."
# ──────────────────────────────────────────────────────────────────────────────

def scene_spine(t):
    img = Image.new("RGB", (W, H), LIGHT_BG)

    fig_a   = eo(t, 0.55)
    patch_a = eo(max(0., t - 0.4), 0.55)

    img = draw_figure(img, NAVY, fig_a)
    if patch_a > 0:
        img = draw_patch(img, patch_a, pulse_t=t)

    # Arrow label pointing to patch
    if t >= 0.6:
        arr_a  = eo(t - 0.6, 0.45)
        bounce = int(8 * math.sin((t - 0.6) * math.pi * 3.5))
        lbx, lby = _fig_pts()['lower_back']
        # arrow text left-anchored after patch right edge
        al = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(al).text(
            (lbx + 72 + bounce, lby - 20),
            "← AuraEase™ patch",
            font=fb(34),
            fill=(*NAVY, int(255 * arr_a))
        )
        img = Image.alpha_composite(img.convert("RGBA"), al).convert("RGB")

    # Text block
    a1 = eo(max(0., t - 0.8), 0.45)
    img = put_text(img, "Stop overpaying.", 340, fb(68), NAVY, alpha=a1)

    if t >= 1.4:
        a2 = eo(t - 1.4, 0.45)
        img = put_text(img, "Manage your tension daily.", 460, fb(48),
                       (80, 100, 140), alpha=a2)

    # Price pill
    if t >= 1.9:
        a3     = eo(t - 1.9, 0.4)
        pill_w = 420
        pill_h = 90
        pill_x = (W - pill_w) // 2
        pill_y = H - 420
        pl     = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(pl).rounded_rectangle(
            [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
            radius=45, fill=(*GOLD, int(255 * a3))
        )
        img = Image.alpha_composite(img.convert("RGBA"), pl).convert("RGB")
        img = put_text(img, "Only $35", pill_y + pill_h // 2, fb(48),
                       NAVY, alpha=a3)

    # Extended content for 5s scene — 3 checkmarks slide in after 2.5s
    _checks = [
        ("Works in 30 seconds",     2.5),
        ("Invisible under clothes", 3.1),
        ("$35 vs $150 physio",      3.7),
    ]
    ck_x = 145
    for text, delay in _checks:
        lt = t - delay
        if lt < 0:
            continue
        a   = eo(lt, 0.32)
        row = _checks.index((text, delay))
        cy_ = H - 310 + row * 110
        dx  = int((1 - a) * -130)

        badge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd    = ImageDraw.Draw(badge)
        bd.ellipse([ck_x + dx - 30, cy_ - 30, ck_x + dx + 30, cy_ + 30],
                   fill=(*GOLD, int(255 * a)))
        bd.text((ck_x + dx - 16, cy_ - 23), "✓",
                font=fb(38), fill=(*NAVY, int(255 * a)))
        img = Image.alpha_composite(img.convert("RGBA"), badge).convert("RGB")
        img = put_text(img, text, cy_, fb(42), NAVY, alpha=a, dx=48 + dx)

    return np.array(img)


# ── SCENE 4 (12-14s) — "THE MATH IS MATHING" CTA ─────────────────────────────
# Navy BG, big text, pulsing CTA button
# ──────────────────────────────────────────────────────────────────────────────

def scene_final(t):
    img = Image.new("RGB", (W, H), NAVY)

    # Gradient overlay
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(0, H, 3):
        mix = (y / H) * 0.22
        r   = int(NAVY[0] + (GOLD[0] - NAVY[0]) * mix)
        g_  = int(NAVY[1] + (GOLD[1] - NAVY[1]) * mix)
        b   = int(NAVY[2] + (GOLD[2] - NAVY[2]) * mix * 0.3)
        gd.rectangle([(0, y), (W, y + 3)], fill=(r, g_, b, 255))
    img = Image.alpha_composite(img.convert("RGBA"), grad).convert("RGB")

    # Radial glow
    img = glow_layer(img, W//2, H//2 - 80, GOLD, 500, 0.08 + 0.04 * math.sin(t * math.pi * 2))

    # "THE MATH" — slams in
    a1  = eo(t, 0.45)
    img = put_text(img, "THE MATH", H//2 - 250, fb(110), WHITE,
                   alpha=a1, dy=int((1 - a1) * 80))

    # "IS MATHING." — gold, delayed
    if t >= 0.3:
        a2  = eo(t - 0.3, 0.45)
        img = put_text(img, "IS MATHING.", H//2 - 90, fb(110), GOLD,
                       alpha=a2, dy=int((1 - a2) * 60))

    # AuraEase brand
    if t >= 0.7:
        a3  = eo(t - 0.7, 0.4)
        img = put_text(img, "AuraEase™", H//2 + 120, fb(52), WHITE, alpha=a3 * 0.8)

    # Pulsing CTA button
    if t >= 0.9:
        btn_a  = eo(t - 0.9, 0.5)
        pulse  = 1.0 + 0.03 * math.sin(t * math.pi * 3.2)
        btn_w  = int(680 * pulse)
        btn_h  = 120
        btn_cy = H//2 + 350
        bx0    = W//2 - btn_w//2
        bx1    = W//2 + btn_w//2
        by0    = btn_cy - btn_h//2
        by1    = btn_cy + btn_h//2

        glow_btn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow_btn).rounded_rectangle(
            [bx0 - 14, by0 - 14, bx1 + 14, by1 + 14],
            radius=68, fill=(*GOLD, int(255 * btn_a * 0.36))
        )
        glow_btn = glow_btn.filter(ImageFilter.GaussianBlur(22))
        img = Image.alpha_composite(img.convert("RGBA"), glow_btn).convert("RGB")
        ImageDraw.Draw(img).rounded_rectangle(
            [bx0, by0, bx1, by1], radius=60,
            fill=GOLD, outline=(*WHITE, int(255 * btn_a * 0.9)), width=3
        )
        img = put_text(img, "Link in bio  →", btn_cy, fb(48), NAVY, alpha=btn_a)

    # Fade-in at start
    if t < 0.18:
        black = np.zeros((H, W, 3), dtype=np.uint8)
        return crossfade(black, np.array(img), t / 0.18)

    return np.array(img)


# ── MASTER FRAME ───────────────────────────────────────────────────────────────
# S1 0-2s | S2 2-5s | S3 5-9s | S4 9-12s | S5 12-14s
# ──────────────────────────────────────────────────────────────────────────────

CUT = [0.0, 2.0, 5.0, 9.0, 14.0, 16.0]
BD  = 0.20   # crossfade blend duration (s)

_SCENES = [
    lambda t: scene_hook(t),
    lambda t: scene_split(t),
    lambda t: scene_time(t),
    lambda t: scene_spine(t),
    lambda t: scene_final(t),
]

def make_frame(t):
    for i in range(len(_SCENES)):
        s_start = CUT[i]
        s_end   = CUT[i + 1]

        if t < s_end - BD:
            if t >= s_start:
                return _SCENES[i](t - s_start)
        elif t < s_end:
            # Blend current → next scene
            if i + 1 < len(_SCENES):
                alpha  = (t - (s_end - BD)) / BD
                fr_cur = _SCENES[i](t - s_start)
                fr_nxt = _SCENES[i + 1](0.0)
                return crossfade(fr_cur, fr_nxt, alpha)

    # last scene tail
    return _SCENES[-1](t - CUT[-2])


# ── BUILD ──────────────────────────────────────────────────────────────────────

def build():
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"),
                exist_ok=True)
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "output", "v1_1_final.mp4"
    )
    VideoClip(make_frame, duration=16).write_videofile(
        out,
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        logger="bar",
    )
    print(f"\n✔  Saved → {out}")


if __name__ == "__main__":
    build()
