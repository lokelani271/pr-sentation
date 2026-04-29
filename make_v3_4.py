"""
v3_4.mp4 — navy bg, word-split headline (white headline + gold punch word) + small subtitle
Reference: "THE RECOVERY" (white large) / "GAP." (gold large) / "CLOSE IT FOR $35." (white small)
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
WHITE = (255, 255, 255)
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
           fill=(255, 255, 255, int(alpha * 180)))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base

def make_split_scene(top_lines, gold_line, subtitle, dur, fade_dur=0.30,
                     big_size=225, sub_size=62, gap_mid=20, gap_sub=100):
    """
    top_lines  — white, big
    gold_line  — gold, big (same size, directly below top_lines)
    subtitle   — white, small, with larger gap below the gold line
    """
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        a = int(alpha * 255)

        fnt_big = fb(big_size)
        fnt_sub = fb(sub_size)
        lh_big  = big_size + 20

        n_big = len(top_lines) + 1  # +1 for gold line
        total_h = n_big * lh_big + gap_sub + sub_size + 20
        y = H // 2 - total_h // 2 - 40

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        # White headline lines
        for line in top_lines:
            bb = d.textbbox((0, 0), line, font=fnt_big)
            tw = bb[2] - bb[0]
            d.text(((W - tw) // 2, y), line, font=fnt_big,
                   fill=(*WHITE, a))
            y += lh_big

        # Gold punch word/line
        bb = d.textbbox((0, 0), gold_line, font=fnt_big)
        tw = bb[2] - bb[0]
        d.text(((W - tw) // 2, y), gold_line, font=fnt_big,
               fill=(*GOLD, a))
        y += lh_big + gap_sub

        # Small white subtitle
        if subtitle:
            bb = d.textbbox((0, 0), subtitle, font=fnt_sub)
            tw = bb[2] - bb[0]
            d.text(((W - tw) // 2, y), subtitle, font=fnt_sub,
                   fill=(*WHITE, a))

        base = img.convert("RGBA")
        base.alpha_composite(overlay)
        img2 = draw_watermark(base, alpha=alpha)
        return np.array(img2.convert("RGB"))
    return VideoClip(frame, duration=dur)

def make_single(lines, color, size, dur, fade_dur=0.30):
    def frame(t):
        img = Image.new("RGB", (W, H), NAVY)
        alpha = min(t / fade_dur, 1.0, (dur - t) / fade_dur)
        a = int(alpha * 255)
        fnt = fb(size)
        lh = size + 20
        total_h = len(lines) * lh
        y = H // 2 - total_h // 2 - 40
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for line in lines:
            bb = d.textbbox((0, 0), line, font=fnt)
            tw = bb[2] - bb[0]
            d.text(((W - tw) // 2, y), line, font=fnt, fill=(*color, a))
            y += lh
        base = img.convert("RGBA")
        base.alpha_composite(overlay)
        img2 = draw_watermark(base, alpha=alpha)
        return np.array(img2.convert("RGB"))
    return VideoClip(frame, duration=dur)

scenes = [
    # s1 — "THE RECOVERY / GAP." / "CLOSE IT FOR $35."
    make_split_scene(
        top_lines=["THE", "RECOVERY"],
        gold_line="GAP.",
        subtitle="CLOSE IT FOR $35.",
        dur=2.5,
    ),
    # s2 — "PRE-WORKOUT? / YES." / "RECOVERY? SKIPPED."
    make_split_scene(
        top_lines=["PRE-WORKOUT?"],
        gold_line="YES.",
        subtitle="RECOVERY? SKIPPED.",
        dur=2.5,
        big_size=220, sub_size=65,
    ),
    # s3 — "EVERYTHING / YOU NEED." / "FOR $35."
    make_split_scene(
        top_lines=["EVERYTHING", "YOU NEED."],
        gold_line="$35.",
        subtitle="ONE TIME. ZERO SUBSCRIPTION.",
        dur=3.0,
        big_size=210, sub_size=55,
    ),
    # s4 — CTA
    make_split_scene(
        top_lines=["JOIN"],
        gold_line="THE CLUB.",
        subtitle="LINK IN BIO →",
        dur=2.0,
        big_size=230, sub_size=60,
    ),
]

os.makedirs("output", exist_ok=True)
out = "output/v3_4.mp4"
concatenate_videoclips(scenes).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    logger=None,
)
print(f"\nDone → {out}")
