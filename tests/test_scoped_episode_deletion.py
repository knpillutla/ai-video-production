"""Targeted unit tests verifying scoped episode deletion safety."""

import shutil
from pathlib import Path
import pytest
from src.api.routes.local_production import delete_episode_artifacts


@pytest.mark.asyncio
async def test_scoped_deletion_preserves_other_formats(tmp_path, monkeypatch):
    # Setup mock network structure:
    # user_container / networks / test_net / documentary / tour_a / ep-001
    # user_container / networks / test_net / relaxation / nature_b / ep-001
    user_cont = tmp_path / "user-0000-0000-00000"
    doc_ep = user_cont / "networks" / "test_net" / "documentary" / "tour_a" / "ep-001"
    rel_ep = user_cont / "networks" / "test_net" / "relaxation" / "nature_b" / "ep-001"
    doc_ep.mkdir(parents=True)
    rel_ep.mkdir(parents=True)

    (doc_ep / "data.txt").write_text("doc")
    (rel_ep / "data.txt").write_text("rel")

    monkeypatch.setattr("src.core.storage.storage_service.get_user_container_path", lambda uid: user_cont)
    monkeypatch.setattr("src.core.storage.storage_service.get_network_path", lambda uid, cid: user_cont / "networks" / cid)

    # Delete ONLY the documentary episode
    res = await delete_episode_artifacts(
        episode_id="ep-001",
        channel_id="test_net",
        format="documentary",
        production_name="tour_a",
        user_id="user-0000-0000-00000",
    )

    assert res["success"] is True
    # Documentary episode folder itself should be completely removed from disk
    assert not doc_ep.exists()
    # Empty parent production folder 'tour_a' should be pruned cleanly
    assert not doc_ep.parent.exists()
    # Relaxation episode and its parent MUST be preserved!
    assert rel_ep.exists()
    assert (rel_ep / "data.txt").read_text() == "rel"


@pytest.mark.asyncio
async def test_deletion_preserves_parent_if_other_episodes_exist(tmp_path, monkeypatch):
    user_cont = tmp_path / "user-0000-0000-00000"
    ep1 = user_cont / "networks" / "test_net" / "documentary" / "tour_a" / "ep-001"
    ep2 = user_cont / "networks" / "test_net" / "documentary" / "tour_a" / "ep-002"
    ep1.mkdir(parents=True)
    ep2.mkdir(parents=True)

    (ep1 / "data.txt").write_text("ep1")
    (ep2 / "data.txt").write_text("ep2")

    monkeypatch.setattr("src.core.storage.storage_service.get_user_container_path", lambda uid: user_cont)
    monkeypatch.setattr("src.core.storage.storage_service.get_network_path", lambda uid, cid: user_cont / "networks" / cid)

    res = await delete_episode_artifacts(
        episode_id="ep-001",
        channel_id="test_net",
        format="documentary",
        production_name="tour_a",
        user_id="user-0000-0000-00000",
    )

    assert res["success"] is True
    assert not ep1.exists()
    # Parent 'tour_a' must remain because ep-002 still exists!
    assert ep1.parent.exists()
    assert ep2.exists()
    assert (ep2 / "data.txt").read_text() == "ep2"

