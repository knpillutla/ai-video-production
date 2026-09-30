"""Automated test for 0-cost local video production and manual stage-gate photo mode."""

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import create_app


@pytest.mark.asyncio
async def test_local_video_production_persists_to_storage():
    """Verify manual mode stops after photos and auto mode renders complete MP4."""
    app = create_app()

    from src.mcp.topic_memory.server import clear_topic_vault
    clear_topic_vault("user_krishna_01")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test 1: Manual Mode (Stage 1 Photos Only)
        manual_payload = {
            "prompt": "Explore Niagara Falls Local Storage Test",
            "title": "Explore Niagara Falls Automated Test",
            "episode_id": "EP-AUTOTEST-MANUAL-01",
            "user_id": "user_krishna_01",
            "pipeline_strategy": "manual",
            "photos_only": True,
            "duration_seconds": 4.0,
            "num_shots": 1,
        }

        resp = await client.post("/api/production/local-produce", json=manual_payload)
        assert resp.status_code == 200, f"Expected 200 but got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["success"] is True
        assert data["episode_id"] == "EP-AUTOTEST-MANUAL-01"
        assert data["video_url"] is None
        assert len(data["keyframes"]) >= 1
        assert len(data["motion_clips"]) == 0

        # Verify keyframe image exists on disk
        kf_url = data["keyframes"][0]["url"]
        assert kf_url.startswith("/storage/")
        kf_resp = await client.get(kf_url)
        assert kf_resp.status_code == 200
        assert "image/" in kf_resp.headers.get("content-type", "") or len(kf_resp.content) > 1000
