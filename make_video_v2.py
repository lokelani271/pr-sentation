"""
AuraEase TikTok v2 — Premium wellness ad
1080×1920 px · 15 s · 30 fps · H264 · no audio
Output: auraease_tiktok_v2.mp4
"""

import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip, concatenate_videoclips

# ── Canvas & colours ─────────────────────────────────────────────────────────
W, H   = 1080, 1920
FPS    = 30
SAFE_W = int(W * 0.82)

NAVY    = (27,  42,  74)
WHITE   = (255, 255, 255)
ICE     = (168, 216, 234)
GOLD    = (201, 169, 110)
BLACK   = (10,  10,  15)
GRAY    = (110, 110, 120)
RED     = (210,  50,  50)
PURPLE  = (45,  27, 105)
GREEN   = (55,  170,  80)

_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_REG     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_ITALIC  = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"   # closest italic-feel

@lru_cache(maxsize=30)
def fb(sz):  return ImageFont.truetype(_BOLD,   sz)
@lru_cache(maxsize=30)
def fr(sz):  return ImageFont.truetype(_REG,    sz)
@lru_cache(maxsize=30)
def fi(sz):  return ImageFont.truetype(_ITALIC, sz)

# ── Maths helpers ────────────────────────────────────────────────────────────
def eo(t, d):                          # ease-out cubic
    return 1 - (1 - max(0., min(1., t / d))) ** 3

def lerp_c(a, b, t):
    t = max(0., min(1., t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def fade(img, alpha):
    if alpha >= 1.: return img
    return Image.fromarray(
        (np.array(img, dtype=float) * max(0., alpha)).astype(np.uint8))

# ── Drawing primitives ───────────────────────────────────────────────────────
def _wrap(text, fnt, max_w):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words, lines, line = text.split(), [], ""
    for w in words:
        c = (line + " " + w).strip()
        if d.textbbox((0, 0), c, font=fnt)[2] <= max_w:
            line = c
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines or [text]


def put_text(img, text, cy, fnt, color, dx=0, alpha=1.0):
    """Draw centered text at vertical centre cy. dx = horizontal offset."""
    lines = _wrap(text, fnt, SAFE_W)
    lh    = fnt.size + 10
    y0    = cy - len(lines) * lh // 2
    ov    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(ov)
    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=fnt)
        tw   = bbox[2] - bbox[0]
        d.text(((W - tw) // 2 + dx, y0 + i * lh), ln,
               font=fnt, fill=(*color[:3], int(255 * alpha)))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def put_glow(img, text, cy, fnt, txt_col, glow_col=WHITE,
             radius=18, glow_a=0.8, txt_a=1.0):
    """Text with a blurred halo behind it."""
    lines = _wrap(text, fnt, SAFE_W)
    lh    = fnt.size + 10
    y0    = cy - len(lines) * lh // 2
    gl    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(gl)
    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=fnt)
        tw   = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, y0 + i * lh), ln,
               font=fnt, fill=(*glow_col[:3], int(220 * glow_a)))
    gl = gl.filter(ImageFilter.GaussianBlur(radius))
    base = Image.alpha_composite(img.convert("RGBA"), gl).convert("RGB")
    return put_text(base, text, cy, fnt, txt_col, alpha=txt_a)


def vgrad(c1, c2):
    """Vertical gradient from c1 (top) to c2 (bottom)."""
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        arr[y] = lerp_c(c1, c2, y / H)
    return Image.fromarray(arr)


