"""Upload 4K Master Broadcasts & Pure Nature Variants to Earth Serenade (@EarthSerenade4K)."""

import argparse
from pathlib import Path
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.youtube_upload_service import upload_channel_episode


def main():
    parser = argparse.ArgumentParser(description="Upload 4K Masters to Earth Serenade YouTube Channel")
    parser.add_argument("--id", type=str, required=True, help="Episode ID to upload (e.g. ep_swiss_alps_1790365543)")
    parser.add_argument("--privacy", type=str, default="unlisted", choices=["public", "unlisted", "private"], help="YouTube privacy status (default: unlisted)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate upload payload without uploading")
    parser.add_argument("--no-short", action="store_true", help="Skip uploading the vertical 9:16 teaser short")
    args = parser.parse_args()

    channel_dir = Path("storage/channels/earth_serenade") / args.id
    if not channel_dir.is_dir():
        print(f"\n❌ Episode directory not found at: {channel_dir}")
        sys.exit(1)

    upload_channel_episode(
        channel_key="earth_serenade",
        channel_name="Earth Serenade",
        episode_dir=channel_dir,
        privacy_status=args.privacy,
        dry_run=args.dry_run,
        upload_short=not args.no_short,
    )


if __name__ == "__main__":
    main()
