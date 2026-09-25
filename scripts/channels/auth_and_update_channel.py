"""Automated Google OAuth 2.0 Authenticator & Channel Metadata Publisher.

Authenticates with YouTube Data API v3 and updates channel bio, description, and keywords.
"""

import argparse
import json
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from src.core.telemetry import logger
from scripts.channels.update_channel_metadata import get_channel_branding_bundle

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtubepartner",
]


def authenticate_and_update_channel(
    channel_key: str = "earth_serenade",
    client_secrets_file: Path | str = "config/youtube_client_secret.json",
    token_dir: Path | str = "config/tokens",
):
    """Run OAuth flow and update channel metadata via YouTube Data API."""
    secrets_path = Path(client_secrets_file).resolve()
    tokens_path = Path(token_dir).resolve()
    tokens_path.mkdir(parents=True, exist_ok=True)
    token_file = tokens_path / f"token_{channel_key}.json"

    if not secrets_path.is_file():
        print(f"\n❌ Client secrets file not found at: {secrets_path}")
        print("Please download your OAuth client JSON from Google Cloud Console and save it to config/youtube_client_secret.json\n")
        return False

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import googleapiclient.discovery
    except ImportError:
        print("\n❌ Google API client libraries missing. Install with: pip install google-api-python-client google-auth-oauthlib\n")
        return False

    creds = None
    if token_file.is_file():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            branding = get_channel_branding_bundle(channel_key)
            print(f"\n🌐 Opening browser for 1-time YouTube authorization for '{branding.channel_name}'...")
            print(f"👉 In the Google Brand Account picker, select: 👉 '{branding.channel_name}' 👈\n")
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
            creds = flow.run_local_server(port=0, prompt="select_account consent")

        token_file.write_text(creds.to_json(), encoding="utf-8")
        print(f"✅ Token saved permanently to: {token_file}")

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    # Fetch current channel details
    response = youtube.channels().list(part="snippet,brandingSettings", mine=True).execute()
    if not response.get("items"):
        print("❌ No channel found for authorized account.")
        return False

    channel_item = response["items"][0]
    channel_id = channel_item["id"]
    branding = get_channel_branding_bundle(channel_key)

    print(f"\n📡 Connected to YouTube Channel: {channel_item['snippet']['title']} (ID: {channel_id})")
    print(f"📝 Pushing SEO Bio and Keywords for '{branding.channel_name}'...")

    # Update Channel Branding Settings (Description and Keywords)
    update_body = {
        "id": channel_id,
        "brandingSettings": {
            "channel": {
                "description": branding.about_description,
                "keywords": " ".join([f'"{k}"' if " " in k else k for k in branding.channel_keywords]),
                "featuredChannelsTitle": "Warm Glow Entertainment Network",
            }
        }
    }

    try:
        update_resp = youtube.channels().update(part="brandingSettings", body=update_body).execute()
        print(f"🎉 SUCCESS! Channel '{branding.channel_name}' bio, description, and keywords updated successfully!")
        return True
    except Exception as err:
        print(f"⚠️ Error updating channel metadata: {err}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Authenticate and update YouTube Channel metadata")
    parser.add_argument(
        "--channel",
        type=str,
        default="earth_serenade",
        choices=["earth_serenade", "silent_hearth", "rain_and_quill"],
        help="Channel to authenticate and update",
    )
    args = parser.parse_args()
    authenticate_and_update_channel(channel_key=args.channel)


if __name__ == "__main__":
    main()
