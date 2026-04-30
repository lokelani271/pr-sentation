"""
make_kling_auraease.py — AuraEase TikTok video with Kling AI backgrounds
1. Generates 3 video clips via fal.ai Kling AI
2. Downloads the clips to tmp/
3. Composites AuraEase text overlays on each clip
4. Concatenates into final output/kling_auraease.mp4

Usage:
    FAL_KEY=your_key python3 make_kling_auraease.py
Or set FAL_KEY in .claude/settings.local.json and restart Claude Code.
"""
import os, sys, time, urllib.request
import numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, VideoClip
except ImportError:
    from moviepy import VideoFileClip, concatenate_videoclips, VideoClip

import fal_client

# ── Config ──────────────────────────────────────────────────────────────────
W, H, FPS = 1080, 1920, 30
NAVY  = (27,  42,  74)
WHITE = (255, 255, 255)
GOLD  = (197, 158,  80)
ICE   = (168, 216, 234)
MAX_TXT_W = W - 80

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]

# ── Kling AI prompts ─────────────────────────────────────────────────────────
KLING_CLIPS = [
    {
        "id": "pain",
        "prompt": (
            "Close-up of a muscular man's back, white athletic shirt, "
            "he winces and reaches back to touch a sore spot on his lower back. "
            "Bright gym background. Cinematic, 4K, shallow depth of field."
        ),
        "duration": 3,   # seconds
    },
    {
        "id": "patch",
        "prompt": (
            "Hands carefully peeling open a navy blue thermal patch package "
            "and applying it to bare skin. Clean white clinical background. "
            "Macro lens, soft lighting, product-reveal style."
        ),
        "duration": 4,
    },
    {
        "id": "relief",
        "prompt": (
            "Same man in a dark gym, now standing straight and smiling, "
            "a glowing navy blue patch visible on his lower back. "
            "Motivational tone, cinematic color grade, 4K."
        ),
        "duration": 4,
    },
]

# ── Text overlays per clip ───────────────────────────────────────────────────
# Each entry: list of (text, color, font_size, y_fraction, fade_in_s, fade_out_s)
OVERLAYS = {
    "pain": [
        ("Hate ice baths?",        WHITE, 100, 0.12, 0.3, 0.2),
        ("Same.",                  GOLD,  130, 0.25, 0.8, 0.2),
    ],
    "patch": [
        ("AURAEASE™",              GOLD,   80, 0.08, 0.1, 0.2),
        ("Dual Thermal Therapy",   WHITE,  75, 0.82, 0.2, 0.2),
        ("Hot + Cold. One patch.", ICE,    65, 0.89, 0.3, 0.2),
    ],
    "relief": [
        ("$35 for 200+ uses.",     WHITE, 85, 0.10, 0.2, 0.3),
        ("Link in bio 🔗",         GOLD,  80, 0.88, 0.5, 0.2),
    ],
}

# ── Font helpers ─────────────────────────────────────────────────────────────
@lru_cache(maxsize=32)
def fb(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def fit_font(text, max_size):
    size = max_size
    while size > 30:
        fnt = fb(size)
        bb = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=fnt)
        if bb[2] - bb[0] <= MAX_TXT_W:
            return fnt, size
        size -= 4
    return fb(30), 30

# ── Overlay renderer ─────────────────────────────────────────────────────────
def apply_overlays(frame_rgb, t, clip_id, clip_duration):
    img = Image.fromarray(frame_rgb).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    for (text, color, fs, y_frac, fi, fo) in OVERLAYS.get(clip_id, []):
        # Compute alpha
        alpha = 1.0
        if t < fi:
            alpha = t / fi
        if t > clip_duration - fo:
            alpha = max(0.0, (clip_duration - t) / fo)
        a = int(alpha * 255)

        fnt, _ = fit_font(text, fs)
        bb = d.textbbox((0, 0), text, font=fnt)
        tw = bb[2] - bb[0]
        x = (W - tw) // 2
        y = int(H * y_frac)
        r, g, b = color
        # Shadow
        d.text((x + 3, y + 3), text, font=fnt, fill=(0, 0, 0, int(a * 0.6)))
        d.text((x, y), text, font=fnt, fill=(r, g, b, a))

    # Watermark
    wfnt = fb(40)
    wtxt = "AURAEASE"
    wbb = d.textbbox((0, 0), wtxt, font=wfnt)
    wx = (W - (wbb[2] - wbb[0])) // 2
    d.text((wx, H - 110), wtxt, font=wfnt, fill=(255, 255, 255, 160))

    img.alpha_composite(overlay)
    return np.array(img.convert("RGB"))

# ── Kling AI generation ───────────────────────────────────────────────────────
def generate_kling_clip(clip_def, out_path):
    if os.path.exists(out_path):
        print(f"  [skip] {out_path} already exists")
        return

    print(f"  Generating '{clip_def['id']}' via Kling AI…")

    result = fal_client.subscribe(
        "fal-ai/kling-video/v1.6/standard/text-to-video",
        arguments={
            "prompt": clip_def["prompt"],
            "duration": str(clip_def["duration"]),
            "aspect_ratio": "9:16",
        },
        with_logs=True,
    )

    url = result["video"]["url"]
    print(f"  Downloading {url}")
    urllib.request.urlretrieve(url, out_path)
    print(f"  Saved → {out_path}")

# ── Build composited clip ────────────────────────────────────────────────────
def build_composited_clip(clip_def, raw_path):
    cid = clip_def["id"]
    clip = VideoFileClip(raw_path).resize((W, H))
    dur  = clip.duration

    def make_frame(t):
        frame = clip.get_frame(t)
        return apply_overlays(frame, t, cid, dur)

    return VideoClip(make_frame, duration=dur).set_fps(FPS)

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key or fal_key == "YOUR_FAL_KEY_HERE":
        print("ERROR: FAL_KEY not set.")
        print("Add it to .claude/settings.local.json under 'env' and restart,")
        print("or run:  FAL_KEY=your_key python3 make_kling_auraease.py")
        sys.exit(1)

    os.makedirs("tmp",    exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Step 1: Generate clips
    print("\n=== Step 1: Generating Kling AI clips ===")
    raw_paths = {}
    for cd in KLING_CLIPS:
        raw = f"tmp/kling_{cd['id']}.mp4"
        generate_kling_clip(cd, raw)
        raw_paths[cd["id"]] = raw

    # Step 2: Composite overlays
    print("\n=== Step 2: Compositing text overlays ===")
    composited = []
    for cd in KLING_CLIPS:
        print(f"  Processing '{cd['id']}'…")
        c = build_composited_clip(cd, raw_paths[cd["id"]])
        composited.append(c)

    # Step 3: Concatenate
    print("\n=== Step 3: Concatenating clips ===")
    final = concatenate_videoclips(composited, method="compose")
    out   = "output/kling_auraease.mp4"
    final.write_videofile(
        out, fps=FPS, codec="libx264", audio=False,
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p",
                       "-movflags", "+faststart", "-preset", "medium"],
        logger=None,
    )
    print(f"\nDone → {out}")

if __name__ == "__main__":
    main()
