"""Generate Master Stage Keyframe: Cute & Modern South Indian Singer in Stylish Punjabi Dress."""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from src.providers.fal_storage import _fal_api_key

PUNJABI_DRESS_PROMPT = (
    "Award-winning 4K live concert photograph of a strikingly beautiful and cute 24-year-old South Indian woman "
    "(naturally fit medium-slender build with graceful feminine curves, radiant charming smile, captivating expressive eyes, glowing skin). "
    "She is performing live on an intimate acoustic concert stage, singing into a vintage chrome condenser microphone on a stand, one hand gently resting on the mic stand. "
    "Wardrobe: wearing a gorgeous modern designer Punjabi dress (stylish sleeveless pastel ice-blue and silver georgette kurti with delicate minimal thread embroidery along the sweetheart neckline, fitted matching pants, lightweight sheer dupatta gracefully draped over one shoulder), subtle delicate silver jhumki earrings and minimal bracelet. "
    "Cute, modern, youthful, and elegant Indo-western aesthetic. "
    "Lighting: bright crisp neutral white 5600K studio key spotlight illuminating her face, hair, and outfit with sharp clarity. "
    "Background: cool deep blue and indigo ambient concert stage, soft-focus silhouettes of an audience swaying with bokeh concert lights, 50mm f/1.4 portrait lens, ultra-sharp focus."
)

NEGATIVE_PROMPT = (
    "overly traditional heavy bridal saree, yellow tint, amber wash, golden hour flare, oversaturated orange, "
    "too skinny bony, chubby, distorted hands, blurry face, low resolution, clumsy anatomy."
)


async def main():
    out_dir = Path("storage/tests/lofi_singer_test").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_img = out_dir / "south_indian_singer_punjabi_dress.jpg"

    fal_key = _fal_api_key()
    if not fal_key:
        raise ValueError("FAL_KEY is not configured.")

    print("=====================================================================")
    print("🎤 Generating Master Keyframe: Cute & Modern South Indian Singer")
    print("👗 Wardrobe: Stylish Sleeveless Ice-Blue Modern Punjabi Suit")
    print("💡 Lighting: Crisp Bright White Spotlight (5600K) + Deep Blue Ambient")
    print("💰 Cost: ~$0.025 (Flux Dev on Fal.ai)")
    print("=====================================================================\n")

    t0 = time.time()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": PUNJABI_DRESS_PROMPT,
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

        print("⏳ Rendering 4K keyframe on Fal GPU...")
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
    print(f"✅ Modern Punjabi Dress Keyframe Complete!")
    print(f"⏱️ Finished in {elapsed:.1f}s")
    print(f"📦 File Size: {size_kb:.1f} KB")
    print(f"🖼️ Local Path: {out_img}")
    print("=====================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
