"""Targeted Unit Test for MusicVideoPipeline and Specialized Music Pipelines ($0.00 Spend)."""

import json
import shutil
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.studios.music_video_studio import (
    MusicVideoPipeline,
    get_music_video_pipeline,
    StaticVocalPipeline,
    SoloSingingPipeline,
    ConcertPipeline,
    DuetRomancePipeline,
    DanceFolkPipeline,
    MassSongPipeline,
)


@pytest.mark.asyncio
async def test_music_pipeline_stage1_script_only():
    """Verify MusicVideoPipeline executes Stage 1 offline, generating storyboard and input/output files."""
    pipe = MusicVideoPipeline(
        user_id="test_user_mv",
        channel_id="test_music_channel",
        episode_id="EP-MV-TEST-01",
        production_name="standalone",
    )
    try:
        res = await pipe.produce(
            genre="music/static_vocal",
            sub_genre="romantic_melody",
            primary_archetype="local_country_heritage",
            prompt="Sakura Spring Blossom",
            country="Japan",
            language="ja",
            duration_seconds=30.0,
            num_shots=1,
            script_only=True,
        )

        assert res["success"] is True
        assert res["stage"] == 1
        assert res["current_stage"] == 1
        assert res["script"] is not None
        assert res["script"]["language"] == "ja"
        assert res["script"]["country"] == "Japan"
        assert res["script"]["vocal_gender"] in ("female", "male")
        assert len(res["script"]["lyrics_segments"]) > 0

        # Verify disk artifacts including gemini_inputs, raw_gemini_output, and user_inputs
        assert (pipe.ep_dir / "storyboard.json").exists()
        assert (pipe.ep_dir / "pipeline_state.json").exists()
        assert (pipe.ep_dir / "episode_manifest.json").exists()
        assert (pipe.ep_dir / "user_inputs.json").exists()
        assert (pipe.ep_dir / "gemini_inputs.json").exists()
        assert (pipe.ep_dir / "raw_gemini_output.json").exists()

        u_inputs = json.loads((pipe.ep_dir / "user_inputs.json").read_text("utf-8"))
        assert u_inputs["language"] == "ja"
        assert u_inputs["country"] == "Japan"

        g_inputs = json.loads((pipe.ep_dir / "gemini_inputs.json").read_text("utf-8"))
        assert "language" in g_inputs or "prompt" in g_inputs

        pipe_state = json.loads((pipe.ep_dir / "pipeline_state.json").read_text("utf-8"))
        assert pipe_state["current_stage"] == 1
        assert pipe_state["stage_approvals"]["script"] is True

        # Test Idempotency (re-run reuses storyboard without changes)
        res2 = await pipe.produce(
            genre="music/static_vocal",
            country="Japan",
            language="ja",
            script_only=True,
        )
        assert res2["success"] is True
        assert res2["script"]["title_en"] == res["script"]["title_en"]
    finally:
        if pipe.ep_dir.exists():
            shutil.rmtree(pipe.ep_dir, ignore_errors=True)


def test_specialized_pipelines_factory_dispatch():
    """Verify get_music_video_pipeline instantiates the correct specialized pipeline class."""
    u = "test_user_factory"
    ch = "test_chan_factory"
    ep = "EP-MV-DISPATCH"

    p_static = get_music_video_pipeline("music/static_vocal", u, ch, ep)
    assert isinstance(p_static, StaticVocalPipeline)
    assert p_static.pipeline_type == "static_vocal"

    p_solo = get_music_video_pipeline("music/solo_singer", u, ch, ep)
    assert isinstance(p_solo, SoloSingingPipeline)
    assert p_solo.pipeline_type == "solo_singer"

    p_concert = get_music_video_pipeline("music/concert_live", u, ch, ep)
    assert isinstance(p_concert, ConcertPipeline)
    assert p_concert.pipeline_type == "concert_live"

    p_duet = get_music_video_pipeline("music/duet_romance", u, ch, ep)
    assert isinstance(p_duet, DuetRomancePipeline)
    assert p_duet.pipeline_type == "duet_romance"

    p_dance = get_music_video_pipeline("dance/folk", u, ch, ep)
    assert isinstance(p_dance, DanceFolkPipeline)
    assert p_dance.pipeline_type == "dance_folk"

    p_mass = get_music_video_pipeline("music/mass_song", u, ch, ep)
    assert isinstance(p_mass, MassSongPipeline)
    assert p_mass.pipeline_type == "mass_song"


