"""YouTube OAuth Credential & Authorization Service.

Manages Google OAuth 2.0 client secrets, channel-specific tokens,
and authorization verification for multi-channel video distribution.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

from src.core.telemetry import logger

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtubepartner",
]

SECRETS_DIR = Path("config/youtube_client_secrets")
TOKENS_DIR = Path("config/tokens")


def get_secret_file_path(channel_slug: str) -> Path:
    """Return path to channel client secret JSON file."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    return SECRETS_DIR / f"client_secret_{channel_slug}.json"


def get_token_file_path(channel_slug: str) -> Path:
    """Return path to channel authorized user token JSON file."""
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    return TOKENS_DIR / f"token_{channel_slug}.json"


def save_client_secret(channel_slug: str, secret_data: dict | bytes | str) -> Path:
    """Persist client secrets JSON for a specific distribution channel."""
    secret_path = get_secret_file_path(channel_slug)
    if isinstance(secret_data, bytes):
        secret_path.write_bytes(secret_data)
    elif isinstance(secret_data, str):
        secret_path.write_text(secret_data, encoding="utf-8")
    else:
        secret_path.write_text(json.dumps(secret_data, indent=2), encoding="utf-8")
    logger.info(f"youtube_client_secret_saved: channel='{channel_slug}' path='{secret_path}'")
    return secret_path


def get_channel_credentials(channel_slug: str) -> Optional[Credentials]:
    """Load and validate credentials for a channel, refreshing expired tokens automatically."""
    token_path = get_token_file_path(channel_slug)
    if not token_path.is_file() or token_path.stat().st_size < 10:
        return None

    try:
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                token_path.write_text(creds.to_json(), encoding="utf-8")
                logger.info(f"youtube_token_refreshed: channel='{channel_slug}'")
            except Exception as ref_err:
                logger.warning(f"failed_to_refresh_token: channel='{channel_slug}' error='{ref_err}'")
                return None
        return creds if (creds and creds.valid) else None
    except Exception as err:
        logger.warning(f"corrupt_token_file: channel='{channel_slug}' error='{err}'")
        return None


def get_auth_status(channel_slug: str) -> Dict[str, Any]:
    """Check whether channel credentials are valid and retrieve authorized YouTube details."""
    secret_path = get_secret_file_path(channel_slug)
    has_secret = secret_path.is_file() and secret_path.stat().st_size > 10

    creds = get_channel_credentials(channel_slug)
    if not creds:
        return {
            "authorized": False,
            "has_client_secret": has_secret,
            "channel_title": None,
            "channel_id": None,
            "channel_handle": None,
        }

    try:
        yt = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
        res = yt.channels().list(mine=True, part="snippet,contentDetails").execute()
        items = res.get("items", [])
        if items:
            ch_data = items[0]
            snippet = ch_data.get("snippet", {})
            return {
                "authorized": True,
                "has_client_secret": has_secret,
                "channel_id": ch_data.get("id"),
                "channel_title": snippet.get("title"),
                "channel_handle": snippet.get("customUrl"),
                "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url"),
            }
    except Exception as err:
        logger.error(f"failed_to_fetch_yt_channel_info: channel='{channel_slug}' error='{err}'")

    return {
        "authorized": True,
        "has_client_secret": has_secret,
        "channel_title": "Authorized Channel",
        "channel_id": None,
        "channel_handle": None,
    }


def authorize_channel_local_flow(channel_slug: str, port: int = 8085) -> Dict[str, Any]:
    """Execute local browser OAuth 2.0 flow using client secrets and save authorized token."""
    secret_path = get_secret_file_path(channel_slug)
    if not secret_path.is_file():
        raise FileNotFoundError(f"Missing client secret JSON for '{channel_slug}'. Please upload it first.")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise RuntimeError("Missing google-auth-oauthlib. Run: pip install google-auth-oauthlib") from exc

    flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), SCOPES)
    creds = flow.run_local_server(port=port, prompt="select_account consent")

    token_path = get_token_file_path(channel_slug)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    logger.info(f"youtube_oauth_completed: channel='{channel_slug}' token='{token_path.name}'")

    return get_auth_status(channel_slug)


def disconnect_channel(channel_slug: str) -> bool:
    """Revoke and delete the stored YouTube token for a channel."""
    token_path = get_token_file_path(channel_slug)
    if token_path.is_file():
        token_path.unlink(missing_ok=True)
        logger.info(f"youtube_channel_disconnected: channel='{channel_slug}'")
        return True
    return False
