"""Dedicated Idempotent Stretch Script for Silent Hearth (@SilentHearthSleep).

Usage:
  1. Stretch Latest Video (No arguments needed - defaults to 8H with 2H Fade-to-Black):
     python scripts/channels/stretch_silent_hearth.py

  2. Stretch Specific Episode by ID:
     python scripts/channels/stretch_silent_hearth.py --id ep_blizzard_1727285200 --hours 8.0 --fade-black 2.0
"""

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.long_play_stretcher import export_long_play_broadcast
from scripts.channels.stretch_existing_video import find_latest_episode_master

CHANNEL_KEY = "silent_hearth"


def main():
    parser = argparse.ArgumentParser(description="Stretch Silent Hearth 60s video to 8-Hour Deep Sleep")
    parser.add_argument("--id", type=str, default=None, help="Episode ID/folder name (e.g. ep_blizzard_1727285200)")
    parser.add_argument("--hours", type=float, default=8.0, help="Total sleep duration in hours (default: 8.0)")
    parser.add_argument("--fade-black", type=float, default=2.0, help="Hours after which video fades to OLED black (default: 2.0)")
    args = parser.parse_args()

    channel_dir = PROJECT_ROOT / "storage/channels" / CHANNEL_KEY

    if args.id:
        src_video = channel_dir / args.id / "master_4k_ambient.mp4"
    else:
        src_video = find_latest_episode_master(channel_dir)

    if not src_video or not src_video.is_file():
        print(f"\n❌ No 60s master video found in {channel_dir}")
        print("Please produce a 60s video first or provide a valid --id\n")
        return

    suffix = f"_{int(args.fade_black)}h_black" if args.fade_black else ""
    hour_label = int(args.hours) if args.hours.is_integer() else args.hours
    out_video = src_video.parent / f"master_4k_{hour_label}hour{suffix}_sleep.mp4"

    if out_video.is_file() and out_video.stat().st_size > 1000:
        print("\n" + "=" * 65)
        print("⚡ IDEMPOTENT HIT: Target Long-Play already exists on disk!")
        print(f"File Path:   {out_video.resolve()}")
        print(f"File Size:   {round(out_video.stat().st_size / (1024*1024), 2)} MB")
        print("=" * 65 + "\n")
        return

    print("\n" + "=" * 65)
    print("🌙  STRETCHING SILENT HEARTH TO 8-HOUR DEEP SLEEP ($0.00 Cost)")
    print(f"Episode:     {src_video.parent.name}")
    print(f"Total Sleep: {args.hours} Hours | Fades to Black after {args.fade_black} Hours")
    print("=" * 65)

    export_long_play_broadcast(
        source_4k_video=src_video,
        output_long_play=out_video,
        target_duration_seconds=args.hours * 3600.0,
        fade_to_black_hours=args.fade_black,
    )

    print("\n" + "=" * 65)
    print("✅ SILENT HEARTH 8-HOUR SLEEP EXPORT COMPLETE!")
    print(f"Output File: {out_video.resolve()}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
