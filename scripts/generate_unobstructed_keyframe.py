"""Generate Unobstructed Stage Keyframe via Z-Image Turbo ($0.01).

Critical Fix: Microphone held below chin at chest level, leaving lips & mouth 100% visible.
"""

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

UNOBSTRUCTED_PROMPT = (
    "Award-winning 4K live concert photograph of a strikingly cute and stylish 24-year-old South Indian woman "
    "(naturally fit medium-slender build with graceful feminine curves, radiant smile, captivating expressive eyes, glowing skin). "
    "She is performing live on an acoustic concert stage. "
    "She holds a vintage stage microphone comfortably in her hand below her chin at chest level; "
    "her mouth, lips, teeth, and facial expressions are completely clear, visible, and totally unobstructed by the microphone. "
    "Wardrobe: gorgeous modern designer sleeveless pastel ice-blue and silver georgette Punjabi dress with delicate silver embroidery, "
    "delicate silver jhumki earrings. Cute, stylish, and youthful. "
    "Lighting: bright crisp neutral white 5600K studio spotlight directly illuminating her face and outfit with sharp clarity. "
    "Background: cool deep blue concert stage with soft-focus audience bokeh lights, 50mm f/1.4 lens, ultra-sharp focus."
)


async def main():
    out_dir = Path("storage/tests/lofi_singer_test").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_img = out_dir / "unobstructed_singer_keyframe.png"

    fal_key = _fal_api_key()
    if not fal_key:
        raise ValueError("FAL_KEY is not configured.")

    print("=====================================================================")
    print("📸 Step 2: Generating Unobstructed Keyframe via Z-Image Turbo")
    print("🎤 Mic Placement: Held below chin at chest level (100% visible lips)")
    print("💰 Cost: ~$0.01 (Fal Z-Image Turbo)")
    print("=====================================================================\n")

    t0 = time.time()
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": UNOBSTRUCTED_PROMPT,
        "image_size": "landscape_16_9",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post("https://queue.fal.run/fal-ai/z-image/turbo", headers=headers, json=payload)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Z-Image submit failed: {resp.text}")

        data = resp.json()
        status_url = data.get("status_url")
        response_url = data.get("response_url")

        print("⏳ Rendering 4K unobstructed keyframe on Fal GPU...")
        for _ in range(30):
            await asyncio.sleep(1.5)
            st_data = (await client.get(status_url, headers=headers)).json()
            if st_data.get("status") == "COMPLETED":
                res_data = (await client.get(response_url, headers=headers)).json()
                img_url = res_data["images"][0]["url"]
                img_bytes = (await client.get(img_url)).content
                out_img.write_bytes(img_bytes)
                break
            elif st_data.get("status") in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Z-Image task failed: {st_data}")

    elapsed = time.time() - t0
    size_kb = out_img.stat().st_size / 1024

    print("\n=====================================================================")
    print(f"✅ Unobstructed Keyframe Ready!")
    print(f"⏱️ Finished in {elapsed:.1f}s")
    print(f"📦 File Size: {size_kb:.1f} KB")
    print(f"🖼️ Local Path: {out_img}")
    print("=====================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
