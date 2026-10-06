"""Targeted unit tests for Universal Artifact Registry Service."""
from pathlib import Path
import json
from unittest.mock import AsyncMock, patch
import pytest

from src.services.artifact_registry_service import (
    UniversalArtifactRecord,
    register_artifact,
    get_artifact,
    list_artifacts,
    resolve_or_download_artifact,
)


def test_register_and_get_artifact(tmp_path: Path):
    """Verify artifact registration writes to pipeline_state.json and can be retrieved."""
    rec = UniversalArtifactRecord(
        artifact_id="EP-001_motion_p2",
        category="video",
        scene_index=2,
        model="wan_2_1",
        owner="test_user@example.com",
        status="synthesized",
        local_path="motion_p2.mp4",
        local_url="/storage/channels/ep001/motion_p2.mp4",
        remote_url="https://v3b.fal.media/files/b/test_motion_p2.mp4",
        file_size_bytes=2048000,
        duration_seconds=5.0,
        resolution="3840x2160",
    )
    register_artifact(tmp_path, rec)

    fetched = get_artifact(tmp_path, "EP-001_motion_p2")
    assert fetched is not None
    assert fetched.model == "wan_2_1"
    assert fetched.owner == "test_user@example.com"
    assert fetched.remote_url == "https://v3b.fal.media/files/b/test_motion_p2.mp4"

    all_arts = list_artifacts(tmp_path)
    assert len(all_arts) == 1
    assert all_arts[0].artifact_id == "EP-001_motion_p2"


@pytest.mark.asyncio
async def test_resolve_or_download_local_cache_hit(tmp_path: Path):
    """Tier 1: Local file exists (>1000 bytes) -> returns local file with $0.00 spend."""
    local_f = tmp_path / "motion_p1.mp4"
    local_f.write_bytes(b"A" * 2000)

    res = await resolve_or_download_artifact(
        ep_dir=tmp_path,
        artifact_id="EP-001_motion_p1",
        local_file=local_f,
    )
    assert res == local_f


@pytest.mark.asyncio
async def test_resolve_or_download_remote_cdn_hit(tmp_path: Path):
    """Tier 2: Local file is missing, but remote_url is recorded -> re-downloads from CDN."""
    local_f = tmp_path / "motion_p2.mp4"
    assert not local_f.exists()

    rec = UniversalArtifactRecord(
        artifact_id="EP-001_motion_p2",
        category="video",
        model="wan_2_1",
        owner="test_user@example.com",
        local_path="motion_p2.mp4",
        remote_url="https://v3b.fal.media/files/b/test_motion_p2.mp4",
    )
    register_artifact(tmp_path, rec)

    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.content = b"VIDEO_BYTES_FROM_REMOTE_CDN" * 100

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        res = await resolve_or_download_artifact(
            ep_dir=tmp_path,
            artifact_id="EP-001_motion_p2",
            local_file=local_f,
        )

    assert res == local_f
    assert local_f.exists()
    assert len(local_f.read_bytes()) == len(mock_resp.content)
