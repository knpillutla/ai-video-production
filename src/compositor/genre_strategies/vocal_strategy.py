"""Vocal Song & Lyrical Video Genre Strategy.

Orchestration config:
1. Gemini: Original poetic rhyming lyrics, Suno music tags, multi-model image prompts, and timed lyrics.
2. Suno v3.5 Pro: Full commercial vocal song synthesis matching mood & gender.
3. 4K Keyframe: Z-Image Turbo default (with multi-model prompt alternatives in script JSON).
4. Local FFmpeg ($0.00): Song-duration lock, center-screen native lyrics burn-in, -14 LUFS mastering.
"""

from __future__ import annotations

import re
from typing import Any

from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check
from src.compositor.genre_strategies.vocal_cast_builder import (
    build_cast_and_visual_directives,
    build_vocal_suno_tags,
    is_kids_song_genre,
)


def vocal_gemini_schema() -> dict:
    """Return strict JSON schema for vocal lyrical video structured output."""
    character = {
        "type": "OBJECT",
        "properties": {"name": {"type": "STRING"}, "gender": {"type": "STRING"}, "age": {"type": "INTEGER"}, "body_composition": {"type": "STRING"}, "outfit_description": {"type": "STRING"}},
        "required": ["name", "gender", "age", "body_composition", "outfit_description"],
    }
    lyrics_seg = {
        "type": "OBJECT",
        "properties": {"start": {"type": "NUMBER"}, "end": {"type": "NUMBER"}, "text": {"type": "STRING"}, "text_en": {"type": "STRING"}},
        "required": ["start", "end", "text", "text_en"],
    }
    prompts_model = {
        "type": "OBJECT",
        "properties": {"z_image": {"type": "STRING"}, "flux_dev": {"type": "STRING"}, "flux_pro_ultra": {"type": "STRING"}, "imagen3": {"type": "STRING"}, "midjourney": {"type": "STRING"}},
        "required": ["z_image", "flux_dev", "flux_pro_ultra", "imagen3", "midjourney"],
    }
    youtube_meta = {
        "type": "OBJECT",
        "properties": {"title": {"type": "STRING"}, "description": {"type": "STRING"}, "tags": {"type": "ARRAY", "items": {"type": "STRING"}}, "pinned_comment": {"type": "STRING"}, "thumbnail_prompt": {"type": "STRING"}, "category_id": {"type": "STRING"}},
        "required": ["title", "description", "tags", "pinned_comment"],
    }
    anim_cue = {
        "type": "OBJECT",
        "properties": {"start_time": {"type": "NUMBER"}, "end_time": {"type": "NUMBER"}, "musical_phase": {"type": "STRING"}, "camera_motion": {"type": "STRING"}, "effect_type": {"type": "STRING"}, "intensity": {"type": "STRING"}, "rationale": {"type": "STRING"}},
        "required": ["start_time", "end_time", "camera_motion", "effect_type"],
    }
    return {
        "type": "OBJECT",
        "properties": {
            "title_en": {"type": "STRING"},
            "title_localized": {"type": "STRING"},
            "song_type": {"type": "STRING"},
            "mood": {"type": "STRING"},
            "language": {"type": "STRING"},
            "country": {"type": "STRING"},
            "tempo_bpm": {"type": "INTEGER"},
            "hook_thesis": {"type": "STRING"},
            "suno_tags": {"type": "STRING"},
            "vocal_gender": {"type": "STRING"},
            "lyrics": {"type": "STRING"},
            "prompts_by_model": prompts_model,
            "characters": {"type": "ARRAY", "items": character},
            "lyrics_segments": {"type": "ARRAY", "items": lyrics_seg},
            "animation_timeline": {"type": "ARRAY", "items": anim_cue},
            "youtube_metadata": youtube_meta,
            "scenes": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "scene_index": {"type": "INTEGER"},
                        "duration_seconds": {"type": "NUMBER"},
                        "location_hub": {"type": "STRING"},
                        "character_pose": {"type": "STRING"},
                        "camera_shot_type": {"type": "STRING"},
                        "visual_prompt": {"type": "STRING"},
                        "dialogue": {"type": "STRING"},
                    },
                    "required": ["scene_index", "duration_seconds", "location_hub", "character_pose", "camera_shot_type", "visual_prompt"],
                },
            },
        },
        "required": [
            "title_en", "title_localized", "hook_thesis", "suno_tags",
            "vocal_gender", "lyrics", "prompts_by_model", "characters",
            "lyrics_segments", "youtube_metadata", "scenes",
        ],
    }


