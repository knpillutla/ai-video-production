"""Regenerate scene_03.jpg with 4-zone accessories, slender/curvy build, and strict anatomical watch placement."""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from src.core.config import settings
from src.providers.fal_storage import _fal_api_key

SCENE_03_PROMPT = (
    "Intricate classical stone pergola draped in cascading purple and green wisteria blossoms overlooking deep sapphire lake waters. "
    "A strikingly beautiful South Indian woman (age 24, healthy medium build with natural feminine curves, healthy natural proportions, neither skinny nor thin, cute warm dimpled smile, hair styled half-up with a delicate gold pin, delicate gold chain necklace, dainty gold earrings, slender gold bangles on wrist, wearing an emerald green linen dress) "
    "standing beside a handsome South Indian man (age 26, athletic medium build, clean plain ivory linen button-down shirt with rolled sleeves, unadorned plain shirt front, navy tailored trousers). "
    "Authentic 35mm film photography, crisp morning daylight, photorealistic natural skin texture."
)


async def main():
    target_img = Path(
        r"C:\neel-1\projects\content-generation\storage\user-knpillutla-gmail-com\networks\telugu_rhythms\music_video\chigurinche_premala\ep-001\scenes\scene_03.jpg"
    )
    backup_img = target_img.with_name("scene_03_backup_watch_gaffe.jpg")
    if target_img.exists() and not backup_img.exists():
        backup_img.write_bytes(target_img.read_bytes())
        print(f"[i] Backed up old gaffe image to {backup_img.name}")

    fal_key = _fal_api_key()
    if not fal_key:
        raise ValueError("FAL_KEY is not configured.")

    print(f"Rendering updated scene_03.jpg with Flux Dev on Fal.ai...")
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": SCENE_03_PROMPT,
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
            st_data = (await client.get(status_url, headers=headers)).json()
            if st_data.get("status") == "COMPLETED":
                res_data = (await client.get(response_url, headers=headers)).json()
                img_url = res_data["images"][0]["url"]
                img_bytes = (await client.get(img_url)).content
                target_img.write_bytes(img_bytes)
                print(f"[+] Successfully wrote regenerated image: {target_img} ({len(img_bytes)/1024:.1f} KB)")
                break
            elif st_data.get("status") in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Flux task failed: {st_data}")


if __name__ == "__main__":
    asyncio.run(main())
