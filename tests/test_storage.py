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
    """Verify physical air-gapping of separate user directories."""
    u1_path = temp_storage.get_user_container_path("user-1")
    u2_path = temp_storage.get_user_container_path("user-2")

    assert u1_path != u2_path
    assert u1_path.exists()
    assert u2_path.exists()
    assert "user-user-1" in str(u1_path)
    assert "user-user-2" in str(u2_path)


def test_decoupled_vault_and_distribution(temp_storage: MultiTenantStorageService):
    """Verify creative vault is completely decoupled from distribution channels."""
    vault = temp_storage.get_creative_vault_path("user-1", "delhi_wfh")
    char_path = temp_storage.get_character_path("user-1", "delhi_wfh", "char_aaradhya")
    ep_path = temp_storage.get_episode_path("user-1", "delhi_wfh", "ep001")
    chan_path = temp_storage.get_channel_path("user-1", "yt_main")

    assert "creative_vault" in str(vault)
    assert "characters" in str(char_path)
    assert "episodes" in str(ep_path)
    assert "distribution" in str(chan_path)
    assert "channels" in str(chan_path)


@pytest.mark.asyncio
async def test_atomic_json_save_load(temp_storage: MultiTenantStorageService):
    """Verify atomic persistence and reading of JSON metadata."""
    target_file = temp_storage.get_creative_vault_path("user-1", "show-a") / "meta.json"
    payload = {"title": "Test Show", "status": "active", "views": 1000}

    await temp_storage.save_json(target_file, payload)
    loaded = await temp_storage.load_json(target_file)

    assert loaded == payload
