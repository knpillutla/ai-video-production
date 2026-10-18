"""Targeted unit tests verifying persistence of Auto/Manual and Test/Prod settings."""

import json
from pathlib import Path
import pytest
from src.api.routes.local_production import update_episode_inputs


@pytest.mark.asyncio
async def test_update_episode_inputs_persists_auto_and_prod(tmp_path, monkeypatch):
    user_cont = tmp_path / "user-0000"
    ep_dir = user_cont / "networks" / "test_channel" / "documentary" / "tour_1" / "EP-001"
    ep_dir.mkdir(parents=True)

    # Initial state
    u_file = ep_dir / "user_inputs.json"
    u_file.write_text(json.dumps({"prompt": "Scenic Alps", "execution_mode": "test", "pipeline_strategy": "manual"}))
    p_file = ep_dir / "pipeline_state.json"
    p_file.write_text(json.dumps({"current_stage": 1, "execution_mode": "test", "pipeline_strategy": "manual"}))

    monkeypatch.setattr("src.core.storage.storage_service.get_user_container_path", lambda uid: user_cont)
    monkeypatch.setattr("src.core.storage.storage_service.get_network_path", lambda uid, cid: user_cont / "networks" / cid)

    # User toggles to auto and prod in the UI
    res = await update_episode_inputs(
        episode_id="EP-001",
        payload={"execution_mode": "prod", "pipeline_strategy": "auto"},
        channel_id="test_channel",
        format="documentary",
        production_name="tour_1",
        user_id="user-0000",
    )

    assert res["success"] is True
    saved_inputs = json.loads(u_file.read_text("utf-8"))
    assert saved_inputs["execution_mode"] == "prod"
    assert saved_inputs["pipeline_strategy"] == "auto"

    saved_pipe = json.loads(p_file.read_text("utf-8"))
    assert saved_pipe["execution_mode"] == "prod"
    assert saved_pipe["pipeline_strategy"] == "auto"


@pytest.mark.asyncio
async def test_update_episode_inputs_creates_files_if_missing(tmp_path, monkeypatch):
    user_cont = tmp_path / "user-0000"
    ep_dir = user_cont / "networks" / "test_channel" / "documentary" / "tour_1" / "EP-002"
    ep_dir.mkdir(parents=True)

    monkeypatch.setattr("src.core.storage.storage_service.get_user_container_path", lambda uid: user_cont)
    monkeypatch.setattr("src.core.storage.storage_service.get_network_path", lambda uid, cid: user_cont / "networks" / cid)

    # Call update_inputs when user_inputs.json doesn't exist yet
    res = await update_episode_inputs(
        episode_id="EP-002",
        payload={"execution_mode": "test", "pipeline_strategy": "manual"},
        channel_id="test_channel",
        format="documentary",
        production_name="tour_1",
        user_id="user-0000",
    )

    assert res["success"] is True
    u_file = ep_dir / "user_inputs.json"
    assert u_file.is_file()
    saved_inputs = json.loads(u_file.read_text("utf-8"))
    assert saved_inputs["execution_mode"] == "test"
    assert saved_inputs["pipeline_strategy"] == "manual"
