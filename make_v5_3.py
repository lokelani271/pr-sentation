"""
v5_3.mp4 — 11s, 4 scenes with crossfades
Hook (0-2s): WHITE + GOLD stroke
Scene1 (2-5s): ICE blue, cut
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

W, H, FPS = 1080, 1920, 30
TOTAL     = 11.0
NAVY      = (27,  42,  74)
WHITE     = (255, 255, 255)
GOLD      = (197, 158,  80)
ICE       = (168, 216, 234)
MAX_TXT_W = W - 80
FADE_IN   = 0.20
XF        = 0.30

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

def fit_font(line, max_size):
    size = max_size
    while size > 40:
        fnt = fb(size)
        bb = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), line, font=fnt)
        if bb[2] - bb[0] <= MAX_TXT_W:
            return fnt, size
        size -= 4
    return fb(40), 40

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

def render_scene(lines, color, font_size, alpha=1.0, stroke=False, stroke_color=WHITE):
    img = Image.new("RGB", (W, H), NAVY)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    a = int(alpha * 255)
    r, g, b = color

    fitted  = [fit_font(line, font_size) for line in lines]
    lh_list = [sz + 22 for _, sz in fitted]
    total_h = sum(lh_list)
    y = H // 2 - total_h // 2 - 40

    for (fnt, sz), lh, line in zip(fitted, lh_list, lines):
        bb = d.textbbox((0, 0), line, font=fnt)
        tw = bb[2] - bb[0]
        x  = (W - tw) // 2
        if stroke:
            sr, sg, sb = stroke_color
            d.text((x, y), line, font=fnt,
                   fill=(r, g, b, a),
                   stroke_width=3, stroke_fill=(sr, sg, sb, a))
        else:
            d.text((x, y), line, font=fnt, fill=(r, g, b, a))
        y += lh

    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return draw_watermark(base, alpha=alpha).convert("RGB")

SCENES = [
    (["HOT OR COLD?"],                     WHITE, 140, True,  GOLD,  0.0, 2.0),
    (["WHY NOT BOTH?"],                    ICE,   130, False, WHITE, 2.0, 5.0),
    (["DUAL THERMAL THERAPY.", "ONE PATCH."], GOLD, 110, False, WHITE, 5.0, 9.0),
    (["BEST OF BOTH WORLDS."],             GOLD,  110, False, WHITE, 9.0, 11.0),
]

def crossfade(a, b, alpha):
    return (a.astype(float) * (1 - alpha) + b.astype(float) * alpha).astype(np.uint8)

def make_frame(t):
    sc = 0
    for i, (*_, start, end) in enumerate(SCENES):
        if start <= t < end:
            sc = i
            break
    else:
        sc = len(SCENES) - 1

    lines, color, fs, stroke, scol, start, end = SCENES[sc]
    local_t   = t - start
    scene_dur = end - start

    alpha = 1.0
    if sc == 0 and local_t < FADE_IN:
        alpha = local_t / FADE_IN
    if sc == len(SCENES) - 1:
        alpha = min(1.0, (end - t) / 0.30)

    frame_a = np.array(render_scene(lines, color, fs, alpha=alpha,
                                    stroke=stroke, stroke_color=scol))

    if sc < len(SCENES) - 1 and local_t >= (scene_dur - XF):
        xf_prog = min(max((local_t - (scene_dur - XF)) / XF, 0), 1)
        nlines, ncolor, nfs, nstroke, nscol, _, _ = SCENES[sc + 1]
        frame_b = np.array(render_scene(nlines, ncolor, nfs, alpha=1.0,
                                        stroke=nstroke, stroke_color=nscol))
        return crossfade(frame_a, frame_b, xf_prog)

    return frame_a

os.makedirs("output", exist_ok=True)
out = "output/v5_3.mp4"
VideoClip(make_frame, duration=TOTAL).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p",
                   "-movflags", "+faststart", "-preset", "medium"],
    logger=None,
)
print(f"\nDone → {out}")