def _format_lyrics_directives(language: str, culture: str, theme: str, duration_seconds: int = 60) -> str:
    """Compile culturally authentic lyrical verse instructions scaled to target duration."""
    lang = (language or "en").lower()
    if duration_seconds > 150:
        len_hint = "Full 3.5-min song: 6-8 structured stanzas (~28-36 lines). Use [Intro], [Chorus/Mukhda] (repeated), [Verse 1/Antra 1], [Chorus], [Verse 2/Antra 2], [Bridge/Charanam], [Verse 3], [Final Chorus & Outro]."
    elif duration_seconds > 75:
        len_hint = "Full 2-min song: 4 structured stanzas (~16-20 lines). Use [Chorus/Mukhda], [Verse 1/Antra 1], [Chorus], [Verse 2/Antra 2], [Outro]."
    else:
        len_hint = "Compact 1-min song: 2 stanzas (~8-12 lines) with [Mukhda] and [Antra]."

    base = f"1. Write complete rhyming lyrics in NATIVE SCRIPT of {language} celebrating '{theme}'.\n"
    if lang in ("te", "ta", "kn", "ml"):
        base += "2. Cultural meter (Pallavi, Anupallavi, Charanam) with strict prasa & chandas.\n"
    elif lang in ("hi", "pa", "bn", "ur"):
        base += "2. Cultural meter (Mukhda chorus, Antras) with strict qafiya & radif.\n"
    else:
        base += "2. Metric rhyme scheme and radio-friendly melodic hook.\n"
    return f"{base}3. SONG STRUCTURE & DURATION SCALE: {len_hint}\n"


