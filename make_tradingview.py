"""
TradingView Promo  |  1080x1920  |  10s  |  30fps  |  no audio
Palette officielle TradingView : #131722 bg · #089981 green · #f23645 red · #2962ff blue
Brand intro → Graphique bougies animé → Features → CTA
"""

import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip, concatenate_videoclips
from functools import lru_cache

W, H   = 1080, 1920
FPS    = 30
SAFE_W = int(W * 0.88)

# ── Palette TradingView ───────────────────────────────────────────────────────
BG       = (19,  23,  34)    # #131722
BG2      = (30,  34,  45)    # #1e222d  chart panel
SURFACE  = (42,  46,  57)    # #2a2e39
GRID_C   = (54,  58,  69)    # #363a45
TV_GREEN = (8,   153, 129)   # #089981  bougie haussière
TV_RED   = (242, 54,  69)    # #f23645  bougie baissière
TV_BLUE  = (41,  98,  255)   # #2962ff  accent / CTA
TEXT     = (209, 212, 220)   # #d1d4dc  texte principal
DIM      = (120, 123, 134)   # #787b86  texte secondaire
WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

@lru_cache(maxsize=30)
def fb(sz): return ImageFont.truetype(_BOLD, sz)

@lru_cache(maxsize=30)
def fr(sz): return ImageFont.truetype(_REG, sz)

_DD = ImageDraw.Draw(Image.new("RGB", (1, 1)))

# ── Helpers ───────────────────────────────────────────────────────────────────
def eo(t, d):
    p = max(0., min(1., t / max(d, 1e-9)))
    return 1 - (1 - p) ** 3

def crossfade(a_img, b_img, alpha):
    a = np.array(a_img, dtype=float)
    b = np.array(b_img, dtype=float)
    return Image.fromarray((a * (1 - alpha) + b * alpha).astype(np.uint8))

def _wrap(text, fnt, max_w=None):
    max_w = max_w or SAFE_W
    words = text.split()
    lines, line = [], ""
    for w in words:
        c = f"{line} {w}".strip()
        if _DD.textbbox((0, 0), c, font=fnt)[2] <= max_w:
            line = c
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
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

def put_glow(img, text, cy, fnt, txt_col,
             glow_col=TV_BLUE, radius=32, glow_a=0.55, txt_a=1.0):
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

