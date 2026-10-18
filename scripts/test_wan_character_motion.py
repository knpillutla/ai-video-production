"""Generate 5-second living character motion using Alibaba Wan 2.1 via Fal.ai."""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.core.telemetry import logger
from src.providers.visual.fal_wan21 import FalWan21Adapter

MOTION_PROMPT = (
    "Cinematic natural movement: the beautiful young South Indian woman wearing headphones gently sways her head "
    "and shoulders to the slow Lo-Fi chillhop beat, soft natural blinking, gentle chest breathing, peaceful subtle smile, "
    "rain trickling down the windowpane, warm incandescent lamp glow, cozy nostalgic atmosphere, fluid realistic human motion."
)

NEGATIVE_PROMPT = (
    "fast motion, robotic movement, unnatural head jerk, distorted facial features, deformed hands, "
    "glitching eyes, strobe lighting, cartoonish animation."
)


async def main():
    img_path = Path("storage/tests/lofi_singer_test/character_singer_portrait.jpg").resolve()
    out_video = Path("storage/tests/lofi_singer_test/character_living_motion_5s.mp4").resolve()

    if not img_path.is_file():
        raise FileNotFoundError(f"Keyframe not found at {img_path}")

    print("=====================================================================")
    print("🎬 Generating 5-Second Living Character Motion via Alibaba Wan 2.1")
    print(f"🖼️ Input Keyframe: {img_path.name}")
    print(f"📁 Output Video: {out_video.name}")
    print("💰 Estimated Cost: $0.40 (5 seconds @ $0.08/s on Fal.ai)")
    print("=====================================================================\n")

    t0 = time.time()
    adapter = FalWan21Adapter()

    # force_live=True to dispatch the live model to Fal
    video_url, saved_path = await adapter.generate_video(
        image_url=str(img_path),
        motion_prompt=MOTION_PROMPT,
        output_path=out_video,
        duration=5,
        force_live=True,
        negative_prompt=NEGATIVE_PROMPT,
    )

    elapsed = time.time() - t0
    size_mb = saved_path.stat().st_size / (1024 * 1024)

    print("\n=====================================================================")
    print(f"✅ Living Character Video Complete!")
    print(f"⏱️ Generation Time: {elapsed:.1f}s")
    print(f"📦 File Size: {size_mb:.2f} MB")
    print(f"🎥 Local Path: {saved_path}")
    print("=====================================================================")


if __name__ == "__main__":
    asyncio.run(main())
