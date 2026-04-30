"""
script_5_1_final.mp4 — 12s, Ken Burns zoom on "30 SECONDS. / ZERO PAIN. / START THE TIMER."
Programmatic frame generation + slow zoom (1.0→1.04), fade in/out, no audio
"""
import os, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy import VideoClip

W, H, FPS = 1080, 1920, 30
DURATION   = 12.0
NAVY       = (27,  42,  74)
WHITE      = (255, 255, 255)
GOLD       = (197, 158,  80)
LIGHT_BLUE = (135, 195, 230)
PAD        = 65

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

def build_base_frame(scale=1.10):
    """Render at scale× size so Ken Burns crop never shows border."""
    sw, sh = int(W * scale), int(H * scale)
    img = Image.new("RGB", (sw, sh), NAVY)

    fnt_g = fb(int(175 * scale))
    fnt_w = fb(int(248 * scale))
    fnt_b = fb(int(155 * scale))

    lh_g = int(175 * scale) + int(16 * scale)
    lh_w = int(248 * scale) + int(16 * scale)
    lh_b = int(155 * scale) + int(16 * scale)
    gap1 = int(14  * scale)
    gap2 = int(85  * scale)
    pad  = int(PAD * scale)

    total_h = lh_g + gap1 + lh_w + gap2 + lh_b
    y = sh // 2 - total_h // 2 - int(30 * scale)

    overlay = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    d.text((pad, y), "30 SECONDS.", font=fnt_g, fill=(*GOLD,  255)); y += lh_g + gap1
    d.text((pad, y), "ZERO PAIN.", font=fnt_w,  fill=(*WHITE, 255)); y += lh_w + gap2
    d.text((pad, y), "START THE TIMER.", font=fnt_b, fill=(*LIGHT_BLUE, 255))

    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    base = draw_watermark(base)
    return base.convert("RGB")

# Pre-render at 1.10× — max zoom is 1.04, so 1.10 gives enough headroom
BASE = build_base_frame(scale=1.10)
BASE_W, BASE_H = BASE.size

def crop_center(img, cw, ch):
    x = (img.width  - cw) // 2
    y = (img.height - ch) // 2
    return img.crop((x, y, x + cw, y + ch))

FADE = 0.3

def make_frame(t):
    # Ken Burns: zoom 1.0 → 1.04 over duration
    zoom   = 1.0 + 0.04 * (t / DURATION)
    # crop size at current zoom (relative to original W×H)
    cw = int(W / zoom)
    ch = int(H / zoom)
    # scale crop coords to BASE dimensions (which are 1.10× the original)
    scale_factor = BASE_W / W  # = 1.10
    cw_base = int(cw * scale_factor)
    ch_base = int(ch * scale_factor)
    cropped = crop_center(BASE, cw_base, ch_base)
    frame   = cropped.resize((W, H), Image.LANCZOS)

    # Fade in / out
    alpha = min(t / FADE, 1.0, (DURATION - t) / FADE)
    if alpha < 1.0:
        black = Image.new("RGB", (W, H), (0, 0, 0))
        frame = Image.blend(black, frame, alpha)

    return np.array(frame)

os.makedirs("output", exist_ok=True)
out = "output/script_5_1_final.mp4"
VideoClip(make_frame, duration=DURATION).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p",
                   "-movflags", "+faststart", "-preset", "medium"],
    logger=None,
)
print(f"\nDone → {out}")
