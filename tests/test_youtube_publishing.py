"""Offline Unit Tests for YouTube Credentials, OAuth Status & Idempotent Publishing."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.services.youtube_auth_service import (
    get_auth_status,
    get_secret_file_path,
    get_token_file_path,
    save_client_secret,
    disconnect_channel,
)
from src.services.youtube_publish_pipeline import (
    get_episode_publish_status,
    publish_episode_bundle_idempotent,
)


def test_youtube_auth_status_unauthorized(tmp_path, monkeypatch):
    """Verify auth status returns authorized=False when no token exists."""
    monkeypatch.setattr("src.services.youtube_auth_service.TOKENS_DIR", tmp_path / "tokens")
    monkeypatch.setattr("src.services.youtube_auth_service.SECRETS_DIR", tmp_path / "secrets")

    status = get_auth_status("test_channel")
    assert status["authorized"] is False
    assert status["has_client_secret"] is False
    assert status["channel_title"] is None


def test_youtube_save_client_secret(tmp_path, monkeypatch):
    """Verify client secrets file is persisted accurately."""
    monkeypatch.setattr("src.services.youtube_auth_service.SECRETS_DIR", tmp_path / "secrets")

    secret_data = {"installed": {"client_id": "test_client_id", "client_secret": "test_secret"}}
    saved = save_client_secret("test_channel", secret_data)
    assert saved.is_file()
    loaded = json.loads(saved.read_text(encoding="utf-8"))
    assert loaded["installed"]["client_id"] == "test_client_id"


def test_youtube_publish_status_idempotent(tmp_path):
    """Verify get_episode_publish_status returns false initially and true once manifest exists."""
    ep_dir = tmp_path / "EP-001"
    ep_dir.mkdir(parents=True)

    initial = get_episode_publish_status(ep_dir)
    assert initial["published"] is False

    # Simulate saved publication manifest
    manifest = {
        "published": True,
        "published_at": 1791220000,
        "channel_slug": "earth_serenade",
        "short": {"video_id": "yt_short_123", "url": "https://youtube.com/shorts/yt_short_123"},
        "broadcast": {"video_id": "yt_broad_456", "url": "https://youtu.be/yt_broad_456"},
    }
    (ep_dir / "youtube_published.json").write_text(json.dumps(manifest), encoding="utf-8")

    res = get_episode_publish_status(ep_dir)
    assert res["published"] is True
    assert res["short"]["video_id"] == "yt_short_123"
    assert res["broadcast"]["video_id"] == "yt_broad_456"


def test_publish_bundle_idempotent_skips_when_published(tmp_path):
    """Verify publish_episode_bundle_idempotent avoids duplicate upload when already published."""
    ep_dir = tmp_path / "EP-001"
    ep_dir.mkdir(parents=True)
    manifest = {
        "published": True,
        "published_at": 1791220000,
        "channel_slug": "earth_serenade",
        "short": {"video_id": "s1", "url": "https://youtube.com/shorts/s1"},
        "broadcast": {"video_id": "b1", "url": "https://youtu.be/b1"},
    }
    (ep_dir / "youtube_published.json").write_text(json.dumps(manifest), encoding="utf-8")

    result = publish_episode_bundle_idempotent(ep_dir=ep_dir, channel_slug="earth_serenade")
    assert result["status"] == "already_published"
    assert result["data"]["short"]["video_id"] == "s1"