class VocalStrategy:
    """Strategy for full-length songs with single 4K visual art and center-screen lyrics."""

    genre_id = "vocal"
    default_fps = 30
    audio_mode = "song"
    lipsync_mode = "none"
    enable_voice_over = False
    enable_bgm = True

    def build_gemini_prompt(
        self,
        title: str,
        duration_seconds: int,
        language: str,
        genre: str = "romantic_melody",
        idea: str | None = None,
        art_style: str | None = None,
        culture_ctx: Any | None = None,
        character_name: str | None = None,
        music_style: str | None = None,
        similar_to: str | None = None,
        country: str | None = None,
        culture: str | None = None,
        gender: str | None = None,
        theme: str | None = None,
        **kwargs: Any,
    ) -> str:
        if kwargs.get("duet") or str(gender).lower() == "duet":
            eff_gender = "duet"
        elif kwargs.get("solo_male") or str(gender).lower() == "male":
            eff_gender = "male"
        elif kwargs.get("solo_female") or str(gender).lower() == "female":
            eff_gender = "female"
        else:
            eff_gender = (gender or kwargs.get("vocal_gender") or "duet").lower()
        eff_country = country or "India"
        if not culture:
            from src.studios.music_video_studio.country_music_catalog import resolve_culture_for_country_and_language
            eff_culture = resolve_culture_for_country_and_language(eff_country, language)
        else:
            eff_culture = culture
        eff_theme = theme or kwargs.get("theme") or idea or "soulful romantic melody"

        user_id = str(kwargs.get("user_id") or "default_user")
        network = kwargs.get("network")
        ep_num = kwargs.get("episode_number")

        from src.services.character_archetypes import (
            get_and_increment_production_slot,
            resolve_cast_archetypes,
        )
        slot = get_and_increment_production_slot(user_id=user_id, network=network, episode_number=ep_num)
        fem_spec, male_spec = resolve_cast_archetypes(slot=slot, culture=eff_culture, language=language)

        is_kids = is_kids_song_genre(genre, eff_theme)
        cast_directive, neg_constraints = build_cast_and_visual_directives(
            slot=slot, fem=fem_spec, male=male_spec, culture=eff_culture,
            setting=eff_theme, gender=eff_gender, is_kids=is_kids,
        )

        suno_hint = build_vocal_suno_tags(genre, eff_culture, gender=eff_gender, tempo_bpm=100)

        is_generic_title = not title or any(k in str(title).lower() for k in ("wfh confusions", "melody - lyrical song", "custom screenplay", "standalone", "new song", "soulful romantic melody"))
        if is_generic_title:
            title_directive = (
                f"- TITLE INVENTION (CRITICAL DIRECTIVE):\n"
                f"  * Invent an evocative, poetic, and culturally authentic title for this song celebrating '{eff_theme}'.\n"
                f"  * 'title_en': Return ONLY the pure Romanized song title in English alphabet (e.g. 'Preyasi Priyatama', 'Sous Le Ciel'). Prohibit 'Episode X'.\n"
                f"  * 'title_localized': Native script title followed by Romanized title in parentheses."
            )
        else:
            clean_in_title = re.sub(r"\s*-\s*episode\s*\d+", "", str(title), flags=re.IGNORECASE).strip()
            title_directive = f"- Title: {clean_in_title} ('title_en' is clean Romanized song title; 'title_localized' is native script)"

        num_images = int(kwargs.get("num_images") or 1)
        from src.compositor.genre_strategies.vocal_poses import build_environmental_pose_directive
        pose_directive = build_environmental_pose_directive(
            gender=eff_gender, theme=eff_theme, culture=eff_culture, num_scenes=num_images,
        )

        if eff_gender == "male":
            vocal_perspective_directive = "5. VOCAL PERFORMER PERSPECTIVE (SOLO MALE):\n   * Write all lyrics strictly from the first-person perspective of the SOLO MALE lead with male grammatical endings (e.g. 'गाता हूँ', 'मेरा'). Strictly NO female lines.\n\n"
        elif eff_gender == "female":
            vocal_perspective_directive = "5. VOCAL PERFORMER PERSPECTIVE (SOLO FEMALE):\n   * Write all lyrics strictly from the first-person perspective of the SOLO FEMALE lead with female grammatical endings (e.g. 'गाती हूँ', 'मेरी'). Strictly NO male lines.\n\n"
        else:
            vocal_perspective_directive = "5. VOCAL PERFORMER PERSPECTIVE (DUET):\n   * Structure the lyrics with alternating call-and-response couplets between [Male Lead] and [Female Lead], joining in harmony for [Chorus / Both].\n\n"

        ref_line = f"- Musical Reference / Similar To: {similar_to}\n" if similar_to else ""
        art_line = f"- Visual & Architectural Art Style: {art_style}\n" if art_style else ""

        return (
            f"You are an acclaimed master lyricist, music director, and visual artist.\n"
            f"Create a full broadcast-grade musical release in the {language.upper()} language.\n\n"
            f"CREATIVE DIRECTIVES:\n"
            f"{title_directive}\n"
            f"- Setting / Premise: {eff_theme}\n"
            f"- SETTING & SCENIC LOCATION FIDELITY: {eff_theme.title()}\n"
            f"- MULTI-SCENE ROTATION ({num_images} SCENES): Rotate camera perspective and framing across scenes matching {eff_theme}.\n"
            f"- Country / Region: {eff_country} | Culture: {eff_culture}\n"
            f"- Music Tone: {genre.replace('_', ' ').title()} | Vocal Performer: {eff_gender.upper()}\n"
            f"{ref_line}{art_line}"
            f"- Song Categorization: Differentiate clearly between 'SOULFUL MELODY' (deep emotional pathos, acoustic yearning, gentle strings, melancholy) vs 'ROMANTIC SONG' (joyous love, celebratory couple bond) vs 'MASS SONG WITH MASS BEATS' (high-energy mass commercial dance, thumping dappu drums, fast teenmaar rhythm, brass, whistle drops, explosive hook couplets) vs 'ENERGETIC FOLK' (mass dance, festive). Populate 'song_type' and 'mood' accordingly.\n"
            f"- Suno Music Tags Reference: '{suno_hint}'\n\n"
            f"LYRICS SPECIFICATION:\n"
            f"{_format_lyrics_directives(language, eff_culture, eff_theme, duration_seconds=duration_seconds)}"
            f"3. DUAL-LINE SUBTITLES (MANDATORY): For every line in 'lyrics_segments', provide:\n"
            f"   * 'text': Native script of {language}.\n"
            f"   * 'text_en': Romanized transliteration + concise English meaning.\n"
            f"4. First segment starts after the opening title card (~6-8s), pacing across {duration_seconds}s.\n"
            f"{vocal_perspective_directive}"
            f"{pose_directive}"
            f"CHARACTER & VISUAL STAGING DIRECTIVE:\n"
            f"{cast_directive}\n"
            f"MANDATORY NEGATIVE CONSTRAINTS (Inject into visual prompts):\n"
            f"Negative: {neg_constraints}\n\n"
            f"MULTI-MODEL PROMPT ADAPTATION (prompts_by_model):\n"
            f"Generate tailored prompts for z_image, flux_dev, flux_pro_ultra, imagen3, midjourney reflecting the exact character modality and setting above.\n\n"
            f"VISUAL EFFECTS & ANIMATIONS (animation_timeline):\n"
            f"Direct 3-5 timed particle cues (camera_motion='static_tripod'): effect_type in ('floating_petals_up', 'golden_fireflies', 'golden_light_leak', 'shimmering_sparkles', 'floating_petals_down', 'romantic_bokeh_drift', 'monsoon_rain_mist').\n"
        )

    def build_gemini_schema(self) -> dict:
        return vocal_gemini_schema()

    def validate_storyboard(self, storyboard: dict) -> list[str]:
        issues = default_storyboard_sanity_check(storyboard)
        if not storyboard.get("lyrics"):
            issues.append("vocal storyboard has no lyrics")
        if not storyboard.get("suno_tags"):
            issues.append("vocal storyboard has no suno_tags")
        if not storyboard.get("prompts_by_model"):
            issues.append("vocal storyboard missing prompts_by_model")
        return issues

    def get_directorial_template_name(self) -> str:
        return "dance_choreography.md"

    def get_ffmpeg_filter_args(self, fps: int, duration: float) -> list[str]:
        return [
            "-filter_complex",
            "[0:v]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,unsharp=5:5:0.8:5:5:0.0[v_out];"
            "[1:a]loudnorm=I=-14.0:TP=-1.0:LRA=7.0[a_out]",
            "-map", "[v_out]", "-map", "[a_out]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        ]


__all__ = ["VocalStrategy", "vocal_gemini_schema"]
