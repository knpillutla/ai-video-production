"""Standalone Idempotent Tool to Stretch any Existing Reviewed 60s Video to Long-Play.

Supports --episode-id, --latest, or direct --video file path.
Zero re-encoding loss, zero API cost ($0.00), renders in ~5-10 seconds.
"""

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.long_play_stretcher import export_long_play_broadcast


def find_latest_episode_master(channel_dir: Path) -> Path | None:
    """Find the most recent master video in a channel's storage directory."""
    if not channel_dir.is_dir():
        return None
    ep_dirs = sorted([d for d in channel_dir.iterdir() if d.is_dir() and d.name.startswith("ep_")], key=lambda d: d.stat().st_mtime, reverse=True)
    for ep in ep_dirs:
        master = ep / "master_4k_ambient.mp4"
        if master.is_file():
            return master
    return None


def main():
    parser = argparse.ArgumentParser(description="Idempotent tool to stretch any reviewed video to Long-Play")
    parser.add_argument("--episode-id", type=str, default=None, help="Episode directory name (e.g. ep_swiss_alps_1727285200)")
    parser.add_argument("--channel", type=str, default="earth_serenade", choices=["earth_serenade", "silent_hearth", "rain_and_quill"])
    parser.add_argument("--latest", action="store_true", help="Automatically pick the most recent produced episode")
    parser.add_argument("--video", type=str, default=None, help="Direct path to 60s master video")
    parser.add_argument("--hours", type=float, default=3.0, help="Target long-play duration in hours (e.g. 1.0, 2.5, 3.0, 8.0)")
    parser.add_argument("--fade-black", type=float, default=None, help="Optional hours after which screen fades to black (e.g. 2.0)")
    args = parser.parse_args()

    src_video = None
    if args.video:
        src_video = Path(args.video).resolve()
    elif getattr(args, "episode_id", None):
        src_video = PROJECT_ROOT / "storage/channels" / args.channel / args.episode_id / "master_4k_ambient.mp4"
    elif args.latest:
        src_video = find_latest_episode_master(PROJECT_ROOT / "storage/channels" / args.channel)

    if not src_video or not src_video.is_file():
        # Fallback search in latest channel dir
        src_video = find_latest_episode_master(PROJECT_ROOT / "storage/channels" / args.channel)

    if not src_video or not src_video.is_file():
        print(f"\n❌ Could not find 60s master video. Please specify --video or --episode-id\n")
        return

    suffix = f"_{int(args.fade_black)}h_black" if args.fade_black else ""
    hour_label = int(args.hours) if args.hours.is_integer() else args.hours
    out_video = src_video.parent / f"master_4k_{hour_label}hour{suffix}_sleep.mp4"

    # Idempotent check: if target long-play already exists, report it
    if out_video.is_file() and out_video.stat().st_size > 1000:
        print("\n" + "=" * 65)
        print("⚡ IDEMPOTENT HIT: Target Long-Play already exists on disk!")
        print(f"File Path:   {out_video.resolve()}")
        print(f"File Size:   {round(out_video.stat().st_size / (1024*1024), 2)} MB")
        print("=" * 65 + "\n")
        return

    print("\n" + "=" * 65)
    print("⚡ IDEMPOTENT STRETCH: Stretching existing 60s master to Long-Play")
    print(f"Source 60s:  {src_video.resolve()}")
    print(f"Target:      {args.hours} Hours ({int(args.hours * 3600)}s)")
    if args.fade_black:
        print(f"Fade Black:  After {args.fade_black} Hours")
    print("=" * 65)

    export_long_play_broadcast(
        source_4k_video=src_video,
        output_long_play=out_video,
        target_duration_seconds=args.hours * 3600.0,
        fade_to_black_hours=args.fade_black,
    )

    print("\n" + "=" * 65)
    print("✅ LONG-PLAY MASTER EXPORT COMPLETE ($0.00 Extra Cost)!")
    print(f"Output File: {out_video.resolve()}")
    print(f"File Size:   {round(out_video.stat().st_size / (1024*1024), 2)} MB")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
