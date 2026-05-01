"""
generate_flux_backgrounds.py — Phase 2
Génère 4 backgrounds AI via fal.ai Flux Schnell (rapide + pas cher)
et les sauvegarde dans public/bg/ pour Remotion.

Usage:
    python3 generate_flux_backgrounds.py

FAL_KEY doit être dans .claude/settings.local.json ou dans l'environnement.
"""
import os, sys, urllib.request
import fal_client

FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY or FAL_KEY == "YOUR_FAL_KEY_HERE":
    print("ERROR: FAL_KEY non configurée.")
    print("Modifie .claude/settings.local.json et redémarre Claude Code.")
    sys.exit(1)

# ── Backgrounds à générer ────────────────────────────────────────────────────
BACKGROUNDS = [
    {
        "id":       "gym",
        "filename": "bg_gym.jpg",
        "prompt": (
            "Dark moody premium gym interior, cinematic lighting, "
            "deep navy blue and charcoal tones, dramatic shadows, "
            "no people, high-end photography, ultra sharp, "
            "vertical 9:16 format, editorial style"
        ),
    },
    {
        "id":       "product",
        "filename": "bg_product.jpg",
        "prompt": (
            "Minimalist product photography background, "
            "soft icy blue-white gradient, cool clinical aesthetic, "
            "subtle frosted glass texture, premium luxury feel, "
            "shallow depth of field, vertical 9:16 format"
        ),
    },
    {
        "id":       "split",
        "filename": "bg_split.jpg",
        "prompt": (
            "Abstract split composition: left side glowing molten orange-red fire energy, "
            "right side deep crystalline ice blue cool energy, "
            "meeting dramatically in the center with light burst, "
            "cinematic volumetric lighting, 4K, vertical 9:16 format"
        ),
    },
    {
        "id":       "victory",
        "filename": "bg_victory.jpg",
        "prompt": (
            "Athletic person silhouette standing tall in triumphant pose, "
            "warm golden backlight, bokeh gym background, "
            "motivational premium sports photography, "
            "cinematic color grade, vertical 9:16 format"
        ),
    },
]

# ── Génération ───────────────────────────────────────────────────────────────
os.makedirs("public/bg", exist_ok=True)

def generate(bg: dict):
    out_path = f"public/bg/{bg['filename']}"
    if os.path.exists(out_path):
        print(f"  [déjà présent] {out_path}")
        return

    print(f"  Génération '{bg['id']}'...")
    result = fal_client.subscribe(
        "fal-ai/flux/schnell",
        arguments={
            "prompt":               bg["prompt"],
            "image_size":           {"width": 768, "height": 1360},
            "num_inference_steps":  4,
            "num_images":           1,
            "enable_safety_checker": True,
        },
        with_logs=False,
    )
    url = result["images"][0]["url"]
    print(f"  Téléchargement...")
    urllib.request.urlretrieve(url, out_path)
    print(f"  ✓ Sauvegardé → {out_path}")

print("\n=== Génération des backgrounds Flux AI ===\n")
for bg in BACKGROUNDS:
    generate(bg)

print("\nTout est prêt. Lance 'npx remotion studio' pour prévisualiser.")
