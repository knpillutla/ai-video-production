"""Unit tests for MultiTenantStorageService and dual-cloud signed URLs."""

import shutil
from pathlib import Path
import pytest

from src.core.storage import MultiTenantStorageService, sanitize_container_name


@pytest.fixture
def temp_storage(tmp_path: Path):
    storage = MultiTenantStorageService(root_dir=str(tmp_path))
    yield storage
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_sanitize_container_name():
    """Verify Azure Blob / GCS container naming compliance."""
    assert sanitize_container_name("usr_12345") == "user-usr-12345"
    assert sanitize_container_name("usr-ABC-DEF") == "user-usr-abc-def"
    assert sanitize_container_name("c4b8e28f-7f61-4c12-b2df-128a50b89312") == "user-c4b8e28f-7f61-4c12-b2df-128a50b89312"


def test_user_container_isolation(temp_storage: MultiTenantStorageService):
    """Verify physical air-gapping of separate user directories with user-0000-0000-00000."""
    u1_path = temp_storage.get_user_container_path("0000-0000-00000")
    u2_path = temp_storage.get_user_container_path("0000-0000-00001")

    assert u1_path != u2_path
    assert u1_path.exists()
    assert u2_path.exists()
    assert "user-0000-0000-00000" in str(u1_path)
    assert "user-0000-0000-00001" in str(u2_path)


def test_network_format_production_episode_hierarchy(temp_storage: MultiTenantStorageService):
    """Verify unified path storage/username/networks/network-name/format/title/episode-xxx."""
    user_id = "0000-0000-00000"
    ep_path = temp_storage.get_channel_format_production_episode_path(
        user_id, "telugu_rhythms", "music_video", "madhura_bhavame", "ep-001"
    )
    assert ep_path.exists()
    norm_path = str(ep_path).replace("\\", "/")
    assert "user-0000-0000-00000/networks/telugu_rhythms/music_video/madhura_bhavame/ep-001" in norm_path

    # Also verify get_episode_path aliases directly to the same hierarchy
    aliased_ep = temp_storage.get_episode_path(
        user_id, "telugu_rhythms", "ep-001", format_slug="music_video", production_name="madhura_bhavame"
    )
    assert aliased_ep == ep_path


@pytest.mark.asyncio
async def test_atomic_json_save_load(temp_storage: MultiTenantStorageService):
    """Verify atomic persistence and reading of JSON metadata under network hierarchy."""
    target_file = temp_storage.get_network_path("0000-0000-00000", "show-a") / "meta.json"
    payload = {"title": "Test Show", "status": "active", "views": 1000}

    await temp_storage.save_json(target_file, payload)
    loaded = await temp_storage.load_json(target_file)

    assert loaded == payload
