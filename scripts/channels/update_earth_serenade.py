"""Dedicated Channel Updater for Earth Serenade (@EarthSerenade4K).

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

CHANNEL_KEY = "earth_serenade"


def main():
    print("\n" + "=" * 65)
    print("🏔️  UPDATING CHANNEL 1: EARTH SERENADE (@EarthSerenade4K)")
    print("Parent: Warm Glow Entertainment")
    print("Target: 4K Scenic Nature & Earth Sanctuaries")
    print("=" * 65)

    success = authenticate_and_update_channel(
        channel_key=CHANNEL_KEY,
        client_secrets_file=PROJECT_ROOT / "config/youtube_client_secret.json",
        token_dir=PROJECT_ROOT / "config/tokens",
    )

    if success:
        print("\n✅ Earth Serenade channel metadata updated successfully!\n")
    else:
        print("\n❌ Earth Serenade update encountered an issue. Check logs above.\n")


if __name__ == "__main__":
    main()
