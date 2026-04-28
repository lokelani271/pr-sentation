import os, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import VideoClip, concatenate_videoclips
except ImportError:
    from moviepy import VideoClip, concatenate_videoclips

W, H, FPS = 1080, 1920, 30
NAVY  = (27, 42, 74)
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

def put_text(img, lines, cy, fnt, color, alpha=1.0):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    line_h = fnt.size + 22
    total_h = len(lines) * line_h
    y = cy - total_h // 2
    for line in lines:
        bb = d.textbbox((0, 0), line, font=fnt)
        tw = bb[2] - bb[0]
        x = (W - tw) // 2
        r, g, b = color
        d.text((x, y), line, font=fnt, fill=(r, g, b, int(alpha * 255)))
        y += line_h
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")

def make_scene(lines, color, dur, fade_dur=0.30):
    fnt = fb(95)
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        return np.array(put_text(img, lines, H // 2, fnt, color, alpha=alpha))
    return VideoClip(frame, duration=dur)

scenes = [
    make_scene(["Can't walk after", "leg day?"],                    WHITE, 2.5),
    make_scene(["Stairs becoming", "your worst enemy."],            WHITE, 2.5),
    make_scene(["Accelerate recovery", "with thermal duality."],    GOLD,  3.0),
    make_scene(["Don't skip recovery."],                            GOLD,  2.0),
]

os.makedirs("output", exist_ok=True)
out = "output/v3_1.mp4"
concatenate_videoclips(scenes).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    logger=None,
)
print(f"\nDone → {out}")
