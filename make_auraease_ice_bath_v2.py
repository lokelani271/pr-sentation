"""
auraease_ice_bath_v2.mp4 — 10s, 3 Kling-faithful backgrounds + caption overlays
Backgrounds painted from Kling AI reference images visible in conversation:
  Scene 1: man's back, white shirt, beige gym
  Scene 2: hands applying navy patch, clean white bg
  Scene 3: man in dark gym holding knee, red pain glow
"""
import os, math, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy import VideoClip

W, H, FPS = 1080, 1920, 30
TOTAL = 10.0
XF    = 0.30

NAVY  = (27,  42,  74)
GOLD  = (201, 169, 110)
WHITE = (255, 255, 255)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

@lru_cache(maxsize=32)
def fb(size, bold=True):
    for p in (FONT_PATHS if bold else FONT_REG):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

MAX_W = W - 120

def fit_font(txt, max_size, bold=True):
    size = max_size
    while size > 28:
        fnt = fb(size, bold)
        bb = ImageDraw.Draw(Image.new("RGBA",(1,1))).textbbox((0,0),txt,font=fnt)
        if bb[2]-bb[0] <= MAX_W: return fnt, size
        size -= 3
    return fb(28, bold), 28

def draw_text(d, txt, y, color, max_size, bold=True, alpha=255):
    fnt, sz = fit_font(txt, max_size, bold)
    bb = d.textbbox((0,0), txt, font=fnt)
    x = (W-(bb[2]-bb[0]))//2
    r,g,b = color
    d.text((x, y), txt, font=fnt, fill=(r,g,b,alpha))

