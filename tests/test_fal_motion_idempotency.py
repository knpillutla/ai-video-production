"""Unit tests verifying Fal motion adapter sidecar preservation and idempotent redownload (Rule 3 & 8)."""

import json
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.providers.visual.fal_kling_v3 import FalKlingV3Adapter
from src.providers.visual.fal_wan21 import FalWan21Adapter
from src.providers.dance.fal_kling import FalKlingAdapter


@pytest.mark.asyncio
async def test_kling_v3_sidecar_preserved_on_timeout(tmp_path: Path):
    """Verify that FalKlingV3Adapter does NOT delete job sidecar when timing out."""
    out_mp4 = tmp_path / "raw_diff_motion_p1.mp4"
    sidecar = out_mp4.with_suffix(out_mp4.suffix + ".fal_job.json")

    mock_client = AsyncMock()
    # POST submit response
    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 200
    mock_post_resp.json.return_value = {
        "status_url": "https://queue.fal.run/status/123",
        "response_url": "https://queue.fal.run/resp/123",
    }
    mock_client.post.return_value = mock_post_resp

    # GET poll responses: status is IN_PROGRESS (202), response_url is 202
    mock_poll_resp = MagicMock()
    mock_poll_resp.status_code = 202
    mock_poll_resp.json.return_value = {"status": "IN_PROGRESS"}
    mock_client.get.return_value = mock_poll_resp

    adapter = FalKlingV3Adapter(api_key="mock_key")

    with patch("httpx.AsyncClient") as mock_http_cls, \
         patch("src.providers.visual.fal_kling_v3._POLL_MAX_ATTEMPTS", 2), \
         patch("src.providers.visual.fal_kling_v3._POLL_INTERVAL_S", 0.01):
        mock_http_cls.return_value.__aenter__.return_value = mock_client

        with pytest.raises(TimeoutError):
            await adapter.generate_video(
                image_url="https://fake.fal.media/img.jpg",
                motion_prompt="Heavy rain downpour",
                output_path=out_mp4,
                force_live=True,
            )

    # CRITICAL: Verify job sidecar is PRESERVED on disk!
    assert sidecar.exists(), "Job sidecar was deleted on timeout! Must be preserved for resumption."
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert data["status_url"] == "https://queue.fal.run/status/123"
    assert data["response_url"] == "https://queue.fal.run/resp/123"


@pytest.mark.asyncio
async def test_kling_v3_redownloads_from_existing_url(tmp_path: Path):
    """Verify that if a remote URL sidecar exists, generation re-downloads without calling submit endpoint."""
    out_mp4 = tmp_path / "raw_diff_motion_p1.mp4"
    meta_sidecar = out_mp4.with_suffix(out_mp4.suffix + ".fal_meta.json")
    meta_sidecar.write_text(json.dumps({
        "video_url": "https://v3b.fal.media/files/kling_test.mp4",
        "response_url": "https://queue.fal.run/resp/123"
    }), encoding="utf-8")

    mock_client = AsyncMock()
    mock_dl_resp = MagicMock()
    mock_dl_resp.status_code = 200
    mock_dl_resp.content = b"fake_video_data_1234567890" * 500  # > 5000 bytes
    mock_client.get.return_value = mock_dl_resp

    adapter = FalKlingV3Adapter(api_key="mock_key")

    with patch("httpx.AsyncClient") as mock_http_cls:
        mock_http_cls.return_value.__aenter__.return_value = mock_client
        vid_url, res_path = await adapter.generate_video(
            image_url="https://fake.fal.media/img.jpg",
            motion_prompt="Heavy rain downpour",
            output_path=out_mp4,
            force_live=True,
        )

        assert vid_url == "https://v3b.fal.media/files/kling_test.mp4"
        assert res_path == out_mp4
        assert out_mp4.exists()
        # Verify submit endpoint was NEVER called!
        mock_client.post.assert_not_called()


@pytest.mark.asyncio
async def test_wan21_sidecar_preserved_on_timeout(tmp_path: Path):
    """Verify that FalWan21Adapter does NOT delete job sidecar when timing out."""
    out_mp4 = tmp_path / "raw_diff_motion_p1.mp4"
    sidecar = out_mp4.with_suffix(out_mp4.suffix + ".fal_job.json")

    mock_client = AsyncMock()
    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 200
    mock_post_resp.json.return_value = {
        "status_url": "https://queue.fal.run/status/wan123",
        "response_url": "https://queue.fal.run/resp/wan123",
    }
    mock_client.post.return_value = mock_post_resp

    mock_poll_resp = MagicMock()
    mock_poll_resp.status_code = 202
    mock_poll_resp.json.return_value = {"status": "IN_PROGRESS"}
    mock_client.get.return_value = mock_poll_resp

    adapter = FalWan21Adapter(api_key="mock_key")

    with patch("httpx.AsyncClient") as mock_http_cls, \
         patch("src.providers.visual.fal_wan21._POLL_MAX_ATTEMPTS", 2), \
         patch("src.providers.visual.fal_wan21._POLL_INTERVAL_S", 0.01):
        mock_http_cls.return_value.__aenter__.return_value = mock_client

        with pytest.raises(TimeoutError):
            await adapter.generate_video(
                image_url="https://fake.fal.media/img.jpg",
                motion_prompt="Flowing mountain stream",
                output_path=out_mp4,
                force_live=True,
            )

    assert sidecar.exists(), "Wan 2.1 sidecar was deleted on timeout! Must be preserved for resumption."


@pytest.mark.asyncio
async def test_kling_sidecar_preserved_on_timeout(tmp_path: Path):
    """Verify that FalKlingAdapter does NOT delete job sidecar when timing out."""
    out_mp4 = tmp_path / "raw_diff_motion_p1.mp4"
    sidecar = out_mp4.with_suffix(out_mp4.suffix + ".fal_job.json")

    mock_client = AsyncMock()
    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 200
    mock_post_resp.json.return_value = {
        "status_url": "https://queue.fal.run/status/k123",
        "response_url": "https://queue.fal.run/resp/k123",
    }
    mock_client.post.return_value = mock_post_resp

    mock_poll_resp = MagicMock()
    mock_poll_resp.status_code = 202
    mock_poll_resp.json.return_value = {"status": "IN_PROGRESS"}
    mock_client.get.return_value = mock_poll_resp

    adapter = FalKlingAdapter(api_key="mock_key")

    with patch("httpx.AsyncClient") as mock_http_cls, \
         patch("src.providers.dance.fal_kling._POLL_MAX_ATTEMPTS", 2), \
         patch("src.providers.dance.fal_kling._POLL_INTERVAL_S", 0.01):
        mock_http_cls.return_value.__aenter__.return_value = mock_client

        with pytest.raises(TimeoutError):
            await adapter.generate_video(
                image_url="https://fake.fal.media/img.jpg",
                motion_prompt="Dance motion",
                output_path=out_mp4,
                force_live=True,
            )

    assert sidecar.exists(), "Kling sidecar was deleted on timeout! Must be preserved for resumption."
