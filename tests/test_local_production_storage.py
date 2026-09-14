"""Automated test for 0-cost local video production and disk storage persistence."""

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import create_app


@pytest.mark.asyncio
async def test_local_video_production_persists_to_storage():
    """Verify local production generates MP4 master, scenes, audio stems, and manifests into storage/."""
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Enforce Rule 8: 1 single test only, duration capped to 4 seconds
        payload = {
            "prompt": "Explore Niagara Falls Local Storage Test",
            "title": "Explore Niagara Falls Automated Test",
            "episode_id": "EP-AUTOTEST-01",
            "user_id": "user_krishna_01",
            "production_type": "Theme",
            "tier": "low_cost",
            "duration_seconds": 4.0,
        }

        resp = await client.post("/api/production/local-produce", json=payload)
        assert resp.status_code == 200, f"Expected 200 but got {resp.status_code}: {resp.text}"

        data = resp.json()
        assert data["success"] is True
        assert data["episode_id"] == "EP-AUTOTEST-01"
        assert data["video_url"].startswith("/storage/")
        assert data["video_url"].endswith(".mp4")

        # 1. Verify master MP4 on disk
        mp4_path = Path(data["storage_path"])
        assert mp4_path.exists(), f"MP4 file does not exist on disk: {mp4_path}"
        assert mp4_path.stat().st_size > 10_000

        # 2. Verify scene keyframe images
        ep_dir = mp4_path.parent.parent
        scene1 = ep_dir / "scenes" / "scene_01.jpg"
        scene2 = ep_dir / "scenes" / "scene_02.jpg"
        assert scene1.exists() and scene1.stat().st_size > 1000
        assert scene2.exists() and scene2.stat().st_size > 1000

        # 3. Verify audio stems
        voice1 = ep_dir / "audio_stems" / "voice_01.wav"
        bgm = ep_dir / "audio_stems" / "bgm_master.wav"
        assert voice1.exists() and voice1.stat().st_size > 1000
        assert bgm.exists() and bgm.stat().st_size > 1000

        # 4. Verify project manifest JSON
        manifest = ep_dir / "project_manifest.json"
        assert manifest.exists() and manifest.stat().st_size > 100

        # 5. Verify static file serving from /storage
        stream_resp = await client.get(data["video_url"])
        assert stream_resp.status_code == 200
        assert "video/mp4" in stream_resp.headers.get("content-type", "")
        assert len(stream_resp.content) == mp4_path.stat().st_size
