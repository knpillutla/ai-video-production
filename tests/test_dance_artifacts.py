from pathlib import Path

import pytest

from src.compositor.dance_artifacts import save_dance_script


@pytest.mark.asyncio
async def test_dance_script_is_localized_and_idempotent(tmp_path: Path):
    storyboard = {
        "title_en": "Telangana Dappu Celebration",
        "title_localized": "తెలంగాణ డప్పు వేడుక",
        "lyrics": "చరణం ఒకటి\nచరణం రెండు",
        "suno_tags": "Telangana folk, dappu, female vocals",
        "scenes": [{"scene_index": 0, "choreography_phase": "intro_groove"}],
    }
    path = await save_dance_script(tmp_path, "te", storyboard, "Fallback English Title")
    original = path.read_text(encoding="utf-8")

    same_path = await save_dance_script(tmp_path, "te", {"lyrics": "replacement"}, "Other")

    assert path.name == "dance_script_te.json"
    assert same_path == path
    assert "Telangana Dappu Celebration" in original
    assert "తెలంగాణ డప్పు వేడుక" in original
    assert path.read_text(encoding="utf-8") == original
