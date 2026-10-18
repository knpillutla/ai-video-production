"""Regenerate scene_03.jpg using FalZImageAdapter (Z-Image Turbo) matching scene 01 and scene 02."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.providers.visual.fal_zimage import FalZImageAdapter

SCENE_03_PROMPT = (
    "Intricate classical stone pergola draped in cascading purple and green wisteria blossoms overlooking deep sapphire lake waters. "
    "A strikingly cute, stylish, and exceptionally beautiful 24-year-old South Indian woman (gorgeous delicate features, slightly slender oval face with subtle defined cheekbones, radiant caramel skin, sparkling expressive eyes, cute dimpled smile, styled wavy dark hair with delicate gold pins, graceful medium-slim build with gentle feminine curves and a defined trimmer waistline, wearing a chic tailored sleeveless emerald green midi dress with a fitted waist, delicate gold drop earrings, dainty layered necklace, and slender gold bangles) "
    "standing close beside a handsome South Indian man (athletic fit build, clean plain ivory linen button-down shirt with rolled sleeves, unadorned plain shirt front, navy trousers) as they share a tender, affectionate romantic glance. "
    "Warm natural morning sunlight, 35mm cinematic photograph, authentic skin textures, stylish high-fashion candid romantic editorial."
)

async def main():
    target_img = Path(
        r"C:\neel-1\projects\content-generation\storage\user-knpillutla-gmail-com\networks\telugu_rhythms\music_video\chigurinche_premala\ep-001\scenes\scene_03.jpg"
    )
    backup_img = target_img.with_name("scene_03_backup_flux.jpg")
    if target_img.exists():
        backup_img.write_bytes(target_img.read_bytes())

    # Calculate the exact seed matching vocal_image_service
    # song_seed = abs(hash("4c12bbf9-2d22-4dc1-a620-32da6b3d7869")) % 100000
    # scene_seed = (song_seed + 3 * 7919) % 1000000
    song_seed = abs(hash("4c12bbf9-2d22-4dc1-a620-32da6b3d7869")) % 100000
    scene_seed = (song_seed + 3 * 7919) % 1000000

    print(f"Generating scene_03 with FalZImageAdapter (Z-Image Turbo) seed={scene_seed}...")
    adapter = FalZImageAdapter()
    
    # Remove existing file so generate_to_file doesn't hit artifact cache
    target_img.unlink(missing_ok=True)
    
    url, path = await adapter.generate_to_file(
        prompt=SCENE_03_PROMPT,
        output_path=target_img,
        aspect_ratio="16:9",
        force_live=True,
        seed=scene_seed,
    )
    print(f"[+] Successfully generated scene_03.jpg via Z-Image Turbo: {path} ({path.stat().st_size/1024:.1f} KB)")

if __name__ == "__main__":
    asyncio.run(main())
