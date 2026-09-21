"""Unit tests for multi-language production, visual keyframe reuse, and language-scoped idempotency."""

import pytest
from pathlib import Path
from uuid import uuid4

from src.mcp.topic_memory.server import check_topic_duplicate, remember_topic, clear_topic_vault


@pytest.mark.asyncio
async def test_topic_memory_language_scoped_idempotency():
    """Verify that same topic with same language blocks duplicate, but allows distinct languages."""
    test_user_id = f"test_user_{uuid4().hex[:8]}"
    topic_title = "Majestic Himalayan Glacier Expedition"

    # Step 1: Initial check for Telugu should pass
    check_te_1 = await check_topic_duplicate(
        topic=topic_title,
        metadata={"genre": "nature", "language": "te"},
        user_id=test_user_id,
        language="te",
    )
    assert not check_te_1["is_duplicate"]

    # Step 2: Record Telugu release in Topic Memory
    await remember_topic(
        topic=topic_title,
        metadata={"genre": "nature", "language": "te"},
        final_story="Telugu commentary on glacier waters.",
        episode_id="ep_te_01",
        show_slug="himalayan_glacier",
        user_id=test_user_id,
    )

    # Step 3: Re-running for Telugu MUST be blocked as duplicate (idempotent guard)
    check_te_2 = await check_topic_duplicate(
        topic=topic_title,
        metadata={"genre": "nature", "language": "te"},
        user_id=test_user_id,
        language="te",
    )
    assert check_te_2["is_duplicate"]
    assert "already exists for language 'te'" in check_te_2["alert_message"]

    # Step 4: Running for Hindi MUST be allowed (legitimate regional localization release)
    check_hi_1 = await check_topic_duplicate(
        topic=topic_title,
        metadata={"genre": "nature", "language": "hi"},
        user_id=test_user_id,
        language="hi",
    )
    assert not check_hi_1["is_duplicate"]

    # Step 5: Record Hindi release in Topic Memory
    await remember_topic(
        topic=topic_title,
        metadata={"genre": "nature", "language": "hi"},
        final_story="Hindi commentary on glacier peaks.",
        episode_id="ep_hi_01",
        show_slug="himalayan_glacier",
        user_id=test_user_id,
    )

    # Step 6: Re-running for Hindi MUST now also be blocked
    check_hi_2 = await check_topic_duplicate(
        topic=topic_title,
        metadata={"genre": "nature", "language": "hi"},
        user_id=test_user_id,
        language="hi",
    )
    assert check_hi_2["is_duplicate"]
    assert "already exists for language 'hi'" in check_hi_2["alert_message"]

    # Step 7: A third language (e.g. Kannada 'kn') remains allowed
    check_kn = await check_topic_duplicate(
        topic=topic_title,
        metadata={"genre": "nature", "language": "kn"},
        user_id=test_user_id,
        language="kn",
    )
    assert not check_kn["is_duplicate"]


@pytest.mark.asyncio
async def test_multilang_batch_execution_and_caching(monkeypatch, tmp_path):
    """Test produce_video multi-language batch execution and master filename localization."""
    from scripts.produce_video import run_production

    clear_topic_vault()
    import uuid
    unique_title = f"Tokyo Cyberpunk Neon Market {uuid.uuid4().hex[:6]}"
    # Run in local mode with dry_run=True (zero paid API calls)
    res = await run_production(
        title=unique_title,
        genre="travel",
        media_format="walking_tour",
        language="te,hi",
        duration=10,
        local=True,
        dry_run=True,
        auto_confirm=True,
    )

    # Must return a list with 2 completed video paths
    assert isinstance(res, list)
    assert len(res) == 2
    path_te, path_hi = Path(res[0]), Path(res[1])

    # Localized master video filenames
    assert "_te.mp4" in path_te.name
    assert "_hi.mp4" in path_hi.name

    # Both must be created in the same parent directory (shared episode assets)
    assert path_te.parent == path_hi.parent

    # Verify both localized thumbnails exist
    thumb_dir = path_te.parent.parent / "thumbnails"
    assert (thumb_dir / "thumb_ep01_te.jpg").is_file()
    assert (thumb_dir / "thumb_ep01_hi.jpg").is_file()


@pytest.mark.asyncio
async def test_duplicate_rerun_preflight_blocked(capsys):
    """Verify that re-running for the same language is blocked by the idempotency duplicate guard."""
    from scripts.produce_video import run_production
    title = f"Zyq{uuid4().hex[:10]} Qwv{uuid4().hex[:10]}"

    # First run for Tamil
    res1 = await run_production(
        title=title,
        language="ta",
        duration=10,
        local=True,
        dry_run=True,
        auto_confirm=True,
    )
    assert res1 is not None

    # Immediate second run for Tamil with same title
    res2 = await run_production(
        title=title,
        language="ta",
        duration=10,
        local=True,
        dry_run=True,
        auto_confirm=True,
    )
    # Must be blocked and return None
    assert res2 is None
    captured = capsys.readouterr()
    assert "DUPLICATE CONTENT ALERT" in captured.out
    assert "already exists for language 'ta'" in captured.out


@pytest.mark.asyncio
async def test_llm_variation_planner_retries_a_duplicate_premise(monkeypatch):
    """Recurring briefs get a new LLM premise, with Topic Memory as final guard."""
    from importlib import import_module
    from src.services.topic_planner import get_fresh_original_topic

    planner_module = import_module("src.services.topic_planner")

    user_id = f"variation_user_{uuid4().hex[:8]}"
    first = "Swiss Alps Glacier Valley Expedition"
    second = "Himalayan High Pass Shepherds Journey"
    await remember_topic(
        topic=first, metadata={"genre": "mountains", "language": "en"},
        episode_id="existing-mountain", user_id=user_id,
    )

    prompts: list[str] = []

    class FakePlanner:
        async def generate_text(self, prompt, **_kwargs):
            prompts.append(prompt)
            return first if len(prompts) == 1 else second

    monkeypatch.setattr(planner_module, "is_mock_mode", lambda: False)
    monkeypatch.setattr(planner_module, "GeminiLLMAdapter", FakePlanner)
    result = await get_fresh_original_topic(
        "produce videos of mountains", language="en", user_id=user_id,
    )

    assert result == second
    assert first in prompts[0]
