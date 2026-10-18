"""Regenerate scene_02.jpg with clean unadorned shirt and slim medium curvy woman."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from src.providers.fal_storage import _fal_api_key

SCENE_02_PROMPT = (
    "Paved European lakeside stone promenade flanked by tall deep-green cypress trees and vibrant blooming bougainvillea. "
    "A strikingly beautiful South Indian woman (mid-20s, graceful SLIM build with balanced medium feminine curves, healthy natural fit proportions, gentle defined waistline, cute dimpled smile, wearing a flowy emerald green midi dress with subtle waist tie, dainty earrings, delicate gold wrist bracelet, and stylish strap sandals) "
    "and a handsome South Indian man (athletic fit build, clean plain ivory linen button-down shirt with rolled sleeves, completely plain unadorned shirt front with zero badges or pins, navy tailored chinos) "
    "strolling side by side along the stone pier overlooking sparkling crystal clear lake waters. Authentic 35mm film photography, crisp natural daylight, photorealistic skin textures."
)

async def main():
    target_img = Path(
        r"C:\neel-1\projects\content-generation\storage\user-knpillutla-gmail-com\networks\telugu_rhythms\music_video\chigurinche_premala\ep-001\scenes\scene_02.jpg"
    )
    backup_img = target_img.with_name("scene_02_backup_chest_badge.jpg")
    if target_img.exists() and not backup_img.exists():
        backup_img.write_bytes(target_img.read_bytes())
        print(f"[i] Backed up old badge image to {backup_img.name}")

    fal_key = _fal_api_key()
    if not fal_key:
        raise ValueError("FAL_KEY is not configured.")

    print("Rendering updated scene_02.jpg with Flux Dev on Fal.ai...")
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": SCENE_02_PROMPT,
        "image_size": "landscape_16_9",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post("https://queue.fal.run/fal-ai/flux/dev", headers=headers, json=payload)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Flux submit failed: {resp.text}")

        data = resp.json()
        status_url = data.get("status_url")
        response_url = data.get("response_url")

        for _ in range(40):
            await asyncio.sleep(2.0)
            st_resp = await client.get(status_url, headers=headers)
            st_data = st_resp.json()
            if st_data.get("status") == "COMPLETED":
                break

        res_resp = await client.get(response_url, headers=headers)
        res_data = res_resp.json()
        img_url = res_data["images"][0]["url"]

        img_data = await client.get(img_url)
        target_img.write_bytes(img_data.content)
        print(f"[+] Successfully wrote regenerated image: {target_img} ({len(img_data.content)/1024:.1f} KB)")

if __name__ == "__main__":
    asyncio.run(main())
