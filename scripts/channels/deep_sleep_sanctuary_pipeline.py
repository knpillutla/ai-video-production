"""Niche Channel 2 Pipeline: Silent Hearth (8-Hour Deep Sleep & Insomnia Sanctuary).

Produces 60s 4K Master with 432Hz binaural delta waves, pauses for user review,
and stretches to long-play (with Circadian Fade-to-Black) only after user confirmation. Supports --id resume.
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

SLEEP_ARCHETYPES = ["blizzard", "camp_fire", "night_sleep", "rain", "winter", "swiss_alps"]


async def run_deep_sleep_production(
    primary: str = "blizzard",
    secondary: str = "camp_fire",
    episode_id: Optional[str] = None,
    motion_model: str = "auto",
    master_duration: Optional[float] = None,
    shots: Optional[int] = None,
    total_hours: float = 8.0,
    fade_black_hours: float = 2.0,
    generate_short: bool = True,
    review_first: bool = True,
) -> dict:
    """Execute complete production for Silent Hearth channel with idempotent resume and review gate."""
    logger.info(f"starting_deep_sleep_channel_job: {primary}+{secondary} id={episode_id} motion={motion_model}")
    print(f"\n[DECISION - CHANNEL TOPIC SELECTION]")
    print(f"   * Channel:   Silent Hearth (@SilentHearthSleep | 8-Hour Insomnia & Deep Sleep)")
    print(f"   * Concept:   {primary.replace('_', ' ').title()} + {secondary.replace('_', ' ').title()}")
    print(f"   * Strategy:  Hypnotic delta-wave entrainment, cozy hearth warmth, and 2-hour circadian fade-to-black.")

    sb = generate_ambient_storyboard(primary=primary, secondary=secondary, duration_seconds=master_duration, num_shots=shots)
    producer = AmbientWorldProducer(output_base_dir=Path("storage/channels/silent_hearth"))

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
        prompt = input(f"\n👉 Open and review the {actual_dur}s master above.\nStretch to {total_hours} Hours (with {fade_black_hours}H Fade-to-Black) now? [Y/n]: ").strip().lower()
        if prompt in ("n", "no", "exit", "quit"):
            print(f"\n⏸️  Long-play stretch skipped. To stretch later, run:")
            print(f"   python scripts/channels/stretch_silent_hearth.py --id {result['episode_id']}\n")
            return result

    # 2. Stretch to Long-Play upon confirmation
    print(f"\n⚡ Stretching {actual_dur}s master to {total_hours} Hours Long-Play (Fade-to-Black at {fade_black_hours}h)...")
    target_sec = total_hours * 3600.0
    hour_label = int(total_hours) if total_hours.is_integer() else total_hours
    long_play_path = master_path.parent / f"master_4k_{hour_label}hour_{int(fade_black_hours)}h_black_sleep.mp4"
    if not long_play_path.is_file() or long_play_path.stat().st_size < 1000:
        export_long_play_broadcast(
            source_4k_video=master_path,
            output_long_play=long_play_path,
            target_duration_seconds=target_sec,
            fade_to_black_hours=fade_black_hours,
        )

    result["long_play_video_path"] = str(long_play_path)
    print(f"✅ Long-Play Sleep Video Ready: {long_play_path.resolve()}\n")
    return result


async def main():
    parser = argparse.ArgumentParser(description="Silent Hearth Niche Channel Producer")
    parser.add_argument("--primary", type=str, default="blizzard", choices=SLEEP_ARCHETYPES, help="Primary sleep archetype")
    parser.add_argument("--secondary", type=str, default="camp_fire", help="Secondary atmospheric element (e.g. camp_fire, rain)")
    parser.add_argument("--id", type=str, default=None, help="Optional existing episode ID to resume/reuse cached artifacts")
    parser.add_argument("--motion-model", type=str, default="auto", choices=["auto", "wan", "kling", "hunyuan", "lanczos"], help="AI video diffusion motion model (default: auto)")
    parser.add_argument("--master-duration", type=float, default=None, choices=[60.0, 90.0, 120.0], help="Master set duration in seconds (default: auto-derived by topic)")
    parser.add_argument("--shots", type=int, default=None, choices=[2, 3, 4], help="Explicit number of visual shots (default: auto-derived by topic)")
    parser.add_argument("--hours", type=float, default=8.0, help="Total sleep broadcast duration in hours (default: 8.0)")
    parser.add_argument("--fade-black", type=float, default=2.0, help="Hours after which video fades to OLED black screen (default: 2.0)")
    parser.add_argument("--no-short", action="store_true", help="Disable 9:16 vertical short generation")
    parser.add_argument("--no-review", action="store_true", help="Auto-stretch without pausing for review")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("🌙  CHANNEL 2: SILENT HEARTH & 8-HOUR DEEP SLEEP")
    print(f"Atmosphere:  {args.primary.title()} + {args.secondary.title()}")
    print(f"Master Set:  {args.master_duration or 'Auto-Derived'}s (Shots: {args.shots or 'Auto-Derived'})")
    print(f"Motion:      AI Video Diffusion ({args.motion_model})")
    if args.id:
        print(f"Episode ID:  {args.id} (Idempotent Resume Mode)")
    print(f"Target:      {args.hours} Hours | Fades to Black after {args.fade_black} Hours")
    print("Entrainment: 432Hz Binaural Delta Waves (2.0 Hz Deep REM Frequency)")
    print("=" * 65)

    await run_deep_sleep_production(
        primary=args.primary,
        secondary=args.secondary,
        episode_id=args.id,
        motion_model=args.motion_model,
        master_duration=args.master_duration,
        shots=args.shots,
        total_hours=args.hours,
        fade_black_hours=args.fade_black,
        generate_short=not args.no_short,
        review_first=not args.no_review,
    )


if __name__ == "__main__":
    asyncio.run(main())
