"""Master Multi-Channel Network Manager for Warm Glow Entertainment.

Coordinates batch production and release cycles across all 3 flagship channels:
1. Earth Serenade (3H 4K Scenic Nature & Earth Sanctuaries)
2. Silent Hearth (8H All-Night Sleep with Black Screen + 432Hz)
3. Rain & Quill (3H Pomodoro Focus & Cozy Study Cafe)
"""

import argparse
import asyncio
from typing import Dict, Any

from src.core.telemetry import logger
from scripts.channels.nature_sanctuary_pipeline import run_nature_sanctuary_production
from scripts.channels.deep_sleep_sanctuary_pipeline import run_deep_sleep_production
from scripts.channels.study_focus_cafe_pipeline import run_study_focus_production


async def produce_full_network_release_batch(motion_model: str = "auto", master_duration: float = 60.0) -> Dict[str, Any]:
    """Produce 1 complete episode for each of the 3 flagship channels."""
    logger.info("starting_full_network_batch_production_cycle")
    results = {}

    print("\n" + "=" * 70)
    print("🚀 PRODUCING BATCH FOR WARM GLOW ENTERTAINMENT NETWORK")
    print("=" * 70)

    # 1. Channel 1: Earth Serenade (Swiss Alps 3H)
    print("\n▶ [1/3] Producing Channel 1: Earth Serenade (Swiss Alps 3H)...")
    results["earth_serenade"] = await run_nature_sanctuary_production(
        archetype="swiss_alps",
        motion_model=motion_model,
        master_duration=master_duration,
        long_play_hours=3.0,
        generate_short=True,
    )
    print(f"  ✓ Earth Serenade Complete: {results['earth_serenade']['master_video_path']}")

    # 2. Channel 2: Silent Hearth (Blizzard Cabin 8H with Fade-to-Black)
    print("\n▶ [2/3] Producing Channel 2: Silent Hearth (Blizzard Cabin 8H)...")
    results["silent_hearth"] = await run_deep_sleep_production(
        primary="blizzard",
        secondary="camp_fire",
        motion_model=motion_model,
        master_duration=master_duration,
        total_hours=8.0,
        fade_black_hours=2.0,
        generate_short=True,
    )
    print(f"  ✓ Silent Hearth Complete: {results['silent_hearth']['long_play_video_path']}")

    # 3. Channel 3: Rain & Quill (Beach House Rain 3H)
    print("\n▶ [3/3] Producing Channel 3: Rain & Quill (Beach House Rain 3H)...")
    results["rain_and_quill"] = await run_study_focus_production(
        primary="beach_house",
        secondary="rain",
        motion_model=motion_model,
        master_duration=master_duration,
        total_hours=3.0,
        generate_short=True,
    )
    print(f"  ✓ Rain & Quill Complete: {results['rain_and_quill']['long_play_video_path']}")

    print("\n" + "=" * 70)
    print("🎉 ALL 3 CHANNELS SUCCESSFULLY PRODUCED AND READY FOR REVIEW!")
    print("=" * 70 + "\n")
    return results


async def main():
    parser = argparse.ArgumentParser(description="Warm Glow Multi-Channel Network Manager")
    parser.add_argument("--channel", type=str, default="all", choices=["all", "nature", "sleep", "study"], help="Channel to produce")
    parser.add_argument("--motion-model", type=str, default="auto", choices=["auto", "wan", "kling", "hunyuan", "lanczos"], help="AI video diffusion motion model (default: auto)")
    parser.add_argument("--master-duration", type=float, default=60.0, choices=[60.0, 120.0], help="Initial master set duration in seconds (default: 60.0)")
    args = parser.parse_args()

    if args.channel == "all":
        await produce_full_network_release_batch(motion_model=args.motion_model, master_duration=args.master_duration)
    elif args.channel == "nature":
        await run_nature_sanctuary_production(archetype="swiss_alps", motion_model=args.motion_model, master_duration=args.master_duration, long_play_hours=3.0)
    elif args.channel == "sleep":
        await run_deep_sleep_production(primary="blizzard", secondary="camp_fire", motion_model=args.motion_model, master_duration=args.master_duration, total_hours=8.0, fade_black_hours=2.0)
    elif args.channel == "study":
        await run_study_focus_production(primary="beach_house", secondary="rain", motion_model=args.motion_model, master_duration=args.master_duration, total_hours=3.0)


if __name__ == "__main__":
    asyncio.run(main())
