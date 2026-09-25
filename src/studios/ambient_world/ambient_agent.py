"""Standalone CLI Agent for Velvet Ambient World & Sleep Productions."""

import argparse
import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.studios.ambient_world.ambient_catalog import ARCHETYPES
from src.studios.ambient_world.ambient_producer import AmbientWorldProducer
from src.studios.ambient_world.ambient_storyboard import generate_ambient_storyboard


async def main():
    parser = argparse.ArgumentParser(description="Produce 4K Velvet Ambient & Sleep Video")
    parser.add_argument(
        "--archetype",
        type=str,
        default="swiss_alps",
        choices=list(ARCHETYPES.keys()),
        help=f"Primary ambient archetype ({', '.join(ARCHETYPES.keys())})",
    )
    parser.add_argument("--secondary", type=str, default=None, help="Optional atmosphere to blend (e.g. rain, camp_fire)")
    parser.add_argument("--duration", type=float, default=60.0, help="Initial master duration in seconds")
    parser.add_argument("--long-play-hours", type=float, default=None, help="Optional Long-Play stretch duration in hours (e.g. 1.0, 3.0, 8.0)")
    parser.add_argument("--fade-to-black-hours", type=float, default=None, help="Hours after which video fades to pure black OLED screen (e.g. 2.0)")
    parser.add_argument("--generate-short", action="store_true", help="Auto-generate 9:16 vertical Short/TikTok teaser")
    parser.add_argument("--title", type=str, default=None, help="Custom title")
    args = parser.parse_args()

    print("\n=======================================================")
    print("🌿 Ambient World Studio: Velvet Anti-Fatigue 4K Production")
    print(f"Primary Archetype:   {args.archetype}")
    print(f"Blended Atmosphere:  {args.secondary or 'None (Pure)'}")
    print(f"Audio Mastering:     -21 LUFS Velvet Sound + 432Hz Binaural Delta Waves")
    print(f"Long-Play Export:    {f'{args.long_play_hours} Hours' if args.long_play_hours else '60s Master Only'}")
    if args.fade_to_black_hours:
        print(f"Circadian Dimming:   Fades to Black Screen after {args.fade_to_black_hours} Hours")
    if args.generate_short:
        print("Shorts Teaser:       Auto-generating 9:16 vertical crop")
    print("=======================================================\n")

    sb = generate_ambient_storyboard(
        primary=args.archetype,
        secondary=args.secondary,
        custom_title=args.title,
        duration_seconds=args.duration,
    )
    producer = AmbientWorldProducer()
    result = await producer.produce(
        sb,
        long_play_hours=args.long_play_hours,
        fade_to_black_hours=args.fade_to_black_hours,
        generate_short=args.generate_short,
    )

    print("\n=======================================================")
    print("✅ Ambient Production Completed Successfully!")
    print(f"Episode ID:  {result['episode_id']}")
    print(f"Master 4K:   {result['master_video_path']}")
    if result.get("long_play_video_path"):
        print(f"Long-Play:   {result['long_play_video_path']}")
    if result.get("short_video_path"):
        print(f"9:16 Short:  {result['short_video_path']}")
    print(f"Soundtrack:  {result['bgm_path']}")
    print(f"YouTube SEO: {result['youtube_package']['title']}")
    print(f"Comment:     {result['youtube_package']['pinned_comment']}")
    print(f"Render Time: {result['render_time_seconds']}s")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
