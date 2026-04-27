import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from functools import lru_cache
try:
    from moviepy.editor import VideoClip, concatenate_videoclips
except ImportError:
    from moviepy import VideoClip, concatenate_videoclips

W, H, FPS = 1080, 1920, 30
NAVY = (27, 42, 74)
GOLD = (201, 169, 110)
WHITE = (255, 255, 255)

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@lru_cache(maxsize=10)
def fb(sz): return ImageFont.truetype(_BOLD, sz)

_DD = ImageDraw.Draw(Image.new("RGB", (1,1)))

def _wrap(text, fnt, max_w=940):
    words, lines, line = text.split(), [], ""
    for w in words:
        c = f"{line} {w}".strip()
        if _DD.textbbox((0,0), c, font=fnt)[2] <= max_w: line = c
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines or [text]

def put_text(img, text, cy, fnt, color, alpha=1.0):
    lines  = _wrap(text, fnt)
    lh     = fnt.size + 16
    y0     = cy - len(lines) * lh // 2
    canvas = img.convert("RGBA")
    layer  = Image.new("RGBA", (W, H), (0,0,0,0))
    d      = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        bbox = d.textbbox((0,0), ln, font=fnt)
        x    = (W - (bbox[2]-bbox[0])) // 2
        d.text((x, y0 + i*lh), ln, font=fnt, fill=(*color, int(255*alpha)))
    return Image.alpha_composite(canvas, layer).convert("RGB")

def make_scene(text, color, dur, fade=0.3):
    def frame(t):
        img   = Image.new("RGB", (W, H), NAVY)
        alpha = min(t/fade, 1.0, (dur-t)/fade)
        img   = put_text(img, text, H//2, fb(108), color, alpha=alpha)
        return np.array(img)
    return VideoClip(frame, duration=dur)

scenes = [
    make_scene("$150 vs $35.\nYou choose.",              GOLD,  2.5),
    make_scene("Same problem.\nDifferent price.",         WHITE, 2.5),
    make_scene("Stop overpaying.\nManage your tension daily.", WHITE, 3.0),
    make_scene("The math is mathing.",                    GOLD,  2.0),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "v1_1_simple.mp4")
os.makedirs(os.path.dirname(out), exist_ok=True)
concatenate_videoclips(scenes).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf","18","-pix_fmt","yuv420p","-movflags","+faststart"],
    logger="bar"
)
print(f"\n✔  Saved → {out}")
