"""Niche Channel 1 Pipeline: Earth Serenade (4K Scenic Nature).

Produces 60s 4K Master with Velvet anti-fatigue audio, pauses for user review,
and stretches to 1h/3h long-play only after approval. Supports resuming with --id.
"""

import argparse
import asyncio
from pathlib import Path
import sys
from typing import Optional
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

from src.core.telemetry import logger
from src.services.long_play_stretcher import export_long_play_broadcast
from src.studios.ambient_world.ambient_producer import AmbientWorldProducer
from src.studios.ambient_world.ambient_storyboard import generate_ambient_storyboard

NATURE_ARCHETYPES = ["swiss_alps", "himalayas", "ocean_world", "mountains", "lake", "forest", "autumn"]


async def run_nature_sanctuary_production(
    archetype: str = "swiss_alps",
    episode_id: Optional[str] = None,
    motion_model: str = "auto",
    master_duration: Optional[float] = None,
    shots: Optional[int] = None,
    long_play_hours: float = 3.0,
    generate_short: bool = True,
    review_first: bool = True,
) -> dict:
    """Execute production for Earth Serenade channel with idempotent caching and review gate."""
    logger.info(f"starting_nature_sanctuary_channel_job: archetype={archetype} id={episode_id} motion={motion_model}")
    print(f"\n[DECISION - CHANNEL TOPIC SELECTION]")
    print(f"   * Channel:   Earth Serenade (@EarthSerenade4K | 4K Scenic Nature Sanctuaries)")
    print(f"   * Archetype: {archetype.replace('_', ' ').title()}")
    print(f"   * Strategy:  High-CTR nature relaxation with immersive spatial foley and alpine acoustic depth.")
    
    sb = generate_ambient_storyboard(primary=archetype, duration_seconds=master_duration, num_shots=shots)
    producer = AmbientWorldProducer(output_base_dir=Path("storage/channels/earth_serenade"))
    
    # 1. Produce Master Video First (Idempotent: skips existing artifacts)
    result = await producer.produce(
        sb=sb,
        episode_id=episode_id,
        motion_model=motion_model,
        long_play_hours=None,
        fade_to_black_hours=None,
        generate_short=generate_short,
    )

    master_path = Path(result["master_video_path"])
    actual_dur = int(sb.total_duration)
    print("\n" + "=" * 70)
    print(f"🎬 {actual_dur}-SECOND 4K MASTER READY FOR REVIEW ({len(sb.scenes)} Shots)!")
    print(f"Episode ID:  {result['episode_id']}")
    print(f"File Path:   {master_path.resolve()}")
    print(f"Audio Track: {result['bgm_path']}")
    if result.get("short_video_path"):
        print(f"9:16 Short:  {result['short_video_path']}")
    print("=" * 70)

    if review_first:
        prompt = input(f"\n👉 Open and review the {actual_dur}s master above.\nStretch to {long_play_hours} Hours Long-Play now? [Y/n]: ").strip().lower()
        if prompt in ("n", "no", "exit", "quit"):
            print(f"\n⏸️  Long-play stretch skipped. To stretch later, run:")
            print(f"   python scripts/channels/stretch_earth_serenade.py --id {result['episode_id']}\n")
            return result

    # 2. Stretch to Long-Play upon confirmation
    print(f"\n⚡ Stretching {actual_dur}s master to {long_play_hours} Hours Long-Play in ~10 seconds...")
    target_sec = long_play_hours * 3600.0
    hour_label = int(long_play_hours) if long_play_hours.is_integer() else long_play_hours
    long_play_path = master_path.parent / f"master_4k_{hour_label}hour_sleep.mp4"
    if not long_play_path.is_file() or long_play_path.stat().st_size < 1000:
        export_long_play_broadcast(
            source_4k_video=master_path,
            output_long_play=long_play_path,
            target_duration_seconds=target_sec,
        )

    result["long_play_video_path"] = str(long_play_path)
    print(f"✅ Long-Play Video Ready: {long_play_path.resolve()}\n")
    return result


async def main():
    parser = argparse.ArgumentParser(description="Earth Serenade Niche Channel Producer")
    parser.add_argument("--archetype", type=str, default="swiss_alps", choices=NATURE_ARCHETYPES, help="Nature archetype")
    parser.add_argument("--id", type=str, default=None, help="Optional existing episode ID to resume/reuse cached artifacts")
    parser.add_argument("--motion-model", type=str, default="auto", choices=["auto", "wan", "kling", "hunyuan", "lanczos"], help="AI video diffusion motion model (default: auto)")
    parser.add_argument("--master-duration", type=float, default=None, choices=[60.0, 90.0, 120.0], help="Master set duration in seconds (default: auto-derived by topic)")
    parser.add_argument("--shots", type=int, default=None, choices=[2, 3, 4], help="Explicit number of visual shots (default: auto-derived by topic)")
    parser.add_argument("--hours", type=float, default=3.0, help="Long-play duration in hours (e.g. 1.0, 3.0, 2.5)")
    parser.add_argument("--no-short", action="store_true", help="Disable 9:16 vertical short generation")
    parser.add_argument("--no-review", action="store_true", help="Auto-stretch without pausing for review")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("🏔️  CHANNEL 1: EARTH SERENADE & 4K SCENIC RELAXATION")
    print(f"Theme:       {args.archetype.replace('_', ' ').title()}")
    print(f"Master Set:  {args.master_duration or 'Auto-Derived'}s (Shots: {args.shots or 'Auto-Derived'})")
    print(f"Motion:      AI Video Diffusion ({args.motion_model})")
    if args.id:
        print(f"Episode ID:  {args.id} (Idempotent Resume Mode)")
    print(f"Target:      {args.hours} Hours")
    print("SEO:         Multi-Language Packaged (JA, DE, ES, PT, FR, KO)")
    print("=" * 65)

    await run_nature_sanctuary_production(
        archetype=args.archetype,
        episode_id=args.id,
        motion_model=args.motion_model,
        master_duration=args.master_duration,
        shots=args.shots,
        long_play_hours=args.hours,
        generate_short=not args.no_short,
        review_first=not args.no_review,
    )


if __name__ == "__main__":
    asyncio.run(main())
