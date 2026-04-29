"""
v3_1.mp4 — oversized bold TikTok style matching reference image
Large gold/white text that dominates the frame, "AURAEASE" watermark bottom center
"""
import os, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import VideoClip, concatenate_videoclips
except ImportError:
    from moviepy import VideoClip, concatenate_videoclips

W, H, FPS = 1080, 1920, 30
NAVY  = (27,  42,  74)
GOLD  = (201, 169, 110)
WHITE = (255, 255, 255)

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

def draw_oversized(img, lines, color, alpha=1.0, font_size=215, x_offset=-30):
    """
    Draw large bold text — each line stacked, left-biased so it bleeds off right edge.
    Lines are vertically centered as a block.
    """
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    fnt = fb(font_size)
    line_h = font_size + 18
    total_h = len(lines) * line_h
    y = H // 2 - total_h // 2 - 80  # sit slightly above center like reference

    r, g, b = color
    a = int(alpha * 255)

    for line in lines:
        # Left-biased: start from x_offset so long text bleeds right
        d.text((x_offset, y), line, font=fnt, fill=(r, g, b, a))
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
    x = (W - tw) // 2
    y = H - 120
    d.text((x, y), txt, font=fnt, fill=(255, 255, 255, int(alpha * 180)))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base

def make_scene(lines, color, dur, fade_dur=0.30, font_size=215, x_offset=-30):
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        img = draw_oversized(img, lines, color, alpha=alpha,
                             font_size=font_size, x_offset=x_offset)
        img = draw_watermark(img, alpha=alpha)
        return np.array(img.convert("RGB"))
    return VideoClip(frame, duration=dur)

scenes = [
    # Hook scenes — white, tight 2-word lines for max impact
    make_scene(["CAN'T WALK", "AFTER", "LEG DAY?"],       WHITE, 2.5, font_size=185, x_offset=-20),
    make_scene(["STAIRS:", "YOUR WORST", "ENEMY."],        WHITE, 2.5, font_size=185, x_offset=-20),
    # Product scenes — gold
    make_scene(["LEG DAY", "HACK"],                        GOLD,  3.0, font_size=230, x_offset=-25),
    make_scene(["DON'T SKIP", "RECOVERY."],                GOLD,  2.0, font_size=200, x_offset=-20),
]

os.makedirs("output", exist_ok=True)
out = "output/v3_1.mp4"
concatenate_videoclips(scenes).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    logger=None,
)
print(f"\nDone → {out}")
