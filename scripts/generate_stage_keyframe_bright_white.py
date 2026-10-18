"""Generate Live Stage Master Keyframe with Bright White Studio Lighting."""

from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from src.providers.fal_storage import _fal_api_key

BRIGHT_WHITE_PROMPT = (
    "Award-winning 4K live concert photograph of a strikingly beautiful South Indian woman (balanced fit build, mid-20s, graceful features), "
    "performing live on an intimate acoustic live session stage. "
    "She is singing into a vintage chrome stage condenser microphone on a stand, one hand gently touching the mic stand. "
    "Wardrobe: sleek elegant black ribbed-knit sleeveless halter top, delicate layered white gold necklace, subtle hoop earrings. "
    "Lighting: bright crisp neutral white studio key spotlight (5600K clean white lighting), beautifully illuminating her glowing, realistic clean skin tones and expressive eyes with sharp clarity. "
    "Background: cool deep indigo and blue ambient stage mood, soft-focus bokeh of an audience with gentle white rim lights, "
    "professional live broadcast television concert, 50mm f/1.4 portrait lens, crystal clear crisp photography, Lara Aredo concert aesthetic."
)

NEGATIVE_PROMPT = (
    "yellow tint, amber wash, golden hour flare, oversaturated orange, sepia tone, monochromatic yellow, "
    "muddy lighting, heavy grain, dark shadows, blurry face."
)


async def main():
    out_dir = Path("storage/tests/lofi_singer_test").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_img = out_dir / "live_stage_singer_bright_white.jpg"

    fal_key = _fal_api_key()
    if not fal_key:
        raise ValueError("FAL_KEY is not configured.")

    print("=====================================================================")
    print("🎤 Generating Master Stage Keyframe (Crisp Bright White Lighting)")
    print("💡 Lighting: 5600K Pure White Studio Spotlight + Deep Blue Ambient")
    print("💰 Cost: ~$0.025 (Flux Dev on Fal.ai)")
    print("=====================================================================\n")

    t0 = time.time()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": BRIGHT_WHITE_PROMPT,
        "negative_prompt": NEGATIVE_PROMPT,
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

        print("⏳ Rendering 4K stage keyframe on Fal GPU...")
        for _ in range(40):
            await asyncio.sleep(2.0)
            st_data = (await client.get(status_url, headers=headers)).json()
            if st_data.get("status") == "COMPLETED":
                res_data = (await client.get(response_url, headers=headers)).json()
                img_url = res_data["images"][0]["url"]
                img_bytes = (await client.get(img_url)).content
                out_img.write_bytes(img_bytes)
                break
            elif st_data.get("status") in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Flux task failed: {st_data}")

    elapsed = time.time() - t0
    size_kb = out_img.stat().st_size / 1024

    print("\n=====================================================================")
    print(f"✅ Bright White Keyframe Complete!")
    print(f"⏱️ Finished in {elapsed:.1f}s")
    print(f"📦 File Size: {size_kb:.1f} KB")
    print(f"🖼️ Local Path: {out_img}")
    print("=====================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
