"""Targeted test to verify persistence of user inputs (execution_mode, duration, dual_editions)."""
import json
from pathlib import Path
import pytest
from src.api.routes.channel_episodes_scanner import scan_all_channel_episodes


def test_ep001_user_inputs_persistence_and_scanning():
    storage_dir = Path("storage").resolve()
    ep_dir = storage_dir / "user-knpillutla-gmail-com" / "channels" / "skylinediariesindia4k" / "EP-001"
    user_inputs_file = ep_dir / "user_inputs.json"

    assert user_inputs_file.is_file(), "user_inputs.json must exist in EP-001"
    data = json.loads(user_inputs_file.read_text(encoding="utf-8"))

    assert data.get("execution_mode") == "test", "execution_mode must be 'test'"
    assert data.get("duration_seconds") == 120.0, "duration_seconds must be 120.0s"
    assert data.get("dual_editions") is True, "dual_editions must be True"

    episodes = scan_all_channel_episodes(storage_dir, user_id="knpillutla@gmail.com")
    ep001 = next((ep for ep in episodes if ep.get("episode_id") == "EP-001" or ep.get("id") == "EP-001"), None)

    assert ep001 is not None, "EP-001 must be discovered by scanner"
    assert ep001.get("execution_mode") == "test"
    assert ep001.get("duration_seconds") == 120.0
    assert ep001.get("dual_editions") is True
