"""
v5_1.mp4 — 11s, 4 scenes with crossfades
Hook (0-2s): GOLD stroke text
Scene1 (2-5s): WHITE, cut
Scene2 (5-9s): GOLD, crossfade 0.3s
Scene3 (9-11s): GOLD, crossfade 0.3s
"""
import os, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy import VideoClip

W, H, FPS   = 1080, 1920, 30
TOTAL       = 11.0
NAVY        = (27,  42,  74)
WHITE       = (255, 255, 255)
GOLD        = (197, 158,  80)
PAD         = 65
FADE_IN     = 0.20
XF          = 0.30   # crossfade duration

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

def render_scene(lines, color, font_size, alpha=1.0, stroke=False):
    """Left-aligned text block, vertically centered."""
    img = Image.new("RGB", (W, H), NAVY)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    fnt = fb(font_size)
    lh = font_size + 22
    total_h = len(lines) * lh
    y = H // 2 - total_h // 2 - 40
    a = int(alpha * 255)
    r, g, b = color
    for line in lines:
        if stroke:
            d.text((PAD, y), line, font=fnt,
                   fill=(r, g, b, a),
                   stroke_width=2,
                   stroke_fill=(255, 255, 255, a))
        else:
            d.text((PAD, y), line, font=fnt, fill=(r, g, b, a))
        y += lh
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return draw_watermark(base, alpha=alpha).convert("RGB")

# Scene content
SCENES = [
    # (lines, color, font_size, stroke, start, end)
    (["STOP THE PAIN", "IN 30 SECONDS."], GOLD,  120, True,  0.0, 2.0),
    (["FASTER THAN", "ANY PILL."],        WHITE, 110, False, 2.0, 5.0),
    (["THERMAL DUAL-ACTION", "STARTS IMMEDIATELY."], GOLD, 105, False, 5.0, 9.0),
    (["FROM OUCH", "TO AHHH."],           GOLD,  115, False, 9.0, 11.0),
]

def crossfade(a, b, alpha):
    return (a.astype(float) * (1 - alpha) + b.astype(float) * alpha).astype(np.uint8)

def make_frame(t):
    # Find current scene
    sc = 0
    for i, (_, _, _, _, start, end) in enumerate(SCENES):
        if start <= t < end:
            sc = i
            break
    else:
        sc = len(SCENES) - 1

    lines, color, fs, stroke, start, end = SCENES[sc]
    local_t  = t - start
    scene_dur = end - start

    # Alpha for this scene
    alpha = 1.0
    if sc == 0 and local_t < FADE_IN:      # hook fade-in
        alpha = local_t / FADE_IN
    if sc == len(SCENES) - 1:              # last scene fade-out
        alpha = min(1.0, (end - t) / 0.30)

    frame_a = np.array(render_scene(lines, color, fs, alpha=alpha, stroke=stroke))

    # Crossfade into next scene
    if sc < len(SCENES) - 1 and local_t >= (scene_dur - XF):
        xf_prog = (local_t - (scene_dur - XF)) / XF
        xf_prog = min(max(xf_prog, 0), 1)
        nlines, ncolor, nfs, nstroke, _, _ = SCENES[sc + 1]
        frame_b = np.array(render_scene(nlines, ncolor, nfs, alpha=1.0, stroke=nstroke))
        return crossfade(frame_a, frame_b, xf_prog)

    return frame_a

os.makedirs("output", exist_ok=True)
out = "output/v5_1.mp4"
VideoClip(make_frame, duration=TOTAL).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p",
                   "-movflags", "+faststart", "-preset", "medium"],
    logger=None,
)
print(f"\nDone → {out}")
