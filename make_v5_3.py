"""
v5_3.mp4 — HOT(gold) + +(white) + COLD(light blue) + WHY CHOOSE?(white) layout
"""
import os, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import VideoClip, concatenate_videoclips
except ImportError:
    from moviepy import VideoClip, concatenate_videoclips

W, H, FPS = 1080, 1920, 30
NAVY       = (27,  42,  74)
WHITE      = (255, 255, 255)
GOLD       = (197, 158,  80)
LIGHT_BLUE = (135, 195, 230)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]

@lru_cache(maxsize=16)
def fb(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_watermark(img, alpha=1.0):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    fnt = fb(42)
    txt = "AURAEASE"
    bb = d.textbbox((0, 0), txt, font=fnt)
    tw = bb[2] - bb[0]
    d.text(((W - tw) // 2, H - 120), txt, font=fnt,
           fill=(255, 255, 255, int(alpha * 180)))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base

def centered_text(d, txt, fnt, y, color, a):
    bb = d.textbbox((0, 0), txt, font=fnt)
    tw = bb[2] - bb[0]
    d.text(((W - tw) // 2, y), txt, font=fnt, fill=(*color, a))
    return bb[3] - bb[1]

def make_hot_cold_scene(dur, fade_dur=0.30):
    """Reference layout: HOT / + / COLD / (gap) / WHY CHOOSE?"""
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        a = int(alpha * 255)

        fnt_big  = fb(230)
        fnt_plus = fb(160)
        fnt_sub  = fb(155)

        lh_big  = 230 + 10
        lh_plus = 160 + 10
        lh_sub  = 155 + 10
        gap     = 70

        total_h = lh_big + lh_plus + lh_big + gap + lh_sub
        y = H // 2 - total_h // 2 - 60

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        centered_text(d, "HOT",         fnt_big,  y,          GOLD,       a); y += lh_big
        centered_text(d, "+",           fnt_plus, y,          WHITE,      a); y += lh_plus
        centered_text(d, "COLD",        fnt_big,  y,          LIGHT_BLUE, a); y += lh_big + gap
        centered_text(d, "WHY CHOOSE?", fnt_sub,  y,          WHITE,      a)

        base = img.convert("RGBA")
        base.alpha_composite(overlay)
        img2 = draw_watermark(base, alpha=alpha)
        return np.array(img2.convert("RGB"))
    return VideoClip(frame, duration=dur)

def make_three_tier(gold_lines, gold_size, white_lines, white_size,
                    blue_lines, blue_size, dur, gap1=16, gap2=80, fade_dur=0.30):
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        a = int(alpha * 255)

        fnt_g = fb(gold_size)
        fnt_w = fb(white_size)
        fnt_b = fb(blue_size)
        lh_g = gold_size + 16
        lh_w = white_size + 16
        lh_b = blue_size  + 16
        total_h = len(gold_lines)*lh_g + gap1 + len(white_lines)*lh_w + gap2 + len(blue_lines)*lh_b
        y = H // 2 - total_h // 2 - 30

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        for line in gold_lines:
            centered_text(d, line, fnt_g, y, GOLD,  a); y += lh_g
        y += gap1
        for line in white_lines:
            centered_text(d, line, fnt_w, y, WHITE, a); y += lh_w
        y += gap2
        for line in blue_lines:
            centered_text(d, line, fnt_b, y, LIGHT_BLUE, a); y += lh_b

        base = img.convert("RGBA")
        base.alpha_composite(overlay)
        img2 = draw_watermark(base, alpha=alpha)
        return np.array(img2.convert("RGB"))
    return VideoClip(frame, duration=dur)

def make_two_block(top_lines, top_color, top_size,
                   bot_lines, bot_color, bot_size,
                   dur, gap=80, fade_dur=0.30):
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        a = int(alpha * 255)
        fnt_t = fb(top_size)
        fnt_b = fb(bot_size)
        lh_t = top_size + 20
        lh_b = bot_size + 20
        total_h = len(top_lines)*lh_t + gap + len(bot_lines)*lh_b
        y = H // 2 - total_h // 2 - 40
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for line in top_lines:
            centered_text(d, line, fnt_t, y, top_color, a); y += lh_t
        y += gap
        for line in bot_lines:
            centered_text(d, line, fnt_b, y, bot_color, a); y += lh_b
        base = img.convert("RGBA")
        base.alpha_composite(overlay)
        img2 = draw_watermark(base, alpha=alpha)
        return np.array(img2.convert("RGB"))
    return VideoClip(frame, duration=dur)

scenes = [
    # s1 — reference layout: HOT + COLD / WHY CHOOSE?
    make_hot_cold_scene(dur=2.5),
    # s2 — "WHY NOT / BOTH?" with light blue punchline
    make_two_block(
        ["WHY NOT"], WHITE,      210,
        ["BOTH?"],   LIGHT_BLUE, 240,
        dur=2.5, gap=80,
    ),
    # s3 — three-tier: gold stat / white main / blue subtitle
    make_three_tier(
        ["DUAL THERMAL"],  170,
        ["ONE PATCH."],    250,
        ["STARTS IN 30s."], 145,
        dur=3.0, gap1=14, gap2=85,
    ),
    # s4 — CTA
    make_two_block(
        ["BEST OF"],       GOLD,  220,
        ["BOTH WORLDS."],  WHITE, 210,
        dur=2.0, gap=75,
    ),
]

os.makedirs("output", exist_ok=True)
out = "output/v5_3.mp4"
concatenate_videoclips(scenes).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    logger=None,
)
print(f"\nDone → {out}")