# ── Precomputed assets ────────────────────────────────────────────────────────
# --- Scene 2 panels (built once) ---
def _left_panel():
    p = Image.new("RGB", (W // 2, H), NAVY)
    d = ImageDraw.Draw(p)
    hw = W // 2
    # Ice bag
    bx, by, bw, bh = 65, 520, 410, 340
    d.rounded_rectangle([bx, by, bx+bw, by+bh], radius=28,
                        fill=(130, 190, 225), outline=(175, 220, 245), width=4)
    d.rounded_rectangle([bx+18, by+18, bx+bw-18, by+bh-18], radius=18,
                        outline=(160, 215, 240), width=2)
    d.text((bx + 70, by + bh // 2 - 22), "ICE PACK", font=fb(38), fill=(200, 235, 248))
    # Tie
    d.rectangle([bx+bw//2-18, by-35, bx+bw//2+18, by+8], fill=(105, 170, 210))
    # Red X
    xc, xs = (hw // 2, 1010), 72
    d.line([(xc[0]-xs, xc[1]-xs), (xc[0]+xs, xc[1]+xs)], fill=RED, width=13)
    d.line([(xc[0]+xs, xc[1]-xs), (xc[0]-xs, xc[1]+xs)], fill=RED, width=13)
    # Label
    lbl = "Old way  ❄"
    bx2 = d.textbbox((0,0), lbl, font=fb(60))
    d.text(((hw - bx2[2]) // 2, 1140), lbl, font=fb(60), fill=WHITE)
    return p


def _right_panel():
    p = Image.new("RGB", (W // 2, H), WHITE)
    d = ImageDraw.Draw(p)
    hw = W // 2
    # Gel pack
    px, py, pw, ph = 55, 490, 430, 380
    d.rounded_rectangle([px, py, px+pw, py+ph], radius=44,
                        fill=NAVY, outline=ICE, width=5)
    d.rounded_rectangle([px+18, py+18, px+pw-18, py+ph-18], radius=32,
                        outline=(55, 95, 150), width=2)
    lbl1 = "AuraEase™"
    b1 = d.textbbox((0,0), lbl1, font=fb(40))
    d.text(((hw-b1[2])//2, py + ph//2 - 38), lbl1, font=fb(40), fill=WHITE)
    lbl2 = "Hot & Cold"
    b2 = d.textbbox((0,0), lbl2, font=fr(28))
    d.text(((hw-b2[2])//2, py+ph//2+22), lbl2, font=fr(28), fill=ICE)
    # Green check circle
    cr, cc = 62, (hw//2, 1020)
    d.ellipse([cc[0]-cr, cc[1]-cr, cc[0]+cr, cc[1]+cr], fill=GREEN)
    d.line([(cc[0]-30, cc[1]+4), (cc[0]-6, cc[1]+30),
            (cc[0]+30, cc[1]-22)], fill=WHITE, width=9)
    # Label
    lbl = "New way  ★"
    bx3 = d.textbbox((0,0), lbl, font=fb(60))
    d.text(((hw-bx3[2])//2, 1140), lbl, font=fb(60), fill=NAVY)
    return p


LEFT_PAN  = _left_panel()
RIGHT_PAN = _right_panel()

# Precomputed static gradients
GRAD_ICE_WHITE   = vgrad(ICE, WHITE)
GRAD_WHITE_ICE   = vgrad(WHITE, ICE)

# Scene 3 particles (deterministic)
_rng_snow = random.Random(7)
SNOW = [(_rng_snow.randint(20, 175),
         _rng_snow.randint(0, H),
         _rng_snow.uniform(60, 140)) for _ in range(14)]

_rng_heat = random.Random(13)
HEAT = [(_rng_heat.randint(W - 185, W - 30),
         _rng_heat.randint(0, H),
         _rng_heat.uniform(55, 130)) for _ in range(12)]

# Scene 5 particles
_rng_dots = random.Random(99)
DOTS = [(_rng_dots.randint(40, W - 40),
         _rng_dots.randint(0, H),
         _rng_dots.uniform(50, 110),
         _rng_dots.randint(3, 9)) for _ in range(35)]


# ── Scene factories ───────────────────────────────────────────────────────────

MAIN_TEXT = "Your back is SCREAMING."
SUB_TEXT  = "And you’re still ignoring it."

def scene1(t):
    """0–2.5 s · white bg · red pulse · typewriter"""
    img  = Image.new("RGB", (W, H), WHITE)
    pulse = math.sin(t * 2 * math.pi * 1.8)
    r     = int(105 + 22 * pulse)
    cx, cy = W // 2, 480

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(ov)
    for dr in (50, 32, 16):
        rr = r + dr
        dv.ellipse([cx-rr, cy-rr, cx+rr, cy+rr],
                   fill=(*RED, max(0, 48 - dr)))
    dv.ellipse([cx-r, cy-r, cx+r, cy+r],
               fill=(*RED, int(195 + 45 * pulse)))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    # Typewriter
    n = int(min(len(MAIN_TEXT), t / 1.5 * len(MAIN_TEXT)))
    if n:
        img = put_text(img, MAIN_TEXT[:n], 820, fb(74), BLACK)

    # Sub text
    sub_a = eo(t - 1.75, 0.45)
    if sub_a > 0:
        img = put_text(img, SUB_TEXT, 960, fi(42), GRAY, alpha=sub_a)

    return np.array(img)


def scene2(t):
    """2.5–5 s · split screen slides in from edges"""
    slide  = eo(t, 0.6)
    lx     = int((1 - slide) * (-W // 2))
    rx     = int(W // 2 + (1 - slide) * (W // 2))
    fade_a = min(1., t / 0.12)

    img = Image.new("RGB", (W, H), (220, 220, 225))
    img.paste(LEFT_PAN,  (lx, 0))
    img.paste(RIGHT_PAN, (rx, 0))

    # Centre divider line
    if slide > 0.65:
        d   = ImageDraw.Draw(img)
        la  = int(255 * (slide - 0.65) / 0.35)
        d.line([(W // 2, 0), (W // 2, H)], fill=(160, 160, 165), width=2)

    return np.array(fade(img, fade_a))


def scene3(t):
    """5–8 s · ice-blue gradient · Ken Burns product · particles · text up"""
    img  = GRAD_ICE_WHITE.copy()
    zoom = 1.0 + 0.038 * (t / 3.0)
    pw   = int(580 * zoom)
    ph   = int(680 * zoom)
    px_  = (W - pw) // 2
    py_  = (H - ph) // 2 - 90

    # Product shadow
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(ov)
    for s in (22, 13, 6):
        dv.rounded_rectangle([px_+s, py_+s, px_+pw+s, py_+ph+s],
                             radius=46, fill=(0, 0, 0, 16))
    # Product body
    dv.rounded_rectangle([px_, py_, px_+pw, py_+ph],
                         radius=46, fill=(*NAVY, 255),
                         outline=(*ICE, 200), width=5)
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    # Product labels
    d = ImageDraw.Draw(img)
    for lbl, fnt, col, dy in [
        ("AuraEase™", fb(52), WHITE,  -40),
        ("Hot & Cold Therapy", fr(30), ICE, 28),
    ]:
        bbox = d.textbbox((0, 0), lbl, font=fnt)
        tw   = bbox[2] - bbox[0]
        d.text(((W - tw) // 2, py_ + ph // 2 + dy), lbl, font=fnt, fill=col)

    # Particles (one composite pass)
    part_a = int(175 * min(1., t * 1.8))
    pov    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd     = ImageDraw.Draw(pov)
    for sx, sy, sp in SNOW:
        py2 = int(sy - t * sp) % H
        pd.text((sx, py2), "❄", font=fr(34), fill=(*ICE, part_a))
    for hx, hy, hp in HEAT:
        py2 = int(hy - t * hp) % H
        pd.text((hx, py2), "~", font=fb(38), fill=(225, 85, 45, int(part_a * 0.9)))
    img = Image.alpha_composite(img.convert("RGBA"), pov).convert("RGB")

    # Text slides up
    txt_slide = eo(t - 0.35, 0.65)
    txt_a     = eo(t - 0.35, 0.5)
    if txt_a > 0:
        yo = int((1 - txt_slide) * 195)
        img = put_text(img, "HOT & COLD",           py_ + ph + 85 + yo,  fb(92), NAVY, alpha=txt_a)
        img = put_text(img, "Therapy in one patch", py_ + ph + 195 + yo, fr(46), GRAY, alpha=txt_a)

    return np.array(img)


_BENS = [
    ("✔  Reusable 200+ times",        0.00),
    ("✔  Works in 30 seconds",         0.42),
    ("✔  Drug-free. No side effects.", 0.84),
]

def scene4(t):
    """8–11 s · dark navy · staggered benefit bullets · gold line sweep"""
    img    = Image.new("RGB", (W, H), NAVY)
    fade_a = min(1., t / 0.22)

    # Header
    h_a = eo(t, 0.4)
    if h_a > 0:
        img = put_text(img, "WHY AURAEASE?", 450, fb(50), GOLD, alpha=h_a * fade_a)
        lw  = int(SAFE_W * eo(t - 0.1, 0.5))
        if lw > 0:
            d = ImageDraw.Draw(img)
            d.line([((W - SAFE_W) // 2, 516),
                    ((W - SAFE_W) // 2 + lw, 516)], fill=GOLD, width=2)

    # Benefit lines
    spacing, base_y = 205, 720
    for i, (txt, delay) in enumerate(_BENS):
        lt = t - delay
        if lt < 0:
            continue
        slide = eo(lt, 0.42)
        dx    = int((1 - slide) * (-360))
        ta    = eo(lt, 0.38) * fade_a

        img = put_text(img, txt, base_y + i * spacing, fb(56), WHITE,
                       dx=dx, alpha=ta)

        # Gold glow on arrival (fades in 0.3 s)
        glow_a = max(0., 1 - lt / 0.32)
        if glow_a > 0 and slide > 0.55:
            glow_a *= (slide - 0.55) / 0.45
            img = put_glow(img, txt, base_y + i * spacing, fb(56),
                           WHITE, glow_col=GOLD, radius=16,
                           glow_a=glow_a * 0.55, txt_a=0)   # glow only

    # Gold bottom line sweep
    gl_t = t - 1.25
    if gl_t > 0:
        lw2 = int(W * eo(gl_t, 0.65))
        d2  = ImageDraw.Draw(img)
        d2.line([(0, 1680), (lw2, 1680)], fill=GOLD, width=4)

    return np.array(img)


def scene5(t):
    """11–15 s · navy→purple gradient · glow title · pulsing CTA · dots"""
    p   = min(1., t / 4.0)
    top = lerp_c(NAVY, PURPLE, p * 0.55)
    bot = lerp_c(NAVY, PURPLE, p)
    img = vgrad(top, bot)

    # Floating dots (one composite pass)
    dot_a = min(1., t * 0.6)
    dov   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd    = ImageDraw.Draw(dov)
    for dx_, dy_, sp, sz in DOTS:
        py2 = int(dy_ - t * sp) % H
        da  = int(70 * dot_a)
        dd.ellipse([dx_-sz, py2-sz, dx_+sz, py2+sz],
                   fill=(*WHITE, da))
    img = Image.alpha_composite(img.convert("RGBA"), dov).convert("RGB")

    # AuraEase title glow
    title_a = eo(t - 0.45, 1.1)
    if title_a > 0:
        img = put_glow(img, "AuraEase™", 660, fb(112),
                       WHITE, glow_col=WHITE, radius=28,
                       glow_a=title_a * 0.85, txt_a=title_a)

    # Subtitle
    sub_a = eo(t - 1.1, 0.75)
    if sub_a > 0:
        img = put_text(img, "Therapy & Relief  ✷", 805, fb(50), GOLD, alpha=sub_a)

    # Pulsing down-arrow + link
    arr_t = t - 1.75
    if arr_t > 0:
        arr_a   = eo(arr_t, 0.5)
        pulse   = 0.52 + 0.48 * math.sin(t * 2 * math.pi * 0.75)
        bob_y   = int(8 * math.sin(t * 2 * math.pi * 0.75))
        aov     = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        da      = ImageDraw.Draw(aov)
        ay      = 1080 + bob_y
        pts     = [(W//2-55, ay), (W//2+55, ay), (W//2, ay+75)]
        da.polygon(pts, fill=(*WHITE, int(210 * arr_a * pulse)))
        img = Image.alpha_composite(img.convert("RGBA"), aov).convert("RGB")

        link_a = arr_a * (0.58 + 0.42 * pulse)
        img    = put_text(img, "Link in bio", 1215, fr(48), WHITE, alpha=link_a)

    return np.array(img)


# ── Fade wrapper (0.2 s in/out per scene) ────────────────────────────────────
def wf(fn, dur, fd=0.20):
    def _f(t):
        frame = fn(t)
        if t < fd:
            a = t / fd
        elif t > dur - fd:
            a = max(0., (dur - t) / fd)
        else:
            a = 1.
        if a < 1.:
            frame = (frame.astype(float) * a).astype(np.uint8)
        return frame
    return _f


# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    clips = [
        VideoClip(wf(scene1, 2.5), duration=2.5),
        VideoClip(wf(scene2, 2.5), duration=2.5),
        VideoClip(wf(scene3, 3.0), duration=3.0),
        VideoClip(wf(scene4, 3.0), duration=3.0),
        VideoClip(wf(scene5, 4.0), duration=4.0),
    ]
    out = "auraease_tiktok_v2.mp4"
    concatenate_videoclips(clips).write_videofile(
        out, fps=FPS, codec="libx264", audio=False,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger="bar",
    )
    print(f"\n✔  {out}")


if __name__ == "__main__":
    build()