def test_music_video_api_produce_and_poll():
    """Verify FastAPI routes /api/music-video/produce and /api/music-video/poll-artifacts work offline."""
    app = create_app()
    client = TestClient(app)

    ep_id = "EP-MV-API-TEST-02"
    u_id = "test_user_api"
    ch_id = "test_api_channel"

    try:
        # 1. Produce Stage 1
        resp = client.post(
            "/api/music-video/produce",
            json={
                "prompt": "Morning Himalayan Serenade",
                "channel_id": ch_id,
                "episode_id": ep_id,
                "user_id": u_id,
                "country": "India",
                "language": "hi",
                "culture": "north_indian",
                "genre": "music/concert_live",
                "duration_seconds": 30.0,
                "script_only": True,
                "pipeline_strategy": "manual",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["episode_id"] == ep_id
        assert data["current_stage"] == 1
        assert data["script"]["language"] == "hi"

        # 2. Poll Artifacts
        poll_resp = client.get(
            f"/api/music-video/poll-artifacts?channel_id={ch_id}&episode_id={ep_id}&user_id={u_id}&format=music_video"
        )
        assert poll_resp.status_code == 200
        poll_data = poll_resp.json()
        assert poll_data["format"] == "music_video"
        assert poll_data["stage"] == 1
        assert poll_data["script"] is not None
        assert poll_data["script"]["country"] == "India"

        # 3. Test Country Languages API (Odia, Bengali, Marathi, Kashmiri, Sindhi)
        c_resp = client.get("/api/music-video/country-languages?country=India")
        assert c_resp.status_code == 200
        c_data = c_resp.json()
        assert c_data["country"] == "India"
        codes = [l["code"] for l in c_data["languages"]]
        for req_code in ("bn", "mr", "or", "ks", "sd", "te", "hi", "ta", "kn", "pa"):
            assert req_code in codes, f"Expected language {req_code} in India languages list"
    finally:
        from src.core.storage import storage_service
        p = storage_service.find_episode_path(user_id=u_id, channel_id=ch_id, episode_id=ep_id, format_slug="music_video")
        if p and p.exists():
            shutil.rmtree(p, ignore_errors=True)


def test_vocal_title_card_and_thumbnail_generation(tmp_path: Path):
    """Verify Scene 0 4K title card and automatic thumbnail generation ($0.00 spend)."""
    from PIL import Image
    from src.compositor.vocal_title_card import (
        generate_vocal_title_card,
        create_thumbnail_from_title_card,
        resolve_song_mood_label,
    )

    # 1. Base 4K test image
    base_img = tmp_path / "scene_001.jpg"
    im = Image.new("RGB", (3840, 2160), color=(20, 30, 45))
    im.save(base_img, format="JPEG")

    # 2. Test mood resolution
    mood_lbl = resolve_song_mood_label(sub_genre="soulful_melody", mood="deeply emotional")
    assert "SOULFUL" in mood_lbl

    # 3. Generate 4K Title Card
    card_p = tmp_path / "scene_000_title.jpg"
    res_p = generate_vocal_title_card(
        base_image_path=base_img,
        title_localized="ఆత్మ గానం",
        title_en="Voice of the Soul",
        song_type=mood_lbl,
        language="te",
        output_path=card_p,
    )
    assert res_p.exists()
    assert res_p.stat().st_size > 1000
    with Image.open(res_p) as c_im:
        assert c_im.size == (3840, 2160)

    # 4. Generate Thumbnail from Title Card
    thumb_p = tmp_path / "thumb_ep_te.jpg"
    thumb_res = create_thumbnail_from_title_card(title_card_path=card_p, output_path=thumb_p)
    assert thumb_res.exists()
    assert thumb_res.stat().st_size > 1000
    with Image.open(thumb_res) as t_im:
        assert t_im.size == (1280, 720)


@pytest.mark.asyncio
async def test_country_region_curator_and_cache():
    """Verify 4-tier country hierarchy curator and local disk caching under storage/assets/."""
    from src.studios.music_video_studio.country_region_curator import (
        get_or_curate_country_hierarchy,
        get_all_country_languages_flat,
    )

    # 1. Test India hierarchy
    india_hier = await get_or_curate_country_hierarchy("India")
    assert india_hier["country"] == "India"
    assert india_hier["continent"] == "Asia"
    sub_ids = [s["id"] for s in india_hier["sub_regions"]]
    assert "south_india" in sub_ids
    assert "east_india" in sub_ids
    assert "west_india" in sub_ids
    assert "north_india" in sub_ids

    # 2. Test East India has Odia and Bengali
    east = next(s for s in india_hier["sub_regions"] if s["id"] == "east_india")
    east_langs = [l["code"] for l in east["languages"]]
    assert "bn" in east_langs
    assert "or" in east_langs

    # 3. Test West India has Marathi and Gujarati
    west = next(s for s in india_hier["sub_regions"] if s["id"] == "west_india")
    west_langs = [l["code"] for l in west["languages"]]
    assert "mr" in west_langs
    assert "gu" in west_langs

    # 4. Verify disk cache file exists
    cache_f = Path("storage/assets/geographic_hierarchy/india.json")
    assert cache_f.exists()
    assert cache_f.stat().st_size > 100

    # 5. Test flat languages helper for backward compatibility
    flat = get_all_country_languages_flat(india_hier)
    assert len(flat) >= 12


def test_country_hierarchy_api_endpoints():
    """Verify /api/music-video/country-hierarchy endpoint returns 4-tier structure."""
    app = create_app()
    client = TestClient(app)

    # Test India hierarchy
    resp = client.get("/api/music-video/country-hierarchy?country=India")
    assert resp.status_code == 200
    data = resp.json()
    assert data["country"] == "India"
    assert len(data["sub_regions"]) >= 4

    # Test Spain hierarchy
    resp_es = client.get("/api/music-video/country-hierarchy?country=Spain")
    assert resp_es.status_code == 200
    data_es = resp_es.json()
    assert data_es["country"] == "Spain"
    es_subs = [s["id"] for s in data_es["sub_regions"]]
    assert "andalusia" in es_subs

