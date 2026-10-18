"""Generate Shot 2: Acoustic Guitar Strumming Cutaway (Keyframe + Wan 2.1 Motion).

Total Cost: ~$0.42 (Flux Dev $0.02 + Wan 2.1 $0.40).
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
from src.providers.visual.fal_wan21 import FalWan21Adapter

GUITAR_KEYFRAME_PROMPT = (
    "Award-winning 4K live concert photograph: cinematic close-up of a musician's graceful hands playing a premium acoustic guitar on stage. "
    "Slender fingers pressing chords on the rosewood fretboard while the other hand gently strums the bronze acoustic guitar strings. "
    "Wardrobe detail: subtle sleeve of a modern pastel ice-blue georgette Punjabi dress with delicate silver bracelet on the wrist. "
    "Lighting: bright crisp neutral white 5600K spotlight illuminating the polished spruce guitar body and vibrating strings with razor-sharp clarity, "
    "cool deep indigo-blue ambient concert stage with soft-focus audience bokeh lights in background, 50mm f/1.4 macro cinematography, Coke Studio aesthetic."
)

GUITAR_MOTION_PROMPT = (
    "Cinematic live concert cutaway: graceful hands passionately strumming the acoustic guitar strings in rhythm to the beat, "
    "fingers shifting chords smoothly along the wooden fretboard, realistic natural finger kinematics and string vibration, "
    "bright white spotlight glinting on guitar strings, fluid realistic instrument playing motion."
)

NEGATIVE_PROMPT = (
    "deformed hands, extra fingers, missing fingers, unnatural hand motion, blurry guitar, "
    "yellow tint, amber wash, golden hour flare, glitchy movement."
)


async def main():
    out_dir = Path("storage/tests/lofi_singer_test").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    img_path = out_dir / "shot2_acoustic_guitar_keyframe.jpg"
    video_path = out_dir / "shot2_acoustic_guitar_5s.mp4"

    fal_key = _fal_api_key()
    if not fal_key:
        raise ValueError("FAL_KEY is not configured.")

    print("=====================================================================")
    print("🎸 Generating Shot 2: Acoustic Guitar Strumming Cutaway")
    print("💰 Total Cost: ~$0.42 (Flux Dev $0.02 + Wan 2.1 $0.40)")
    print("=====================================================================\n")

    t0 = time.time()

    # Step 1: Generate Guitar Keyframe via Flux Dev (~$0.02)
    if not img_path.is_file() or img_path.stat().st_size < 10000:
        print("📸 Step 1/2: Generating Acoustic Guitar Keyframe via Flux Dev...")
        headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
        payload = {
            "prompt": GUITAR_KEYFRAME_PROMPT,
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
            status_url, response_url = data.get("status_url"), data.get("response_url")

            for _ in range(40):
                await asyncio.sleep(2.0)
                st_data = (await client.get(status_url, headers=headers)).json()
                if st_data.get("status") == "COMPLETED":
                    res_data = (await client.get(response_url, headers=headers)).json()
                    img_bytes = (await client.get(res_data["images"][0]["url"])).content
                    img_path.write_bytes(img_bytes)
                    break
        print(f"  ✅ Guitar Keyframe Ready: {img_path.name} ({img_path.stat().st_size / 1024:.1f} KB)")
    else:
        print(f"  [CACHE HIT] Reusing existing guitar keyframe: {img_path.name} ($0.00)")

    # Step 2: Generate 5-Second Strumming Motion via Wan 2.1 ($0.40)
    print("\n🎬 Step 2/2: Generating 5s Living Strumming Motion via Alibaba Wan 2.1 ($0.40)...")
    adapter = FalWan21Adapter()
    _, saved_video = await adapter.generate_video(
        image_url=str(img_path),
        motion_prompt=GUITAR_MOTION_PROMPT,
        output_path=video_path,
        duration=5,
        force_live=True,
        negative_prompt=NEGATIVE_PROMPT,
    )

    elapsed = time.time() - t0
    size_mb = saved_video.stat().st_size / (1024 * 1024)

    print("\n=====================================================================")
    print("✅ Shot 2 (Acoustic Guitar Cutaway) Complete!")
    print(f"⏱️ Total Elapsed Time: {elapsed:.1f}s")
    print(f"📦 Video File Size: {size_mb:.2f} MB")
    print(f"🎥 Video Path: {saved_video}")
    print("=====================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
