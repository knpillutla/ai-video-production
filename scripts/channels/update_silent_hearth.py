"""Dedicated Channel Updater for Silent Hearth (@SilentHearthSleep).

Executes 1-click Google OAuth authentication and pushes SEO bio, description, and keywords.
"""

from pathlib import Path
import sys
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from scripts.channels.auth_and_update_channel import authenticate_and_update_channel

CHANNEL_KEY = "silent_hearth"


def main():
    print("\n" + "=" * 65)
    print("🌙  UPDATING CHANNEL 2: SILENT HEARTH (@SilentHearthSleep)")
    print("Parent: Warm Glow Entertainment")
    print("Target: 8-Hour Deep Sleep & Insomnia Sanctuary")
    print("=" * 65)

    success = authenticate_and_update_channel(
        channel_key=CHANNEL_KEY,
        client_secrets_file=PROJECT_ROOT / "config/youtube_client_secret.json",
        token_dir=PROJECT_ROOT / "config/tokens",
    )

    if success:
        print("\n✅ Silent Hearth channel metadata updated successfully!\n")
    else:
        print("\n❌ Silent Hearth update encountered an issue. Check logs above.\n")


if __name__ == "__main__":
    main()
