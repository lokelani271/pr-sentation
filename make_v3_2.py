"""
v3_2.mp4 — oversized bold style, light blue hooks + gold CTA, AURAEASE watermark
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
GOLD       = (201, 169, 110)
LIGHT_BLUE = (135, 195, 230)   # sky-blue accent matching reference

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

def draw_centered(img, lines, color, font_size, alpha=1.0, cy_offset=0):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    fnt = fb(font_size)
    line_h = font_size + 24
    total_h = len(lines) * line_h
    y = H // 2 - total_h // 2 + cy_offset

    r, g, b = color
    a = int(alpha * 255)
    for line in lines:
        bb = d.textbbox((0, 0), line, font=fnt)
        tw = bb[2] - bb[0]
        x = (W - tw) // 2
        d.text((x, y), line, font=fnt, fill=(r, g, b, a))
        y += line_h

    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base

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

def make_scene(lines, color, dur, font_size=220, cy_offset=0, fade_dur=0.30):
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        img = draw_centered(img, lines, color, font_size, alpha=alpha,
                            cy_offset=cy_offset)
        img = draw_watermark(img, alpha=alpha)
        return np.array(img.convert("RGB"))
    return VideoClip(frame, duration=dur)

def make_two_block_scene(top_lines, top_color, top_size,
                         bot_lines, bot_color, bot_size,
                         dur, gap=60, fade_dur=0.30):
    """Two separate text blocks stacked with a gap — matches 'SKIP THE ICE BATH. / $35.' layout."""
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)

        fnt_top = fb(top_size)
        fnt_bot = fb(bot_size)
        lh_top = top_size + 24
        lh_bot = bot_size + 24
        total_h = len(top_lines)*lh_top + gap + len(bot_lines)*lh_bot
        y = H // 2 - total_h // 2 - 40

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        a = int(alpha * 255)

        for line in top_lines:
            r, g, b = top_color
            bb = d.textbbox((0, 0), line, font=fnt_top)
            tw = bb[2] - bb[0]
            d.text(((W - tw) // 2, y), line, font=fnt_top, fill=(r, g, b, a))
            y += lh_top
        y += gap
        for line in bot_lines:
            r, g, b = bot_color
            bb = d.textbbox((0, 0), line, font=fnt_bot)
            tw = bb[2] - bb[0]
            d.text(((W - tw) // 2, y), line, font=fnt_bot, fill=(r, g, b, a))
            y += lh_bot

        base = img.convert("RGBA")
        base.alpha_composite(overlay)
        img = base
        img = draw_watermark(img, alpha=alpha)
        return np.array(img.convert("RGB"))
    return VideoClip(frame, duration=dur)

scenes = [
    make_scene(["HATE ICE", "BATHS?", "SAME."],            LIGHT_BLUE, 2.5, font_size=200),
    make_scene(["SMARTER", "WAY TO", "RECOVER."],          LIGHT_BLUE, 2.5, font_size=200),
    # Reference-style: "SKIP THE ICE BATH." over "$35."
    make_two_block_scene(
        ["SKIP THE", "ICE BATH."], LIGHT_BLUE, 210,
        ["$35."],                  GOLD,       220,
        dur=3.0, gap=70,
    ),
    make_scene(["RECOVER", "SMARTER."],                    GOLD,       2.0, font_size=220),
]

os.makedirs("output", exist_ok=True)
out = "output/v3_2.mp4"
concatenate_videoclips(scenes).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    logger=None,
)
print(f"\nDone → {out}")
