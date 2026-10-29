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
    build_cast_and_visual_directives, build_vocal_suno_tags, is_kids_song_genre,
)


from src.compositor.genre_strategies.vocal_schema import vocal_gemini_schema



def _format_lyrics_directives(language: str, culture: str, theme: str, duration_seconds: int = 60) -> str:
    """Compile culturally authentic lyrical verse instructions scaled to target duration."""
    lang = (language or "en").lower()
    if duration_seconds > 150:
        len_hint = "Full 3.5-min song: 6-8 structured stanzas (~28-36 lines). Use [Intro], [Chorus/Mukhda - Catchy Hummable Hook] (repeated), [Verse 1/Antra 1], [Chorus], [Verse 2/Antra 2], [Bridge/Charanam], [Verse 3], [Final Chorus & Outro]."
    elif duration_seconds > 75:
        len_hint = "Full 2-min song: 4 structured stanzas (~16-20 lines). Use [Chorus/Mukhda - Catchy Hummable Hook], [Verse 1/Antra 1], [Chorus], [Verse 2/Antra 2], [Outro]."
    else:
        len_hint = "Compact 1-min song: 2 stanzas (~8-12 lines) with [Mukhda - Catchy Hook] and [Antra]."

    is_classical_sangam = any(k in f"{theme} {culture}".lower() for k in ("carnatic", "sangam", "narumugaye", "raga", "classical"))
    if is_classical_sangam:
        meter_spec = "Classical Sangam / Raga poetry (Pallavi, Anupallavi, Charanam) with evocative nature metaphors (lotus, twilight, jasmine, sacred river, fragrant breeze), high-literary vocabulary, and yearning romantic Sringara rasa."
    elif lang in ("te", "ta", "kn", "ml"):
        meter_spec = "Cultural meter (Pallavi, Anupallavi, Charanam) with strict prasa, anuprasa, and melodic chandas."
    elif lang in ("hi", "pa", "bn", "ur"):
        meter_spec = "Cultural meter (Mukhda chorus, Antras) with strict qafiya, radif, and poetic flow."
    else:
        meter_spec = "Metric rhyme scheme, infectious rhythm, and radio-friendly melodic hook."
    lang_name = "ENGLISH" if lang == "en" else f"NATIVE SCRIPT of {language}"
    return (
        f"1. Write complete rhyming lyrics in {lang_name} celebrating '{theme}'.\n"
        f"2. CATCHY & HUMMABLE HIGH-CTR HOOK MANDATE:\n"
        f"   - Opening Chorus/Pallavi/Mukhda couplet MUST be extremely catchy, simple, rhythmically symmetrical, and instantly hummable. Repeat signature hook 3-4 times across stanzas for retention.\n"
        f"3. SUNO COMPOSITION INSTRUCTIONS & SECTION HEADERS:\n"
        f"   - Embed descriptive bracketed cue tags in 'lyrics': e.g. [Catchy Melodic Hook], [Hummable Chorus], [Verse 1 - Rhythmic Flow], [Instrumental Whistle Hook], [Antra 2], [Explosive Hook Refrain], [Outro]. Suno utilizes these cue headers to compose musical transitions and melodic hooks.\n"
        f"4. METRIC & CULTURAL CADENCE: {meter_spec}\n"
        f"5. SONG STRUCTURE & DURATION SCALE: {len_hint}\n"
        f"6. VOCAL RANGE & CASING: Standard sentence casing only (NO ALL-CAPS or '!!!'). Anchor male vocals in a warm, resonant chest-voice register (zero high-pitch strain or cracking).\n"
    )


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
        is_lang_en = (language or "en").lower().strip() == "en"
        eff_country = country or ("USA" if is_lang_en else None)
        eff_culture = culture or ("western" if is_lang_en else None)
        eff_theme = theme or kwargs.get("theme") or idea or "soulful romantic melody"

        user_id = str(kwargs.get("user_id") or "default_user")
        network = kwargs.get("network")
        ep_num = kwargs.get("episode_number")

        from src.services.character_archetypes import (
            get_and_increment_production_slot,
            resolve_cast_archetypes,
        )
        slot = get_and_increment_production_slot(user_id=user_id, network=network, episode_number=ep_num)
        chars_req = kwargs.get("chars") or kwargs.get("chars_arg") or kwargs.get("character_name")
        fem_spec, male_spec = resolve_cast_archetypes(slot=slot, culture=eff_culture, language=language, custom_names=chars_req)

        is_kids = is_kids_song_genre(genre, eff_theme)
        is_jugalbandi = bool(kwargs.get("jugalbandi") or any(k in f"{genre} {eff_theme}".lower() for k in ("jugalbandi", "sawaal", "jawaab")))
        is_va = bool(kwargs.get("virtual_artist") or "virtual_artist" in genre or "artist" in genre)
        costume_hint = kwargs.get("costume_style") or kwargs.get("costume") or kwargs.get("costume_hint")
        cast_directive, neg_constraints = build_cast_and_visual_directives(
            slot=slot, fem=fem_spec, male=male_spec, culture=eff_culture,
            setting=eff_theme, gender=eff_gender, is_kids=is_kids, is_jugalbandi=is_jugalbandi,
            costume_hint=costume_hint, is_va=is_va,
        )

        suno_hint = build_vocal_suno_tags(genre if not is_jugalbandi else "jugalbandi", eff_culture, gender=eff_gender, tempo_bpm=100)

        is_lang_en = (language or "en").lower() == "en"
        is_generic_title = not title or any(k in str(title).lower() for k in ("wfh confusions", "melody - lyrical song", "custom screenplay", "standalone", "new song", "soulful romantic melody"))
        if is_generic_title:
            if is_lang_en:
                title_directive = (
                    f"- TITLE INVENTION (CRITICAL DIRECTIVE):\n"
                    f"  * Invent an evocative, poetic song title for this song celebrating '{eff_theme}'.\n"
                    f"  * 'title_en': Return the English song title (e.g. 'Whispers of My Heart', 'Endless Horizon'). Prohibit 'Episode X'.\n"
                    f"  * 'title_localized': Return the exact same English title as 'title_en' (strictly prohibit non-English or foreign script when language is English)."
                )
            else:
                title_directive = (
                    f"- TITLE INVENTION (CRITICAL DIRECTIVE):\n"
                    f"  * Invent an evocative, poetic, and culturally authentic title for this song celebrating '{eff_theme}'.\n"
                    f"  * 'title_en': Return ONLY the pure Romanized song title in English alphabet (e.g. 'Preyasi Priyatama', 'Sous Le Ciel'). Prohibit 'Episode X'.\n"
                    f"  * 'title_localized': Native script title followed by Romanized title in parentheses."
                )
        else:
            clean_in_title = re.sub(r"\s*-\s*episode\s*\d+", "", str(title), flags=re.IGNORECASE).strip()
            title_directive = f"- Title: {clean_in_title} ('title_en' is clean Romanized song title; 'title_localized' is native script)"

        raw_num = kwargs.get("num_images")
        auto_mode = kwargs.get("auto_images", True)
        forced_n: int | None = None
        if raw_num not in (None, "", "auto", "None", 0, "0"):
            try:
                val = int(raw_num)
                if val > 0:
                    forced_n = val
                    auto_mode = False
            except (ValueError, TypeError):
                pass

        is_mass = kwargs.get("mass_song", False) or any(k in f"{genre} {eff_theme}".lower() for k in ("mass", "dappu", "teenmaar", "mass_beats"))
        if auto_mode or forced_n is None:
            sec_win = (7, 11) if is_mass else (12, 18)
            min_sc = max(2, int(round(duration_seconds / sec_win[1])))
            max_sc = min(15, max(min_sc + 1, int(round(duration_seconds / sec_win[0]))))
            scene_rotation_directive = (
                f"- AUTONOMOUS DURATION-BASED SCENE PACING (DEFAULT):\n"
                f"  * Total Song Duration: {duration_seconds}s | Pacing Window: {'7-11s (mass beats)' if is_mass else '12-18s (melody)'}.\n"
                f"  * Autonomously determine optimal visual scenes count (recommended: {min_sc} to {max_sc} scenes) "
                f"matching musical movements (Intro, Verses, Chorus, Beat Drops, Outro).\n"
                f"  * Each scene MUST represent a distinct visual tableau or location hub (no visual stagnation)."
            )
            pose_scene_lbl = f"AUTONOMOUS {min_sc}-{max_sc}"
        else:
            scene_rotation_directive = f"- MULTI-SCENE ROTATION ({forced_n} SCENES): Rotate camera perspective across exactly {forced_n} scenes matching {eff_theme}."
            pose_scene_lbl = str(forced_n)

        self._is_va = bool(is_va)
        if is_va:
            from src.compositor.genre_strategies.virtual_artist_directives import build_virtual_artist_directives
            pose_directive = build_virtual_artist_directives(
                gender=eff_gender, artist_mode=kwargs.get("artist_mode", "scenic"),
                instrument=kwargs.get("instrument"), has_orchestra=bool(kwargs.get("has_orchestra") or kwargs.get("orchestra")),
                scenic_archetype=kwargs.get("scenic"), landmark=kwargs.get("landmark"),
                culture=eff_culture, country=eff_country, theme=eff_theme,
            )
            dyn_motion_dir = (
                "DYNAMIC SINGER PERFORMANCE MOTION DIRECTIVE (scenes[i].render_mode & motion_prompts):\n"
                "- Set 'render_mode': 'motion' for performance scenes.\n"
                "- In 'motion_prompts', direct pitch-inflected singer hand gestures (free hand lifting upward/outward on high notes and vocal climaxes, lowering gently near chest/heart on tender notes, subtle rhythm sway, emotive eyes/mouth), strictly NO two-handed rigid mic clutching and NO high-energy dance jumps.\n\n"
            )
        else:
            from src.compositor.genre_strategies.vocal_poses import build_environmental_pose_directive
            pose_directive = build_environmental_pose_directive(gender=eff_gender, theme=eff_theme, culture=eff_culture, num_scenes=pose_scene_lbl, is_mass=is_mass)
            dyn_motion_dir = (
                "DYNAMIC MOTION DANCE DIRECTIVE (scenes[i].render_mode & motion_prompts):\n"
                "Evaluate musical pacing and choreographic intensity of each scene:\n"
                "- 'motion': Select for 1 (or max 2) peak musical energy moments. Provide tailored wan and kling prompts.\n"
                "- 'still': For all other scenes, set 'render_mode': 'still' and leave motion_prompts empty.\n\n"
            )

        if is_jugalbandi:
            vocal_perspective_directive = "5. VOCAL PERFORMER PERSPECTIVE (VOCAL JUGALBANDI / SAWAAL-JAWAAB):\n   * Structure lyrics as a virtuoso vocal face-off between [Vocalist A] and [Vocalist B] with counter-melodies, rapid 2-line trades, and a grand Sangam unison climax. Label each stanza: [Vocalist A], [Vocalist B], or [Both].\n\n"
        elif eff_gender == "male":
            vocal_perspective_directive = "5. VOCAL PERFORMER PERSPECTIVE (SOLO MALE):\n   * Write all lyrics strictly from the first-person perspective of the SOLO MALE lead with male grammatical endings (e.g. 'गाता हूँ', 'मेरा'). Strictly NO female lines.\n\n"
        elif eff_gender == "female":
            vocal_perspective_directive = "5. VOCAL PERFORMER PERSPECTIVE (SOLO FEMALE):\n   * Write all lyrics strictly from the first-person perspective of the SOLO FEMALE lead with female grammatical endings (e.g. 'गाती हूँ', 'मेरी'). Strictly NO male lines.\n\n"
        else:
            vocal_perspective_directive = "5. VOCAL PERFORMER PERSPECTIVE (DUET):\n   * Structure the lyrics with alternating call-and-response couplets between [Male Lead] and [Female Lead], joining in harmony for [Chorus / Both].\n\n"

        ref_line = (
            f"- MELODIC BLUEPRINT / SIMILAR TO: '{similar_to}'\n"
            f"  * Capture the exact musical DNA, raga cadence, tempo, and melodic sweetness of '{similar_to}' while composing 100% original lyrics in {language.upper()}.\n"
        ) if similar_to else ""
        art_line = f"- Visual & Architectural Art Style: {art_style}\n" if art_style else ""

        if eff_country:
            country_directive = (
                f"- Country / Region: {eff_country} | Culture: {eff_culture or 'authentic regional'}\n"
                f"- 'country' in output JSON MUST be '{eff_country}'. 'language' in output JSON MUST be '{language}'."
            )
        else:
            country_directive = (
                f"- AUTONOMOUS COUNTRY & CULTURE DERIVATION (GEMINI MANDATORY DIRECTIVE):\n"
                f"  * The user did not specify a country. Gemini MUST autonomously identify and derive the authentic 'country' based on the language '{language.upper()}', musical genre, and narrative setting.\n"
                f"  * If language is English ('en') without an explicit country, Gemini MUST default 'country' to a Western country (e.g. 'United States' or 'United Kingdom') and 'culture' to 'western' with Western contemporary musical composition, instrumentation, staging, and attire.\n"
                f"  * For other languages, Gemini MUST autonomously assign the native country of that language (e.g. Telugu -> India, Japanese -> Japan, French -> France).\n"
                f"  * Record your autonomously derived country in the top-level 'country' field of the response JSON. 'language' in output JSON MUST be '{language}'."
            )

        return (
            f"You are an acclaimed master lyricist, music director, and visual artist.\n"
            f"Create a full broadcast-grade musical release in the {language.upper()} language.\n\n"
            f"CREATIVE DIRECTIVES:\n"
            f"{title_directive}\n"
            f"- Setting / Premise: {eff_theme}\n"
            f"- SETTING & SCENIC LOCATION FIDELITY: {eff_theme.title()}\n"
            f"{scene_rotation_directive}\n"
            f"{country_directive}\n"
            f"- Music Tone: {genre.replace('_', ' ').title()} | Vocal Performer: {eff_gender.upper()}\n"
            f"{ref_line}{art_line}"
            f"- High-CTR Earworm & Hummability Mandate: 'hook_thesis' MUST define the central hummable melodic hook. 'suno_tags' MUST include explicit keywords: 'catchy hummable melody, memorable sing-along hook, earworm refrain' along with authentic instruments and rhythm.\n"
            f"- Suno Music Tags Reference: '{suno_hint}'\n\n"
            f"LYRICS SPECIFICATION:\n"
            f"{_format_lyrics_directives(language, eff_culture, eff_theme, duration_seconds=duration_seconds)}"
            f"{'6. SUBTITLES SPECIFICATION (ENGLISH MASTER): For every line in lyrics_segments, text MUST be the clean English lyric line, and text_en MUST be IDENTICAL to text (do NOT add transliterations or translations in parentheses).' if is_lang_en else f'6. DUAL-LINE SUBTITLES (MANDATORY): For every line in lyrics_segments, text is native script of {language}, and text_en is Romanized transliteration + concise English meaning.'}\n"
            f"7. First segment starts after the opening title card (~6-8s), pacing across {duration_seconds}s.\n"
            f"{vocal_perspective_directive}"
            f"{pose_directive}"
            f"CHARACTER & VISUAL STAGING DIRECTIVE:\n"
            f"{cast_directive}\n"
            f"MANDATORY NEGATIVE CONSTRAINTS (Inject into visual prompts):\n"
            f"Negative: {neg_constraints}\n\n"
            f"MULTI-MODEL PROMPT ADAPTATION (prompts_by_model):\n"
            f"For z_image (fal-ai/z-image/turbo): Mandate hyper-realistic 4K UHD Hasselblad H6D-100c prime lens framing, vibrant saturated jewel-tone colors, warm golden sidelight, crystalline clarity, razor-sharp textures, and rich contrast.\n"
            f"For flux_dev & flux_pro_ultra: 35mm Master Prime f/1.4 lens, saturated natural tones, warm directional sidelight, high dynamic range.\n\n"
            f"LOCAL DRONE CAMERA MOTIONS (scenes[i].local_drone & camera_motion):\n"
            f"Direct camera flight for each scene matching choreography and beat intensity:\n"
            f"- Primitives: 'dollyin', 'dollyout', 'pan-left', 'pan-right', 'tilt-up', 'tilt-down', 'orbit-left', 'orbit-right', 'stay'.\n"
            f"- Parallel / Compound Movements: 'drift-up-right', 'drift-up-left', 'dollyin+tilt-up' (crane push-in), 'dollyin+pan-right', 'dollyout+tilt-down'.\n"
            f"- 'camera_motion': Single or compound motion (e.g. 'dollyin+tilt-up', 'orbit-left', 'drift-up-right').\n"
            f"  * Speed Control ('camera_speed'): 'slow'|'medium'|'fast'|'steady'. Mass songs MUST vary speed: 'slow' for lyrics/story/portraits so details are crystal clear; 'fast' strictly for beat drops & hook steps. Carnatic/Melody/Others must ALWAYS be 'slow' or 'steady' (tranquil glide).\n\n"
            f"{dyn_motion_dir}"
            f"VISUAL EFFECTS & ANIMATIONS (animation_timeline):\n"
            f"Direct 3-5 timed particle cues: effect_type in ('floating_petals_down', 'golden_fireflies', 'golden_light_leak', 'shimmering_sparkles', 'floating_petals_up', 'romantic_bokeh_drift', 'monsoon_rain_mist').\n"
        )

    def build_gemini_schema(self, **kwargs) -> dict:
        if kwargs.get("virtual_artist") or getattr(self, "_is_va", False):
            from src.compositor.genre_strategies.virtual_artist_schema import virtual_artist_gemini_schema
            return virtual_artist_gemini_schema()
        return vocal_gemini_schema()

    def validate_storyboard(self, storyboard: dict) -> list[str]:
        issues = default_storyboard_sanity_check(storyboard)
        scenes = storyboard.get("scenes") or []
        for i, s in enumerate(scenes):
            s["scene_index"] = i + 1
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
