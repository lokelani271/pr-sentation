"""
AuraEase TikTok video generator — MoviePy + Pillow
Output: auraease_tiktok_video1.mp4  |  1080x1920  |  12s  |  30fps  |  no audio
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, concatenate_videoclips

# ── Constants ────────────────────────────────────────────────────────────────
W, H = 1080, 1920
FPS  = 30

NAVY       = (27,  42,  74)
WHITE      = (255, 255, 255)
OFF_WHITE  = (230, 230, 230)
LIGHT_GRAY = (170, 170, 180)
DARK_GRAY  = (70,  70,  80)
ACCENT     = (90,  180, 220)   # soft blue for CTA line

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SAFE_W = int(W * 0.82)   # 80 % safe zone = 885 px

# ── Helpers ───────────────────────────────────────────────────────────────────

def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, size)


def ease_out(t: float, duration: float) -> float:
    p = max(0.0, min(1.0, t / duration))
    return 1 - (1 - p) ** 3          # cubic ease-out


def blend_black(img: Image.Image, alpha: float) -> Image.Image:
    """Fade image from black by blending with alpha."""
    if alpha >= 1.0:
        return img
    arr = (np.array(img, dtype=float) * alpha).astype(np.uint8)
    return Image.fromarray(arr)


def wrap_text(text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Wrap text to fit within max_w pixels."""
    dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words = text.split()
    lines, line = [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if dummy_draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_w:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines or [text]


def draw_text_block(
    img: Image.Image,
    text: str,
    center_y: int,
    size: int,
    color: tuple,
    x_shift: int = 0,
    alpha: float = 1.0,
):
    """
    Draw a (possibly wrapped) text block centered at center_y.
    x_shift > 0 → shift rightwards (for slide-in from right).
    alpha → per-text transparency via RGBA compositing.
    """
    fnt   = font(size)
    lines = wrap_text(text, fnt, SAFE_W)
    lh    = size + 10
    total = len(lines) * lh
    y0    = center_y - total // 2

    draw_on = img.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d       = ImageDraw.Draw(overlay)

    for i, ln in enumerate(lines):
        bbox = d.textbbox((0, 0), ln, font=fnt)
        tw   = bbox[2] - bbox[0]
        x    = (W - tw) // 2 + x_shift
        y    = y0 + i * lh
        rgba = (*color[:3], int(255 * alpha))
        d.text((x, y), ln, font=fnt, fill=rgba)

    return Image.alpha_composite(draw_on, overlay).convert("RGB")


# ── Scene factories ───────────────────────────────────────────────────────────

def scene1(t: float) -> np.ndarray:
    """0-2 s │ Fade in │ Dark navy │ OLD WAY ❄"""
    a   = ease_out(t, 0.5)
    img = Image.new("RGB", (W, H), NAVY)
    img = draw_text_block(img, "OLD WAY  ❄",     H // 2 - 70, 90, WHITE,      alpha=a)
    img = draw_text_block(img, "Messy. Cold. Annoying.", H // 2 + 60, 44, LIGHT_GRAY, alpha=a)
    return np.array(img)


def scene2(t: float) -> np.ndarray:
    """2-5 s │ Slide in from right │ White bg │ NEW WAY ★"""
    slide   = ease_out(t, 0.55)
    x_shift = int((1 - slide) * W)          # W → 0 as slide → 1

    img = Image.new("RGB", (W, H), WHITE)
    img = draw_text_block(img, "NEW WAY  ★",                    H // 2 - 70, 90, NAVY,      x_shift=x_shift)
    img = draw_text_block(img, "Clean. Dual action. Reusable 200x.", H // 2 + 60, 40, DARK_GRAY, x_shift=x_shift)
    return np.array(img)


def scene3(t: float) -> np.ndarray:
    """5-8 s │ Fade in │ Dark navy │ Hot & Cold Therapy"""
    a   = ease_out(t, 0.5)
    img = Image.new("RGB", (W, H), NAVY)
    img = draw_text_block(img, "Hot & Cold Therapy",            H // 2 - 80,  85, WHITE,      alpha=a)
    img = draw_text_block(img, "No mess. No appointments.",     H // 2 + 50,  44, LIGHT_GRAY, alpha=a)
    img = draw_text_block(img, "Just relief.",                  H // 2 + 120, 44, LIGHT_GRAY, alpha=a)
    return np.array(img)


_BULLETS = [
    ("✔  Reusable 200+ times", 0.0),
    ("✔  Instant relief",       0.5),
    ("✔  Drug-free",            1.0),
]

def scene4(t: float) -> np.ndarray:
    """8-10 s │ 3 bullets fade in 0.5 s apart │ White bg"""
    img    = Image.new("RGB", (W, H), WHITE)
    gap    = 130
    base_y = H // 2 - gap

    for i, (text, delay) in enumerate(_BULLETS):
        local_t = t - delay
        if local_t < 0:
            continue
        a   = ease_out(local_t, 0.4)
        img = draw_text_block(img, text, base_y + i * gap, 56, NAVY, alpha=a)

    return np.array(img)


def scene5(t: float) -> np.ndarray:
    """10-12 s │ Gentle fade in │ Dark navy │ AuraEase™ CTA"""
    a   = ease_out(t, 0.8)
    img = Image.new("RGB", (W, H), NAVY)
    img = draw_text_block(img, "AuraEase™",         H // 2 - 120, 100, WHITE,      alpha=a)
    img = draw_text_block(img, "Therapy & Relief ✿", H // 2 +  20,  46, LIGHT_GRAY, alpha=a)
    img = draw_text_block(img, "Link in bio  →",     H // 2 + 180,  42, ACCENT,     alpha=a)
    return np.array(img)


# ── Build ─────────────────────────────────────────────────────────────────────

def build():
    clips = [
        VideoClip(scene1, duration=2),   # 0–2 s
        VideoClip(scene2, duration=3),   # 2–5 s
        VideoClip(scene3, duration=3),   # 5–8 s
        VideoClip(scene4, duration=2),   # 8–10 s
        VideoClip(scene5, duration=2),   # 10–12 s
    ]

    output = os.path.join(os.path.dirname(__file__), "auraease_tiktok_video1.mp4")

    final = concatenate_videoclips(clips)
    final.write_videofile(
        output,
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger="bar",
    )
    print(f"\n✔  Saved → {output}")


if __name__ == "__main__":
    build()
