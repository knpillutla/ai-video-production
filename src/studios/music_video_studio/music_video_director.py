"""Dedicated Multilingual Music Video Studio Directorial Agent.

Synthesizes broadcast-grade music video and dance screenplays matching the exact
produce music video output schema (storyboard.json) with structured rhyming lyrics,
beat-driven staging, authentic regional character archetypes, and zero documentary voiceover.
Extended for global multi-country and multi-language production.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from src.core.telemetry import logger
from src.providers.base import HTTPClientPool
from src.providers.llm.gemini_adapter import get_live_gemini_api_key
from src.services.topic_memory import topic_memory
from src.services.dynamic_character_service import get_or_create_language_archetypes_sync
from src.compositor.genre_strategies.vocal_strategy import VocalStrategy, vocal_gemini_schema
from src.studios.music_video_studio.music_video_samples import get_multilingual_sample_lyrics
from src.studios.music_video_studio.country_music_catalog import (
    COUNTRY_CATALOG,
    SCENERY_ARCHETYPES,
    MUSIC_PERFORMANCE_TYPES,
    SONG_MOODS,
    resolve_network_language_and_country,
)
from src.studios.ambient_world.relax_models import (
    RelaxAudioMasterSpec,
    RelaxPublishingPackage,
    RelaxSceneDirective,
    RelaxScreenplay,
)


def _convert_vocal_storyboard_to_screenplay(sb: dict[str, Any], genre: str, sub_genre: str, archetype: str) -> RelaxScreenplay:
    """Convert produce music video storyboard JSON into RelaxScreenplay container for pipeline compatibility."""
    is_static = (genre == "music/static_vocal")
    title = sb.get("title_en") or sb.get("title_localized") or "Global Music Video"
    topic = sb.get("hook_thesis") or sb.get("title_localized") or title

    audio_spec = RelaxAudioMasterSpec(
        audio_mode="static_vocal_music" if is_static else "music_lipsync",
        spoken_narration_script="",  # Rule 15: Zero spoken documentary voiceover
        singing_lyrics_spec=sb.get("lyrics", ""),
        suno_musical_tags=sb.get("suno_tags", "48kHz stereo, -14 LUFS broadcast master"),
        suno_prompt=sb.get("suno_tags", ""),
        vocal_gender=sb.get("vocal_gender", "female"),
        tempo_bpm=sb.get("tempo_bpm", 100),
        target_lufs=-14.0,
        ducking_db=0.0,
    )

    scenes = []
    sb_scenes = sb.get("scenes", [])
    prompts_model = sb.get("prompts_by_model", {})
    fallback_prompt = prompts_model.get("flux_dev") or prompts_model.get("z_image") or "4K cinematic musical performance"

    if sb_scenes:
        for idx, sc in enumerate(sb_scenes):
            scenes.append(
                RelaxSceneDirective(
                    scene_index=idx + 1,
                    location_hub=sc.get("location_hub") or f"Location {idx + 1}",
                    shot_type=sc.get("camera_shot_type") or ("medium_portrait" if idx == 0 else "wide_cinematic"),
                    camera_rig="locked_tripod" if is_static else "stabilized_gimbal",
                    visual_prompt=sc.get("visual_prompt") or fallback_prompt,
                    motion_prompt=f"Musical performance matching lyrical rhythm: {sc.get('character_pose', 'rhythmic swaying and authentic emotional singing')}.",
                    duration_seconds=float(sc.get("duration_seconds", 10.0)),
                    narration_text="",
                )
            )
    else:
        scenes.append(
            RelaxSceneDirective(
                scene_index=1,
                location_hub="Master Setting",
                shot_type="medium_portrait",
                camera_rig="locked_tripod" if is_static else "stabilized_gimbal",
                visual_prompt=fallback_prompt,
                motion_prompt="Subtle breathing and natural rhythmic swaying to musical tempo.",
                duration_seconds=30.0,
                narration_text="",
            )
        )

    yt = sb.get("youtube_metadata", {})
    publishing = RelaxPublishingPackage(
        ctr_titles=[yt.get("title", title), f"{title} (Official 4K Music Video)"],
        description_with_timestamps=yt.get("description", f"Official music video for {title}."),
        seo_tags=yt.get("tags", ["music video", "4k"]),
    )

    return RelaxScreenplay(
        title=title,
        story_topic=topic,
        recommended_fps=30,  # Rule 14: 30fps for music videos
        cluster="music_video",
        genre=genre,
        sub_genre=sub_genre,
        primary_archetype=archetype,
        primary_language=sb.get("language") or "en",
        audio_master=audio_spec,
        cast=sb.get("characters", []),
        scenes=scenes,
        publishing=publishing,
    )


def _build_offline_multilingual_storyboard(
    genre: str, sub_genre: str, country: str, language: str, culture: str,
    character_desc: str, custom_prompt: Optional[str], duration_seconds: float, num_shots: int,
    vocal_gender: str = "female",
) -> dict[str, Any]:
    """Deterministic offline fallback for mock mode and unit tests (Rule 8 $0.00 spend)."""
    from src.compositor.genre_strategies.vocal_cast_builder import build_vocal_suno_tags
    sp = get_multilingual_sample_lyrics(language=language, country=country)
    is_static = (genre == "music/static_vocal")
    shot_dur = max(5.0, duration_seconds / max(1, num_shots))
    eff_suno_tags = build_vocal_suno_tags(sub_genre, culture, gender=vocal_gender, tempo_bpm=100)

    from src.compositor.genre_strategies.vocal_poses import get_offline_dynamic_scene_poses
    scenes = get_offline_dynamic_scene_poses(
        country=country, culture=culture, character_desc=character_desc,
        gender=vocal_gender, num_scenes=num_shots, setting=sub_genre.replace('_', ' ').title(),
    )
    for sc in scenes:
        sc["duration_seconds"] = shot_dur
        sc["dialogue"] = ""

    return {
        "title_en": sp["title_en"],
        "title_localized": sp["title_localized"],
        "language": language,
        "country": country,
        "tempo_bpm": 100,
        "hook_thesis": f"An evocative {sub_genre} celebrating love and music in {country}.",
        "suno_tags": eff_suno_tags,
        "vocal_gender": vocal_gender,
        "lyrics": sp["lyrics"],
        "prompts_by_model": {
            "z_image": f"4K photograph of lead singer in {country}. {character_desc}",
            "flux_dev": f"Cinematic photograph of lead vocalist in {country}. {character_desc}",
            "flux_pro_ultra": f"35mm Master Prime f/1.4 photograph in {country}. {character_desc}",
            "imagen3": f"Photorealistic 4K portrait in {country}. {character_desc}",
            "midjourney": f"Cinematic still in {country}. {character_desc} --ar 16:9",
        },
        "characters": [
            {
                "name": "Lead Vocalist",
                "gender": "female",
                "age": 25,
                "body_composition": "Natural fit medium-slender graceful build",
                "outfit_description": f"Elegant context-matched designer dress for {country} with modest high neckline, fresh blossoms or pins in hair, sparkling earrings and delicate pendant, slim dress watch, and dainty silver ankle chain anklet",
            }
        ],
        "lyrics_segments": [
            {"start": 4.5, "end": 14.5, "text": sp["s1"], "text_en": sp["s1_en"]},
            {"start": 14.5, "end": 24.5, "text": sp["s2"], "text_en": sp["s2_en"]},
        ],
        "animation_timeline": [
            {"start_time": 0.0, "end_time": duration_seconds, "musical_phase": "intro", "camera_motion": "locked_tripod" if is_static else "slow_push", "effect_type": "floating_bokeh", "intensity": "subtle", "rationale": "Atmospheric depth"}
        ],
        "youtube_metadata": {
            "title": f"{sp['title_en']} | Official 4K Music Video",
            "description": f"Listen to the soulful {sub_genre.replace('_', ' ')} in {language}! 🎵 Produced with authentic regional acoustic mastering.",
            "tags": ["music video", language, country, "4k"],
            "pinned_comment": f"Enjoying this {country} melody? Share your favorite line in the comments!",
            "thumbnail_prompt": f"High-CTR 4K thumbnail capturing dramatic emotional performance in {country}.",
            "category_id": "10",
        },
        "scenes": scenes,
    }



async def generate_music_video_screenplay(
    genre: str = "music/static_vocal",
    sub_genre: Optional[str] = None,
    primary_archetype: Optional[str] = None,
    channel_id: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    camera_motion: str = "locked_tripod",
    user_id: Optional[str] = None,
    country: Optional[str] = None,
    language: Optional[str] = None,
    culture: Optional[str] = None,
    raw_output_path: Optional[os.PathLike | str] = None,
    tier: str = "balanced",
    vocal_gender: Optional[str] = None,
    **kwargs: Any,
) -> RelaxScreenplay:
    """Synthesize dedicated music video screenplay matching produce music video output schema."""
    eff_genre = genre if (genre.startswith("music/") or genre.startswith("dance/")) else "music/static_vocal"
    eff_sub = sub_genre or "romantic_melody"
    eff_scenery = primary_archetype or "local_country_heritage"
    eff_gender = (vocal_gender or kwargs.get("vocal_gender") or "female").lower()

    # Resolve Country & Language (User UI selection takes precedence, network identity is fallback)
    def_lang, def_country, def_culture = resolve_network_language_and_country(channel_id or "default")
    eff_country = country or def_country
    eff_lang = language or def_lang
    eff_culture = culture or def_culture

    # Dynamic Character Retrieval (Rule 12 & LoRA mandate)
    from src.compositor.genre_strategies.vocal_cast_builder import is_kids_song_genre
    is_kids = is_kids_song_genre(eff_sub, custom_prompt)
    females, males = get_or_create_language_archetypes_sync(language=eff_lang, culture=eff_culture, count=50)

    if is_kids:
        char_desc = "Whimsical 3D Pixar-style animated character with expressive eyes and cheerful smile in 3D storybook CGI (zero real human photos)."
    elif eff_gender == "male":
        lm = males[0] if males else None
        char_desc = f"{lm.name}: Age {lm.age}, fit athletic build, {lm.skin} skin, {lm.face}, {lm.hair}, watch on left wrist. SOLO MALE ONLY." if lm else f"Fit lead male vocalist, mid-20s, authentic {eff_culture} features, watch on left wrist. SOLO MALE ONLY."
    elif eff_gender == "duet":
        lf, lm = (females[0] if females else None), (males[0] if males else None)
        char_desc = f"Coordinated romantic couple: {lf.name if lf else 'Lead Female'} & {lm.name if lm else 'Lead Male'}, authentic {eff_culture} features."
    else:
        lf = females[0] if females else None
        char_desc = f"{lf.name}: Age {lf.age}, fit slender graceful build, {lf.skin} skin, {lf.face}, {lf.hair}, 4-zone accessories. SOLO FEMALE ONLY." if lf else f"Fit graceful lead vocalist, mid-20s, authentic {eff_culture} features. SOLO FEMALE ONLY."

    is_test_env = bool(os.getenv("PYTEST_CURRENT_TEST")) or os.getenv("TESTING", "false").lower() == "true"
    is_live_allowed = os.getenv("ALLOW_SINGLE_LIVE_MODEL_TEST", "false").lower() == "true"
    api_key = get_live_gemini_api_key()

    if not api_key or (is_test_env and not is_live_allowed):
        logger.info(f"music_video_offline_mode: language='{eff_lang}' country='{eff_country}' (mock fallback)")
        gemini_inputs = {"mode": "offline_mock", "country": eff_country, "language": eff_lang, "culture": eff_culture, "genre": eff_genre, "character": char_desc, "gender": eff_gender}
        sb_data = _build_offline_multilingual_storyboard(
            genre=eff_genre, sub_genre=eff_sub, country=eff_country, language=eff_lang,
            culture=eff_culture, character_desc=char_desc, custom_prompt=custom_prompt,
            duration_seconds=duration_seconds, num_shots=num_shots, vocal_gender=eff_gender,
        )
        raw_output = sb_data
    else:
        vocal_strat = VocalStrategy()
        sys_prompt = vocal_strat.build_gemini_prompt(
            title=custom_prompt or f"{eff_country} {eff_sub.replace('_', ' ').title()}",
            duration_seconds=int(duration_seconds),
            language=eff_lang,
            genre=eff_sub,
            country=eff_country,
            culture=eff_culture,
            gender=eff_gender,
            theme=custom_prompt or f"{eff_sub} set in {eff_scenery}",
            num_images=num_shots,
            user_id=user_id or "user_krishna_01",
            network=channel_id,
        )
        gemini_inputs = {"model": "gemini-flash-latest", "prompt": sys_prompt, "temperature": 0.7}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": sys_prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": vocal_gemini_schema(), "temperature": 0.7},
        }

        client = HTTPClientPool.get_client()
        logger.info(f"music_video_gemini_request: lang='{eff_lang}' country='{eff_country}' genre='{eff_genre}'")
        resp = await client.post(url, json=payload, timeout=180.0)
        if resp.status_code != 200:
            raise RuntimeError(f"Music Video Screenplay failed (HTTP {resp.status_code}): {resp.text[:300]}")

        raw_output = resp.json()
        raw_text = raw_output.get("candidates", [])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        sb_data = json.loads(raw_text)

    # Guarantee canonical country and language metadata in storyboard output
    sb_data["language"] = sb_data.get("language") or eff_lang
    sb_data["country"] = sb_data.get("country") or eff_country
    sb_data["sub_region"] = sb_data.get("sub_region") or kwargs.get("sub_region", "")
    sb_data["continent"] = sb_data.get("continent") or kwargs.get("continent", "")
    sb_data["culture"] = sb_data.get("culture") or eff_culture
    sb_data["tempo_bpm"] = int(sb_data.get("tempo_bpm") or 100)
    ep_id = kwargs.get("episode_id") or kwargs.get("id")
    if ep_id:
        sb_data["episode_id"] = str(ep_id)
        sb_data["id"] = str(ep_id)

    # Persist gemini inputs, raw output, storyboard.json, and raw_gemini_screenplay.json
    if raw_output_path:
        out_p = Path(raw_output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        (out_p.parent / "gemini_inputs.json").write_text(json.dumps(gemini_inputs, indent=2, ensure_ascii=False), encoding="utf-8")
        (out_p.parent / "raw_gemini_output.json").write_text(json.dumps(raw_output, indent=2, ensure_ascii=False), encoding="utf-8")
        out_p.write_text(json.dumps(sb_data, indent=2, ensure_ascii=False), encoding="utf-8")
        sb_path = out_p.parent / "storyboard.json"
        sb_path.write_text(json.dumps(sb_data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"saved_music_video_storyboard: {sb_path}")

    return _convert_vocal_storyboard_to_screenplay(sb_data, genre=eff_genre, sub_genre=eff_sub, archetype=eff_scenery)