def ambient_glow(img, cx, cy, color, r_list, t_offset=0.0):
    """Pulsing ambient radial glow."""
    pulse = 0.85 + 0.15 * math.sin(t_offset * math.pi * 1.8)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for r, a in r_list:
        rr = int(r * pulse)
        lg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lg).ellipse(
            [(cx - rr, cy - rr), (cx + rr, cy + rr)],
            fill=(*color, int(255 * a))
        )
        lg = lg.filter(ImageFilter.GaussianBlur(rr // 3))
        layer = Image.alpha_composite(layer, lg)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

# ── Candlestick chart ─────────────────────────────────────────────────────────
# (open, high, low, close) — normalized 0→1, tendance haussière globale
CANDLES = [
    (0.38, 0.45, 0.34, 0.43),  # vert
    (0.43, 0.47, 0.36, 0.38),  # rouge
    (0.38, 0.49, 0.36, 0.47),  # vert
    (0.47, 0.51, 0.41, 0.44),  # rouge
    (0.44, 0.55, 0.42, 0.53),  # vert
    (0.53, 0.57, 0.47, 0.49),  # rouge
    (0.49, 0.61, 0.47, 0.59),  # vert
    (0.59, 0.64, 0.53, 0.55),  # rouge
    (0.55, 0.66, 0.53, 0.64),  # vert
    (0.64, 0.70, 0.61, 0.67),  # vert
    (0.67, 0.73, 0.60, 0.62),  # rouge
    (0.62, 0.74, 0.60, 0.72),  # vert
    (0.72, 0.80, 0.69, 0.78),  # vert
    (0.78, 0.83, 0.72, 0.74),  # rouge
    (0.74, 0.88, 0.72, 0.86),  # vert — dernier ATH
]
N  = len(CANDLES)

# Dimensions du panneau graphique
CX    = 56          # marge gauche
CW    = 930         # largeur zone bougies (100px réservés à droite pour labels)
CY    = 370         # y haut du graphique
CH    = 780         # hauteur zone bougies
VH    = 130         # hauteur volumes
CBOT  = CY + CH     # y bas zone bougies

def p2y(p, ymin=0.28, ymax=0.96):
    """Prix normalisé → pixel y (inversé)."""
    return int(CBOT - (p - ymin) / (ymax - ymin) * CH)

def draw_panel(img, alpha=1.0):
    """Fond panneau + quadrillage horizontal + labels y."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    # fond
    d.rectangle([(CX - 8, CY - 8), (CX + CW + 110, CBOT + VH + 16)],
                fill=(*BG2, int(255 * alpha)))
    # grille
    for lvl in [0.35, 0.45, 0.55, 0.65, 0.75, 0.85]:
        gy = p2y(lvl)
        if CY <= gy <= CBOT:
            d.line([(CX, gy), (CX + CW, gy)],
                   fill=(*GRID_C, int(255 * alpha * 0.6)), width=1)
            # label prix fictif
            price = int(170000 + (lvl - 0.28) / (0.96 - 0.28) * 60000)
            label = f"{price:,}".replace(",", " ")
            d.text((CX + CW + 8, gy - 10), label,
                   font=fr(20), fill=(*DIM, int(255 * alpha * 0.55)))
    # séparation volumes
    d.line([(CX, CBOT), (CX + CW, CBOT)],
           fill=(*GRID_C, int(255 * alpha * 0.4)), width=1)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_candles(img, n_vis, anim_frac=1.0, alpha=1.0):
    if n_vis == 0:
        return img
    cw  = CW // N
    bw  = max(4, int(cw * 0.60))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    for i in range(min(n_vis, N)):
        o, h, lo, c = CANDLES[i]
        frac   = anim_frac if i == n_vis - 1 else 1.0
        green  = c >= o
        col    = TV_GREEN if green else TV_RED
        col_a  = (*col, int(255 * alpha))
        cx_c   = CX + i * cw + cw // 2
        x0, x1 = cx_c - bw // 2, cx_c + bw // 2

        bt = p2y(max(o, c))
        bb = max(p2y(min(o, c)), bt + 2)
        # animation : corps grandit depuis le bas
        if frac < 1.0:
            full_h = bb - bt
            bt     = int(bb - full_h * frac)

        # mèches (uniquement quand bougie complète)
        if frac >= 0.85:
            wt = p2y(h)
            wb = p2y(lo)
            d.line([(cx_c, wt), (cx_c, bt)],    fill=col_a, width=2)
            d.line([(cx_c, bb), (cx_c, wb)],    fill=col_a, width=2)
        # corps
        d.rectangle([(x0, bt), (x1, bb)], fill=col_a)

        # volume
        vol_h = int((0.35 + 0.65 * abs(c - o) * 5) * VH * 0.85 * frac)
        vy0   = CBOT + VH - vol_h
        d.rectangle([(x0, vy0), (x1, CBOT + VH)],
                    fill=(*col, int(255 * alpha * 0.45)))

    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_ma(img, n_vis, alpha=1.0):
    """Moyenne mobile (période 3) en bleu TradingView."""
    if n_vis < 3:
        return img
    cw     = CW // N
    period = 3
    pts    = []
    for i in range(period - 1, min(n_vis, N)):
        avg = sum(CANDLES[j][3] for j in range(i - period + 1, i + 1)) / period
        pts.append((CX + i * cw + cw // 2, p2y(avg)))
    if len(pts) < 2:
        return img
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    for j in range(len(pts) - 1):
        d.line([pts[j], pts[j + 1]],
               fill=(*TV_BLUE, int(255 * alpha * 0.85)), width=3)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_last_line(img, last_close, alpha=1.0):
    """Ligne pointillée horizontale au dernier prix + badge."""
    y = p2y(last_close)
    if not (CY <= y <= CBOT):
        return img
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    # pointillés
    x = CX
    while x < CX + CW:
        d.line([(x, y), (min(x + 10, CX + CW), y)],
               fill=(*TV_GREEN, int(255 * alpha * 0.75)), width=1)
        x += 16
    # badge prix
    price = int(178600 + last_close * 1200)
    badge_txt = f"{price:,}".replace(",", " ")
    d.rounded_rectangle(
        [(CX + CW + 4, y - 14), (CX + CW + 108, y + 14)],
        radius=3, fill=(*TV_GREEN, int(255 * alpha))
    )
    d.text((CX + CW + 10, y - 11), badge_txt,
           font=fr(18), fill=(*WHITE, int(255 * alpha)))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def draw_ticker(img, t, alpha=1.0):
    """BTC/USD ticker animé au-dessus du graphique."""
    delta = 234 * math.sin(t * 1.7) + t * 38
    price = 178432.50 + delta
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d     = ImageDraw.Draw(layer)
    # Symbole
    d.text((CX, CY - 110), "BTC/USD",
           font=fb(34), fill=(*TEXT, int(255 * alpha)))
    # Prix
    d.text((CX, CY - 66),  f"{price:,.2f}",
           font=fb(44), fill=(*TV_GREEN, int(255 * alpha)))
    # Variation
    d.text((CX + 310, CY - 58), "+2.47%  ▲",
           font=fr(28), fill=(*TV_GREEN, int(255 * alpha * 0.9)))
    # Label MA
    d.text((CX + CW - 190, CY - 66), "MA(3)",
           font=fr(22), fill=(*TV_BLUE, int(255 * alpha * 0.8)))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

# ── Fade wrapper ──────────────────────────────────────────────────────────────
_BLK = Image.new("RGB", (W, H), BLACK)

def wf(fn, dur, fd=0.28):
    def frame(t):
        img = Image.fromarray(fn(t))
        if t < fd:
            img = crossfade(_BLK, img, max(0., t / fd))
        elif t > dur - fd:
            img = crossfade(_BLK, img, max(0., (dur - t) / fd))
        return np.array(img)
    return frame

# ──────────────────────────────────────────────────────────────────────────────
# SCÈNE 1 (0-2.5s): Intro marque — logo glow sur fond sombre
# ──────────────────────────────────────────────────────────────────────────────
def scene1(t):
    img = Image.new("RGB", (W, H), BG)

    # Lueur ambiante bleue pulsante
    a_glow = eo(t, 1.1)
    img = ambient_glow(img, W // 2, H // 2 - 90, TV_BLUE,
                       [(420, 0.04 * a_glow), (220, 0.08 * a_glow),
                        (100, 0.12 * a_glow)], t_offset=t)

    # Logo "TradingView"
    a_logo = eo(t, 0.75)
    img = put_glow(img, "TradingView",
                   H // 2 - 130, fb(96), WHITE,
                   glow_col=TV_BLUE, radius=44,
                   glow_a=0.48 * a_logo, txt_a=a_logo)

    # Ligne séparatrice bleue qui s'élargit
    if t >= 0.6:
        a_line = eo(t - 0.6, 0.55)
        hw     = int(200 * a_line)
        sep    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sep).rectangle(
            [(W // 2 - hw, H // 2 - 42), (W // 2 + hw, H // 2 - 38)],
            fill=(*TV_BLUE, int(255 * a_line))
        )
        img = Image.alpha_composite(img.convert("RGBA"), sep).convert("RGB")

    # Tagline principale
    if t >= 0.85:
        a_tag = eo(t - 0.85, 0.6)
        img = put_text(img, "Analysez. Tradez. Connectez.",
                       H // 2 + 10, fr(40), DIM, alpha=a_tag)

    # Sous-tagline
    if t >= 1.55:
        a_sub = eo(t - 1.55, 0.55)
        img = put_text(img, "La plateforme des traders professionnels",
                       H // 2 + 110, fr(29), DIM, alpha=a_sub * 0.65)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCÈNE 2 (2.5-6.5s, 4s): Graphique bougies japonaises animé
# ──────────────────────────────────────────────────────────────────────────────
def scene2(t):
    img = Image.new("RGB", (W, H), BG)

    a_hdr = eo(t, 0.40)
    img = put_text(img, "Graphiques en temps réel",
                   CY - 160, fb(48), WHITE, alpha=a_hdr)

    # Fond panneau
    img = draw_panel(img, alpha=eo(t, 0.35))

    # Animation bougies : 15 bougies en 3.2s
    interval  = 3.2 / N
    n_full    = int(t / interval)
    remainder = (t % interval) / interval
    n_vis     = min(n_full + 1, N)
    frac      = remainder if n_full < N else 1.0

    img = draw_candles(img, n_vis, frac)

    # Moyenne mobile (à partir de la 3e bougie)
    if n_vis >= 3:
        img = draw_ma(img, n_vis, alpha=min(1.0, (n_vis - 2) * 0.35))

    # Ligne dernier prix
    if n_vis >= N:
        a_last = eo(t - N * interval, 0.4)
        img = draw_last_line(img, CANDLES[-1][3], alpha=a_last)

    # Ticker BTC/USD
    img = draw_ticker(img, t, alpha=eo(t, 0.40))

    # Label bas
    if t >= 2.8:
        a_bot = eo(t - 2.8, 0.5)
        img = put_text(img, "100+ indicateurs techniques • Multiples timeframes",
                       CBOT + VH + 58, fr(27), DIM, alpha=a_bot * 0.75)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCÈNE 3 (6.5-8.5s, 2s): Features clés
# ──────────────────────────────────────────────────────────────────────────────
_FEATS = [
    ("★  +50 millions de traders actifs",          TEXT,    46, 0.10),
    ("■  Crypto · Forex · Actions · Indices",      DIM,     40, 0.65),
    ("●  Alertes, screener & paper trading",        TV_GREEN, 40, 1.20),
]
_FCY = [H // 2 - 185, H // 2 + 5, H // 2 + 195]

def scene3(t):
    img = Image.new("RGB", (W, H), BG)

    # Lueur verte subtile
    img = ambient_glow(img, W // 2, H // 2, TV_GREEN,
                       [(380, 0.03), (180, 0.05)], t_offset=t)

    a_ttl = eo(t, 0.40)
    img = put_text(img, "Tout en un seul endroit",
                   H // 2 - 360, fb(46), WHITE, alpha=a_ttl)

    for (text, color, sz, delay), cy in zip(_FEATS, _FCY):
        lt = t - delay
        if lt < 0:
            continue
        a  = eo(lt, 0.40)
        dx = int((1 - a) * -70)
        img = put_text(img, text, cy, fr(sz), color, alpha=a, dx=dx)

    return np.array(img)

# ──────────────────────────────────────────────────────────────────────────────
# SCÈNE 4 (8.5-10s, 1.5s): CTA — même bg que scène 1 (loop naturel)
# ──────────────────────────────────────────────────────────────────────────────
def scene4(t):
    img = Image.new("RGB", (W, H), BG)

    a_glow = eo(t, 0.7)
    img = ambient_glow(img, W // 2, H // 2 - 70, TV_BLUE,
                       [(380, 0.05 * a_glow), (190, 0.09 * a_glow)], t_offset=t)

    a1  = eo(t, 0.7)
    img = put_glow(img, "TradingView",
                   H // 2 - 115, fb(90), WHITE,
                   glow_col=TV_BLUE, radius=42,
                   glow_a=0.45 * a1, txt_a=a1)

    # Bouton CTA
    if t >= 0.35:
        a2   = eo(t - 0.35, 0.50)
        bw, bh = 560, 96
        bx   = W // 2 - bw // 2
        by   = H // 2 + 42
        btn  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(btn).rounded_rectangle(
            [(bx, by), (bx + bw, by + bh)],
            radius=10, fill=(*TV_BLUE, int(255 * a2))
        )
        img = Image.alpha_composite(img.convert("RGBA"), btn).convert("RGB")
        img = put_text(img, "Commencer gratuitement",
                       by + bh // 2, fb(36), WHITE, alpha=a2)

    # URL
    if t >= 0.85:
        a3 = eo(t - 0.85, 0.35)
        img = put_text(img, "tradingview.com",
                       H // 2 + 200, fr(28), DIM, alpha=a3 * 0.55)

    return np.array(img)

# ── BUILD ─────────────────────────────────────────────────────────────────────
def build():
    FD    = 0.28
    clips = [
        VideoClip(wf(scene1, 2.5, FD), duration=2.5),
        VideoClip(wf(scene2, 4.0, FD), duration=4.0),
        VideoClip(wf(scene3, 2.0, FD), duration=2.0),
        VideoClip(wf(scene4, 1.5, FD), duration=1.5),
    ]
    out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "tradingview_promo.mp4"
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
