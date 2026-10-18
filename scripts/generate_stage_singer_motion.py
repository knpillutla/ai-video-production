"""Generate 5-Second Living Stage Performance Motion for Approved Singer Keyframe via Wan 2.1."""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.providers.visual.fal_wan21 import FalWan21Adapter

STAGE_MOTION_PROMPT = (
    "Cinematic live concert performance: the beautiful and cute South Indian singer gently sways her head and shoulders "
    "to the rhythm of the music while holding the vintage chrome microphone stand, soft natural blinking, expressive emotional eyes, "
    "gentle chest breathing, subtle charming smile, bright crisp white spotlight illuminating her face and modern pastel Punjabi dress, "
    "soft atmospheric stage haze, fluid realistic human kinematics, Coke Studio live session aesthetic."
)

NEGATIVE_PROMPT = (
    "fast jerky movement, robotic motion, unnatural head twists, distorted facial features, deformed hands, "
    "glitching eyes, strobe lighting, cartoonish animation, blurry resolution."
)


async def main():
    img_path = Path("storage/tests/lofi_singer_test/south_indian_singer_punjabi_dress.jpg").resolve()
    out_video = Path("storage/tests/lofi_singer_test/stage_singer_living_motion_5s.mp4").resolve()

    if not img_path.is_file():
        raise FileNotFoundError(f"Keyframe not found at {img_path}")

    print("=====================================================================")
    print("🎬 Generating 5-Second Living Stage Motion via Alibaba Wan 2.1")
    print(f"🖼️ Input Keyframe: {img_path.name}")
    print(f"📁 Output Video: {out_video.name}")
    print("💰 Estimated Cost: $0.40 (5 seconds @ $0.08/s on Fal.ai)")
    print("=====================================================================\n")

    t0 = time.time()
    adapter = FalWan21Adapter()

    _, saved_path = await adapter.generate_video(
        image_url=str(img_path),
        motion_prompt=STAGE_MOTION_PROMPT,
        output_path=out_video,
        duration=5,
        force_live=True,
        negative_prompt=NEGATIVE_PROMPT,
    )

    elapsed = time.time() - t0
    size_mb = saved_path.stat().st_size / (1024 * 1024)

    print("\n=====================================================================")
    print("✅ Living Stage Performance Video Complete!")
    print(f"⏱️ Generation Time: {elapsed:.1f}s")
    print(f"📦 File Size: {size_mb:.2f} MB")
    print(f"🎥 Local Path: {saved_path}")
    print("=====================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
