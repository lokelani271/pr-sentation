"""
v5_1.mp4 — LEFT-ALIGNED three-tier: gold medium / white large / light blue medium
Reference: "30 SECONDS."(gold left) / "ZERO PAIN."(white left, bigger) / "START THE TIMER."(blue left)
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

PAD = 65  # left margin

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

def make_three_tier(
    gold_lines,  gold_size,
    white_lines, white_size,
    blue_lines,  blue_size,
    dur, gap1=16, gap2=80, fade_dur=0.30,
):
    """Left-aligned three-tier on navy background."""
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        a = int(alpha * 255)

        fnt_g = fb(gold_size)
        fnt_w = fb(white_size)
        fnt_b = fb(blue_size)
        lh_g = gold_size  + 16
        lh_w = white_size + 16
        lh_b = blue_size  + 16
        total_h = (len(gold_lines)*lh_g + gap1 +
                   len(white_lines)*lh_w + gap2 +
                   len(blue_lines)*lh_b)
        y = H // 2 - total_h // 2 - 30

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        for line in gold_lines:
            d.text((PAD, y), line, font=fnt_g, fill=(*GOLD, a)); y += lh_g
        y += gap1
        for line in white_lines:
            d.text((PAD, y), line, font=fnt_w, fill=(*WHITE, a)); y += lh_w
        y += gap2
        for line in blue_lines:
            d.text((PAD, y), line, font=fnt_b, fill=(*LIGHT_BLUE, a)); y += lh_b

        base = img.convert("RGBA")
        base.alpha_composite(overlay)
        img2 = draw_watermark(base, alpha=alpha)
        return np.array(img2.convert("RGB"))
    return VideoClip(frame, duration=dur)

scenes = [
    # s1 — reference: "30 SECONDS." / "ZERO PAIN." / "START THE TIMER."
    make_three_tier(
        ["30 SECONDS."], 175,
        ["ZERO PAIN."],  248,
        ["START THE TIMER."], 155,
        dur=2.5, gap1=14, gap2=85,
    ),
    # s2
    make_three_tier(
        ["FASTER THAN"], 165,
        ["ANY PILL."],   255,
        ["NO SIDE EFFECTS."], 148,
        dur=2.5, gap1=14, gap2=85,
    ),
    # s3
    make_three_tier(
        ["THERMAL"],       175,
        ["DUAL-ACTION."],  235,
        ["STARTS IMMEDIATELY."], 138,
        dur=3.0, gap1=14, gap2=85,
    ),
    # s4
    make_three_tier(
        ["FROM OUCH"], 165,
        ["TO AHHH."],  260,
        ["LINK IN BIO →"], 152,
        dur=2.0, gap1=14, gap2=85,
    ),
]

os.makedirs("output", exist_ok=True)
out = "output/v5_1.mp4"
concatenate_videoclips(scenes).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    logger=None,
)
print(f"\nDone → {out}")