# ══════════════════════════════════════════════════════════════════════
# BACKGROUND 1 — Man's back, white t-shirt, beige gym (kling_pain)
# ══════════════════════════════════════════════════════════════════════
def make_bg1():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # Beige/cream gradient background
    for y in range(H):
        t = y / H
        r = int(232 - 18*t)
        g = int(224 - 16*t)
        b = int(210 - 18*t)
        d.line([(0,y),(W,y)], fill=(r,g,b))

    # Gym floor (darker strip at bottom)
    for y in range(int(H*0.82), H):
        t = (y - H*0.82) / (H*0.18)
        c = int(60 + 30*t)
        d.line([(0,y),(W,y)], fill=(c, c-2, c-5))

    # Background gym equipment — blurry dark shapes left
    eq = Image.new("RGBA",(W,H),(0,0,0,0))
    eq_d = ImageDraw.Draw(eq)
    # Vertical rack left
    eq_d.rectangle([60, int(H*0.18), 100, int(H*0.78)], fill=(80,75,72,180))
    eq_d.rectangle([60, int(H*0.18), 200, int(H*0.22)], fill=(80,75,72,180))
    # Vertical rack right
    eq_d.rectangle([W-120, int(H*0.22), W-80, int(H*0.72)], fill=(90,85,82,140))
    blurred_eq = eq.filter(ImageFilter.GaussianBlur(radius=8))
    img.paste(Image.fromarray(np.array(img)), mask=None)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(blurred_eq)
    img = img_rgba.convert("RGB")
    d = ImageDraw.Draw(img)

    # Skin-colored neck
    neck_cx = W//2
    d.ellipse([neck_cx-55, int(H*0.12), neck_cx+55, int(H*0.28)],
              fill=(210, 170, 140))

    # Dark hair
    d.ellipse([neck_cx-145, int(H*0.05), neck_cx+145, int(H*0.20)],
              fill=(28, 22, 18))
    # Hair highlight
    d.ellipse([neck_cx-80, int(H*0.055), neck_cx+40, int(H*0.12)],
              fill=(45, 36, 30))

    # White t-shirt body (large rounded rectangle)
    shirt_left  = int(W*0.12)
    shirt_right = int(W*0.88)
    shirt_top   = int(H*0.20)
    shirt_bot   = int(H*0.68)
    d.rounded_rectangle([shirt_left, shirt_top, shirt_right, shirt_bot],
                        radius=90, fill=(248, 248, 248))

    # Shirt collar opening (small ellipse at top center)
    d.ellipse([neck_cx-80, shirt_top-10, neck_cx+80, shirt_top+80],
              fill=(240, 240, 240))

    # Shirt fabric shadow/crease lines
    crease = Image.new("RGBA",(W,H),(0,0,0,0))
    cd = ImageDraw.Draw(crease)
    mid_y = int(H*0.48)
    cd.line([(W//2-60, mid_y-80),(W//2+80, mid_y+60)], fill=(200,200,200,80), width=6)
    cd.line([(W//2-90, mid_y+20),(W//2+40, mid_y+120)], fill=(200,200,200,60), width=4)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(crease)
    img = img_rgba.convert("RGB")
    d = ImageDraw.Draw(img)

    # Left sleeve
    d.ellipse([int(W*0.04), int(H*0.26), int(W*0.22), int(H*0.46)],
              fill=(246, 246, 246))
    # Right sleeve
    d.ellipse([int(W*0.78), int(H*0.26), int(W*0.96), int(H*0.46)],
              fill=(246, 246, 246))

    # Left arm skin below sleeve
    d.ellipse([int(W*0.05), int(H*0.40), int(W*0.19), int(H*0.65)],
              fill=(205, 168, 138))
    # Right arm skin
    d.ellipse([int(W*0.81), int(H*0.40), int(W*0.95), int(H*0.65)],
              fill=(205, 168, 138))

    # Blue shorts at bottom
    d.rectangle([int(W*0.14), int(H*0.66), int(W*0.86), H],
                fill=(40, 80, 160))

    # Ceiling recessed lights
    for lx in [int(W*0.22), int(W*0.78)]:
        d.ellipse([lx-45, 20, lx+45, 65], fill=(255, 250, 235))
        glow = Image.new("RGBA",(W,H),(0,0,0,0))
        gd = ImageDraw.Draw(glow)
        for r in [90, 60, 35]:
            ga = int(40 * (35/(r+1)))
            gd.ellipse([lx-r, 20-r//2, lx+r, 65+r//2], fill=(255,248,220,min(ga,120)))
        img_rgba = img.convert("RGBA")
        img_rgba.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12)))
        img = img_rgba.convert("RGB")

    return img.filter(ImageFilter.GaussianBlur(radius=0.6))

# ══════════════════════════════════════════════════════════════════════
# BACKGROUND 2 — Hands applying navy patch (kling_patch)
# ══════════════════════════════════════════════════════════════════════
def make_bg2():
    img = Image.new("RGB", (W, H), (250, 248, 246))
    d = ImageDraw.Draw(img)

    # Very soft vignette edges
    vig = Image.new("RGBA",(W,H),(0,0,0,0))
    vd  = ImageDraw.Draw(vig)
    for r in range(700, 300, -30):
        a = int(8 * (700-r)/400)
        vd.ellipse([(W//2-r, H//2-r),(W//2+r, H//2+r)], outline=(180,175,170,a), width=30)
    img.paste(img, mask=None)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(vig)
    img = img_rgba.convert("RGB")
    d = ImageDraw.Draw(img)

    SKIN = (225, 185, 155)
    SKIN_D = (200, 160, 128)

    # The LEG — large diagonal ellipse center of frame
    cx, cy = W//2 + 30, H//2 + 60
    leg_w, leg_h = 340, 900
    angle_img = Image.new("RGBA",(W,H),(0,0,0,0))
    ad = ImageDraw.Draw(angle_img)
    ad.ellipse([cx-leg_w//2, cy-leg_h//2, cx+leg_w//2, cy+leg_h//2],
               fill=(*SKIN, 255))
    # Rotate leg slightly
    rotated = angle_img.rotate(-18, center=(cx, cy), expand=False)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(rotated)
    img = img_rgba.convert("RGB")
    d = ImageDraw.Draw(img)

    # Navy patch — star/cross shape centered on leg
    px, py = cx - 40, cy - 100
    patch_size = 190
    # Draw as overlapping rectangles (cross/plus shape)
    d.rectangle([px - patch_size//3, py - patch_size//2,
                 px + patch_size//3, py + patch_size//2],
                fill=(28, 48, 100))
    d.rectangle([px - patch_size//2, py - patch_size//3,
                 px + patch_size//2, py + patch_size//3],
                fill=(28, 48, 100))
    # Rounded corners to soften
    d.ellipse([px-40, py-100, px+40, py-20], fill=(28,48,100))
    d.ellipse([px-40, py+20,  px+40, py+100], fill=(28,48,100))
    d.ellipse([px-100,py-40, px-20, py+40], fill=(28,48,100))
    d.ellipse([px+20, py-40, px+100,py+40], fill=(28,48,100))

    # TOP HAND — coming from upper right, fingers pointing down-left
    h1 = Image.new("RGBA",(W,H),(0,0,0,0))
    h1d = ImageDraw.Draw(h1)
    # Palm
    h1d.ellipse([px-60, py-260, px+200, py-80], fill=(*SKIN, 255))
    # Fingers
    finger_data = [
        (px+130, py-320, px+165, py-180),
        (px+70,  py-350, px+110, py-190),
        (px+10,  py-340, px+55,  py-185),
        (px-45,  py-300, px+0,   py-170),
    ]
    for fx1,fy1,fx2,fy2 in finger_data:
        h1d.ellipse([fx1,fy1,fx2,fy2], fill=(*SKIN,255))
        h1d.ellipse([fx1,fy1+20,fx2,fy1+50], fill=(*SKIN_D,200))  # knuckle
    h1_blurred = h1.filter(ImageFilter.GaussianBlur(radius=1.5))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(h1_blurred)
    img = img_rgba.convert("RGB")

    # BOTTOM HAND — coming from lower left, fingers pointing up-right
    h2 = Image.new("RGBA",(W,H),(0,0,0,0))
    h2d = ImageDraw.Draw(h2)
    h2d.ellipse([px-220, py+100, px+60, py+280], fill=(*SKIN,255))
    finger_data2 = [
        (px-250, py+120, px-205, py+260),
        (px-200, py+80,  px-155, py+230),
        (px-145, py+60,  px-95,  py+210),
        (px-85,  py+70,  px-35,  py+220),
    ]
    for fx1,fy1,fx2,fy2 in finger_data2:
        h2d.ellipse([fx1,fy1,fx2,fy2], fill=(*SKIN,255))
    h2_blurred = h2.filter(ImageFilter.GaussianBlur(radius=1.5))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(h2_blurred)
    img = img_rgba.convert("RGB")

    return img

# ══════════════════════════════════════════════════════════════════════
# BACKGROUND 3 — Man in dark gym, red knee pain glow (kling_relief)
# ══════════════════════════════════════════════════════════════════════
def make_bg3():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # Very dark background gradient (charcoal → near black)
    for y in range(H):
        t = y / H
        r = int(30 - 12*t)
        g = int(28 - 10*t)
        b = int(32 - 12*t)
        d.line([(0,y),(W,y)], fill=(max(r,8), max(g,8), max(b,8)))

    # Gym rack silhouette (right background)
    rack = Image.new("RGBA",(W,H),(0,0,0,0))
    rd = ImageDraw.Draw(rack)
    # Vertical uprights
    rd.rectangle([int(W*0.55), int(H*0.02), int(W*0.60), int(H*0.70)],
                 fill=(40,38,36,220))
    rd.rectangle([int(W*0.78), int(H*0.02), int(W*0.83), int(H*0.70)],
                 fill=(40,38,36,200))
    # Cross bars
    rd.rectangle([int(W*0.55), int(H*0.12), int(W*0.83), int(H*0.17)],
                 fill=(45,43,40,200))
    rd.rectangle([int(W*0.55), int(H*0.30), int(W*0.83), int(H*0.34)],
                 fill=(45,43,40,180))
    rd.rectangle([int(W*0.55), int(H*0.48), int(W*0.83), int(H*0.52)],
                 fill=(45,43,40,160))
    blurred_rack = rack.filter(ImageFilter.GaussianBlur(radius=3))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(blurred_rack)
    img = img_rgba.convert("RGB")

    # Reflective floor
    for y in range(int(H*0.80), H):
        t = (y - H*0.80) / (H*0.20)
        c = int(22 + 15*t)
        d = ImageDraw.Draw(img)
        d.line([(0,y),(W,y)], fill=(c, c-2, c+2))

    # Bench (dark rectangle)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([int(W*0.18), int(H*0.70), int(W*0.72), int(H*0.76)],
                        radius=12, fill=(35, 32, 30))

    # MAN FIGURE — dark clothing, seated, hunched forward
    # Torso (dark shirt)
    d.ellipse([int(W*0.20), int(H*0.28), int(W*0.65), int(H*0.60)],
              fill=(18, 17, 16))
    d.rectangle([int(W*0.22), int(H*0.40), int(W*0.63), int(H*0.70)],
                fill=(18, 17, 16))

    # Head (dark hair, leaning forward)
    d.ellipse([int(W*0.32), int(H*0.15), int(W*0.60), int(H*0.32)],
              fill=(28, 22, 18))

    # Neck / face (skin, slightly turned)
    d.ellipse([int(W*0.37), int(H*0.26), int(W*0.56), int(H*0.38)],
              fill=(165, 128, 100))

    # Right leg (extending forward, dark shorts/pants)
    d.ellipse([int(W*0.28), int(H*0.60), int(W*0.60), int(H*0.82)],
              fill=(20, 18, 16))
    # Shin / lower leg (skin tone)
    d.ellipse([int(W*0.25), int(H*0.72), int(W*0.52), int(H*0.92)],
              fill=(155, 118, 90))

    # Arms reaching down to knee
    d.ellipse([int(W*0.22), int(H*0.48), int(W*0.40), int(H*0.75)],
              fill=(18, 17, 16))
    d.ellipse([int(W*0.35), int(H*0.55), int(W*0.55), int(H*0.78)],
              fill=(18, 17, 16))
    # Hands (skin)
    d.ellipse([int(W*0.24), int(H*0.70), int(W*0.46), int(H*0.83)],
              fill=(160, 122, 95))

    # Shoe (black sneaker)
    d.rounded_rectangle([int(W*0.18), int(H*0.88), int(W*0.50), int(H*0.95)],
                        radius=18, fill=(15, 13, 12))
    # Yellow accent on shoe
    d.rectangle([int(W*0.22), int(H*0.920), int(W*0.28), int(H*0.940)],
                fill=(200, 160, 20))

    # Dumbbell on floor
    d.ellipse([int(W*0.62), int(H*0.88), int(W*0.72), int(H*0.94)],
              fill=(30, 28, 26))
    d.rectangle([int(W*0.62), int(H*0.90), int(W*0.75), int(H*0.92)],
                fill=(35, 32, 30))
    d.ellipse([int(W*0.72), int(H*0.88), int(W*0.80), int(H*0.94)],
              fill=(30, 28, 26))

    # RED / ORANGE PAIN GLOW at knee area
    glow = Image.new("RGBA",(W,H),(0,0,0,0))
    gd = ImageDraw.Draw(glow)
    kx, ky = int(W*0.36), int(H*0.775)
    for r in [160, 110, 70, 40, 20]:
        ga = int(180 * (20/(r+5)))
        gd.ellipse([kx-r, ky-r//2, kx+r, ky+r//2],
                   fill=(220, 60, 15, min(ga, 230)))
    blurred_glow = glow.filter(ImageFilter.GaussianBlur(radius=18))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(blurred_glow)

    # Second dumbbell reflection on floor
    img = img_rgba.convert("RGB")
    d = ImageDraw.Draw(img)

    return img

# Pre-render all 3 backgrounds once
print("Rendering backgrounds...")
BG1 = make_bg1()
BG2 = make_bg2()
BG3 = make_bg3()
print("Backgrounds done.")

# ── Text helpers ─────────────────────────────────────────────────────

def dark_overlay(img, strength=0.45):
    dark = Image.new("RGBA",(W,H),(0,0,0,int(strength*255)))
    base = img.convert("RGBA")
    base.alpha_composite(dark)
    return base.convert("RGB")

def make_overlay(bg, texts, strength=0.45):
    """bg: PIL Image; texts: list of (txt, y, color, size, bold, alpha)"""
    base = dark_overlay(bg, strength)
    ov = Image.new("RGBA",(W,H),(0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for txt, y, color, size, bold, alpha in texts:
        draw_text(d, txt, y, color, size, bold=bold, alpha=int(alpha*255))
    base.paste(ov.convert("RGB"), mask=ov.split()[3])
    return np.array(base)

# ── Scene functions ──────────────────────────────────────────────────

def scene1(t, dur=3.0):
    a1 = min(t/0.30, 1.0)
    a2 = min(max(t-0.20,0)/0.30, 1.0)
    return make_overlay(BG1, [
        ("Hate ice baths?", 150, WHITE, 80, True,  a1),
        ("Same.",           268, WHITE, 95, True,  a2),
    ], strength=0.38)

def scene2(t, dur=4.0):
    a1 = min(t/0.30, 1.0)
    a2 = min(max(t-0.20,0)/0.30, 1.0)
    a3 = min(max(t-0.40,0)/0.30, 1.0)
    return make_overlay(BG2, [
        ("Targeted cold therapy",       150,  WHITE, 65, True,  a1),
        ("without the freeze. \U0001f9ca", 258, GOLD,  60, True,  a2),
        ("$35 for 200+ uses.",          1600, WHITE, 52, False, a3),
    ], strength=0.18)

def scene3(t, dur=3.0):
    fo = min((dur-t)/0.30, 1.0)
    a1 = min(t/0.30, 1.0) * fo
    a2 = min(max(t-0.20,0)/0.30, 1.0) * fo
    a3 = min(max(t-0.40,0)/0.30, 1.0) * fo
    return make_overlay(BG3, [
        ("Recover smarter.",  150,  WHITE, 82, True,  a1),
        ("AuraEase™",    800,  GOLD,  90, True,  a2),
        ("Link in bio \U0001f517", 1700, WHITE, 50, False, a3),
    ], strength=0.40)

# ── Master frame / crossfade ─────────────────────────────────────────

CUT       = [0.0, 3.0, 7.0, 10.0]
SCENE_FNS = [scene1, scene2, scene3]
SCENE_DUR = [3.0, 4.0, 3.0]

def crossfade(a, b, alpha):
    return (a.astype(float)*(1-alpha)+b.astype(float)*alpha).astype(np.uint8)

def make_frame(t):
    sc = max(i for i,c in enumerate(CUT[:-1]) if c <= t)
    local_t   = t - CUT[sc]
    scene_dur = SCENE_DUR[sc]
    frame_a   = SCENE_FNS[sc](local_t, scene_dur)
    if sc < len(SCENE_FNS)-1 and local_t >= scene_dur - XF:
        xf = min(max((local_t-(scene_dur-XF))/XF, 0), 1)
        frame_b = SCENE_FNS[sc+1](0.0, SCENE_DUR[sc+1])
        return crossfade(frame_a, frame_b, xf)
    return frame_a

os.makedirs("output", exist_ok=True)
out = "output/auraease_ice_bath_v2.mp4"
VideoClip(make_frame, duration=TOTAL).write_videofile(
    out, fps=FPS, codec="libx264", audio=False,
    ffmpeg_params=["-crf","18","-pix_fmt","yuv420p",
                   "-movflags","+faststart","-preset","medium"],
    logger=None,
)
print(f"\nDone → {out}")
