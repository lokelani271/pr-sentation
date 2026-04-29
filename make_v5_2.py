"""
v5_2.mp4 — white bg, navy headline + gold punchline (two-block), AURAEASE watermark in navy
Reference: "WISH YOU HAD A" (navy large) / "RESET BUTTON?" (gold large)
"""
import os, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import VideoClip, concatenate_videoclips
except ImportError:
    from moviepy import VideoClip, concatenate_videoclips

W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255)
NAVY  = (27,  42,  74)
GOLD  = (197, 158,  80)

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
           fill=(*NAVY, int(alpha * 200)))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base

def make_two_block(top_lines, top_color, top_size,
                   bot_lines, bot_color, bot_size,
                   dur, gap=80, fade_dur=0.30):
    def frame(t):
        img = Image.new("RGB", (W, H), WHITE)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        a = int(alpha * 255)

        fnt_top = fb(top_size)
        fnt_bot = fb(bot_size)
        lh_top = top_size + 28
        lh_bot = bot_size + 28
        total_h = len(top_lines)*lh_top + gap + len(bot_lines)*lh_bot
        y = H // 2 - total_h // 2 - 50

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        for line in top_lines:
            bb = d.textbbox((0, 0), line, font=fnt_top)
            tw = bb[2] - bb[0]
            d.text(((W - tw) // 2, y), line, font=fnt_top,
                   fill=(*top_color, a))
            y += lh_top
        y += gap
        for line in bot_lines:
            bb = d.textbbox((0, 0), line, font=fnt_bot)
            tw = bb[2] - bb[0]
            d.text(((W - tw) // 2, y), line, font=fnt_bot,
                   fill=(*bot_color, a))
            y += lh_bot

        base = img.convert("RGBA")
        base.alpha_composite(overlay)
        img2 = draw_watermark(base, alpha=alpha)
        return np.array(img2.convert("RGB"))
    return VideoClip(frame, duration=dur)

scenes = [
    # s1 — reference layout
    make_two_block(
        ["WISH YOU", "HAD A"],  NAVY, 210,
        ["RESET BUTTON?"],      GOLD, 190,
        dur=2.5, gap=85,
    ),
    # s2
    make_two_block(
        ["IMAGINE", "PRESSING IT"],  NAVY, 200,
        ["ANYWHERE."],               GOLD, 210,
        dur=2.5, gap=85,
    ),
    # s3
    make_two_block(
        ["AURAEASE IS", "THE CLOSEST"], NAVY, 195,
        ["THING."],                     GOLD, 220,
        dur=3.0, gap=85,
    ),
    # s4
    make_two_block(
        ["PUSH"],          NAVY, 230,
        ["THE BUTTON."],   GOLD, 200,
        dur=2.0, gap=85,
    ),
]

os.makedirs("output", exist_ok=True)
out = "output/v5_2.mp4"
concatenate_videoclips(scenes).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    logger=None,
)
print(f"\nDone → {out}")
