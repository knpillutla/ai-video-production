"""Vocal Song & Lyrical Video Genre Strategy.

Orchestration config:
1. Gemini: Original poetic rhyming lyrics, Suno music tags, multi-model image prompts, and timed lyrics.
2. Suno v3.5 Pro: Full commercial vocal song synthesis.
3. 4K Keyframe: Z-Image Turbo default (with multi-model prompt alternatives in script JSON).
4. Local FFmpeg ($0.00): Song-duration lock, center-screen native lyrics burn-in, -14 LUFS mastering.
"""

from __future__ import annotations

import re
from typing import Any

from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check


def vocal_gemini_schema() -> dict:
    """Return strict JSON schema for vocal lyrical video structured output."""
    character = {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING"},
            "gender": {"type": "STRING"},
            "age": {"type": "INTEGER"},
            "body_composition": {"type": "STRING"},
            "outfit_description": {"type": "STRING"},
        },
        "required": ["name", "gender", "age", "body_composition", "outfit_description"],
    }
    lyrics_seg = {
        "type": "OBJECT",
        "properties": {
            "start": {"type": "NUMBER"},
            "end": {"type": "NUMBER"},
            "text": {"type": "STRING"},
            "text_en": {"type": "STRING"},
        },
        "required": ["start", "end", "text", "text_en"],
    }
    prompts_model = {
        "type": "OBJECT",
        "properties": {
            "z_image": {"type": "STRING"},
            "flux_dev": {"type": "STRING"},
            "flux_pro_ultra": {"type": "STRING"},
            "imagen3": {"type": "STRING"},
            "midjourney": {"type": "STRING"},
        },
        "required": ["z_image", "flux_dev", "flux_pro_ultra", "imagen3", "midjourney"],
    }
    youtube_meta = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "description": {"type": "STRING"},
            "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
            "pinned_comment": {"type": "STRING"},
            "thumbnail_prompt": {"type": "STRING"},
            "category_id": {"type": "STRING"},
        },
        "required": ["title", "description", "tags", "pinned_comment"],
    }
    anim_cue = {
        "type": "OBJECT",
        "properties": {
            "start_time": {"type": "NUMBER"},
            "end_time": {"type": "NUMBER"},
            "musical_phase": {"type": "STRING"},
            "camera_motion": {"type": "STRING", "enum": ["slow_zoom_in", "slow_zoom_out", "pan_left_to_right", "pan_right_to_left", "subtle_breathe"]},
            "effect_type": {"type": "STRING", "enum": ["floating_petals_up", "floating_petals_down", "golden_fireflies", "shimmering_sparkles", "golden_light_leak", "romantic_bokeh_drift", "monsoon_rain_mist"]},
            "intensity": {"type": "STRING", "enum": ["subtle", "medium", "vibrant"]},
            "rationale": {"type": "STRING"},
        },
        "required": ["start_time", "end_time", "camera_motion", "effect_type"],
    }
    return {
        "type": "OBJECT",
        "properties": {
            "title_en": {"type": "STRING"},
            "title_localized": {"type": "STRING"},
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
        eff_style = music_style or "romantic melody, soft, heartfelt"
        eff_gender = gender or "duet"
        eff_country = country or "India"
        eff_culture = culture or "South Indian"
        eff_theme = theme or kwargs.get("theme") or idea or "soulful romantic melody"

        ref_directive = (
            f"MUSICAL REFERENCE PATTERN: Infuse the tenderness, emotional cadence, softness, and acoustic depth "
            f"evocative of the famous classic '{similar_to}', but compose 100% brand-new original lyrics and melody."
            if similar_to else ""
        )

        is_generic_title = not title or any(k in str(title).lower() for k in ("wfh confusions", "melody - lyrical song", "custom screenplay", "standalone", "new song", "new production", "soulful romantic melody"))
        if is_generic_title:
            title_directive = (
                f"- TITLE INVENTION (CRITICAL DIRECTIVE):\n"
                f"  * Invent an evocative, poetic, and culturally authentic title for this song celebrating '{eff_theme}'.\n"
                f"  * 'title_en': Return ONLY the pure Romanized/transliterated song title in English alphabet (e.g. 'Preyasi Priyatama', 'Kanula Kaanthi Neeve', 'Gundelona Premaga'). STRICTLY PROHIBIT appending 'Episode X', 'Part X', or subtitle descriptions.\n"
                f"  * 'title_localized': Return the native script title followed by the Romanized title in parentheses (e.g. 'ప్రేయసి ప్రియతమా (Preyasi Priyatama)')."
            )
        else:
            clean_in_title = re.sub(r"\s*-\s*episode\s*\d+", "", str(title), flags=re.IGNORECASE).strip()
            title_directive = f"- Title: {clean_in_title} (Ensure 'title_en' is clean Romanized song title only and 'title_localized' is native script)"

        num_images = int(kwargs.get("num_images") or 1)
        multi_scene_directive = (
            f"MULTI-SCENE ROTATION ({num_images} SCENES - AUTONOMOUS DIRECTORIAL DERIVATION):\n"
            f"Produce exactly {num_images} distinct scenes in 'scenes'. Derive each scene strictly within the setting/premise '{eff_theme}':\n"
            f"  * 'location_hub': Derive a unique picturesque environment strictly within '{eff_theme}'. Prohibit repeating or deviating to unrelated foreign locations.\n"
            f"  * 'character_pose': Distinct physical pose & interaction per scene (strolling -> cafe/terrace -> gazing at scenery). Prohibit repeating poses.\n"
            f"  * 'camera_shot_type': Vary framing across scenes (wide establishing -> medium two-shot -> portrait close-up).\n"
            f"  * 'visual_prompt': Complete 4K directorial visual prompt. MANDATORY SCRIPT IDENTITY: Explicitly specify recurring lead couple's authentic {eff_culture} ethnicity, facial identity, and wardrobe continuity.\n\n"
            if num_images > 1 else ""
        )

        return (
            f"You are an acclaimed master lyricist, music director, and visual artist. "
            f"Create a full broadcast-grade musical release in the {language.upper()} language.\n\n"
            f"CREATIVE DIRECTIVES:\n"
            f"{title_directive}\n"
            f"- Central Theme / Setting / Premise: {eff_theme}\n"
            f"- Country / Region: {eff_country}\n"
            f"- Cultural Nuance: {eff_culture}\n"
            f"- Music Style: {eff_style} (e.g. festive, happy, soft romantic melody, or energetic)\n"
            f"- Vocal Gender: {eff_gender} (male solo, female solo, or romantic duet)\n"
            f"{ref_directive}\n\n"
            f"LYRICS SPECIFICATION (3.5-Minute Broadcast Standard):\n"
            f"1. Write complete rhyming lyrical couplets (Pallavi, Anupallavi, Charanam 1, and Charanam 2) in the NATIVE SCRIPT of {language} celebrating '{eff_theme}'.\n"
            f"2. Strict cultural meter and rhyming cadence (e.g. prasa/chandas for Telugu/Kannada, qafiya/radif for Hindi/Urdu).\n"
            f"3. DUAL-LINE SUBTITLES (MANDATORY): In 'lyrics_segments', for every line provide BOTH:\n"
            f"   * 'text': Lyrical line in the NATIVE SCRIPT (e.g. Telugu).\n"
            f"   * 'text_en': Romanized English transliteration + concise English meaning (e.g. 'Kanula Kaanthi Neeve | You are the light in my eyes').\n"
            f"4. INSTRUMENTAL INTRO & VOCAL SYNC: The song begins with a 4.5s-5.5s acoustic intro (flute/guitar/tabla) before singing starts. First segment MUST start at ~4.5s, pacing segments smoothly across {duration_seconds}s.\n\n"
            f"{multi_scene_directive}"
            f"HIGH-CTR 4K IMAGE & CHARACTER SPECIFICATION (Rule 12):\n"
            f"1. HIGH-CTR VIBRANT PALETTE: Depict rich, colorful, eye-catching jewel tones (deep crimson red, emerald green, royal peacock blue, glowing amber) "
            f"with dramatic clean cinematic lighting to achieve maximum YouTube feed click-through rate. Zero washed-out or dull tones.\n"
            f"2. FEMALE & MALE ANATOMICAL ACCURACY, CULTURAL IDENTITY & PHYSICALITY (Mid-20s, Ages 23-27):\n"
            f"   - Cultural Authenticity: Both characters MUST be authentically {eff_culture} / {eff_country} with natural warm skin tones and regional features.\n"
            f"   - Woman: Strikingly beautiful, cute, and stylish {eff_culture} woman, mid-20s (ages 23-26), graceful SLIM build with balanced medium feminine curves (neither too thin nor heavy, healthy natural fit proportions with defined trimmer waistline), delicate slender oval face with subtle defined cheekbones, cute dimpled smile, expressive sparkling dark eyes, delicate collarbones, elegant slender hands, wrists, and ankles, radiant skin.\n"
            f"   - Man: Strikingly handsome {eff_culture} man, mid-20s (ages 24-27), MEDIUM BUILT, lean-athletic fit physique, sharp sculpted jawline.\n"
            f"3. DIVERSE STAGING & POSES (Strict Ban on Default Hand-Holding):\n"
            f"   - Strictly PROHIBIT repetitive, generic hand-holding poses. Feature dynamic, cute, emotional, connecting staging:\n"
            f"     * Travel / Motion: Traveling in open-top vintage jeep, vespa, or train window enjoying warm breeze.\n"
            f"     * Cafe / Bistro: Sitting across from each other at wooden cafe table or outdoor bistro, teasing smile with dimples.\n"
            f"     * Lawn / Garden: Sitting back-to-back on lush grassy lawn with warm fairy lights, candid laughter.\n"
            f"     * Patio / Balcony: Lounging on chic patio furniture, porch swing, or luxury high-rise balcony looking at city skyline.\n"
            f"     * Candid Chemistry: Looking cute, emotional, connecting, sweet, and beautiful with genuine romantic expressions.\n"
            f"4. SETTING & SCENIC LOCATION FIDELITY (MANDATORY):\n"
            f"   - If '{eff_theme}' or art_style mentions a location/environment (e.g. Swiss Alps, Paris, Norway, Mediterranean), ALL scene backgrounds, location_hubs, and thumbnail_prompt MUST be set in picturesque sub-locations of THAT SPECIFIC setting (e.g. for Swiss Alps: snow-capped Eiger/Jungfrau peaks, green alpine meadows, Swiss chalets, glacial streams). Prohibit deviating to unrelated foreign locations.\n"
            f"5. AUTHENTIC 35MM OPTICAL AESTHETIC (Zero Plastic CGI Sheen):\n"
            f"   - Photorealistic 35mm film photograph aesthetic with natural skin texture, visible pores, fine film grain. STRICTLY PROHIBIT plastic doll skin, wax figures, or artificial CGI sheen.\n"
            f"6. CONTEXT-MATCHED DYNAMIC WARDROBE & 4-ZONE CURATED ACCESSORIES:\n"
            f"   - MANDATORY SETTING-OUTFIT HARMONY: Western cities (Paris, London) = chic Western modern fashion (trench coat, tailored wool overcoat, fine knit turtleneck, high-waist trousers, stylish boots). STRICTLY NO sarees in Western cities!\n"
            f"   - STRICT BAN ON SAREES FOR FEMALE CHARACTERS unless explicitly requested by the user or in a traditional temple/wedding setting.\n"
            f"   - 4-ZONE ACCESSORIES FOR HER (Matched to Outfit):\n"
            f"     * Hair: Delicate pearl/gold hairpins or sleek barrette (modern); fresh jasmine flowers or subtle maang tikka (festive).\n"
            f"     * Neck & Ears: Delicate necklace/pendant, matching huggie/stud earrings or cultural jhumkas.\n"
            f"     * Hands & Wrists: Slim luxury dress watch, delicate tennis bracelet or glass bangles, dainty rings on slender fingers.\n"
            f"     * Legs & Feet: Delicate gold/silver ankle chain (anklet) catching light, paired with strappy sandals or heels (modern); silver payal (festive).\n"
            f"   - MALE ANATOMICAL WATCH PLACEMENT (CRITICAL): Male lead's chronograph watch MUST be described as 'strapped securely to his left wrist'. Plain clean unadorned shirt front with zero badges, pins, or graphics.\n"
            f"   - MANDATORY SELF-CONTAINED SCENE PROMPTS: Every scene's 'visual_prompt' MUST repeat the woman's dress, slender-curvy build, and accessories, and the man's outfit and wrist-worn watch. NEVER drop or abbreviate wardrobe in later scenes!\n"
            f"7. YOUTUBE 4K THUMBNAIL & NATIVE SCRIPT SPECIFICATION (youtube_metadata):\n"
            f"   - 'thumbnail_prompt': High-CTR 4K thumbnail image prompt for the image model capturing the emotional climax, gorgeous character chemistry, dramatic lighting, and vibrant jewel tones.\n"
            f"   - 'title_localized': Pure song title in the NATIVE SCRIPT of {language} (e.g. 'చిగురించే ప్రేమలా') rendered on the thumbnail banner with the native regional font (Mandali for Telugu)!\n"
            f"8. FAMILY-FRIENDLY & MONETIZATION SAFETY (Rule 11 - Strict Safe-Ad Guarantee):\n"
            f"   - Outfits must be dignified, classy, and culturally authentic. Zero revealing, provocative, or overly sexualized clothing. STRICTLY NO plunging necklines, NO sheer/exposed underwear, and NEVER nude / NSFW.\n\n"
            f"MULTI-MODEL PROMPT ADAPTATION (prompts_by_model):\n"
            f"Generate tailored image prompts for all 5 image models in the studio. Every prompt MUST explicitly mandate: 'crisp tailored garment construction, zero outfit distortion, scene-matched wardrobe drape, clean tailored seams, authentic anatomy, natural hands':\n"
            f"- 'z_image': Fast, ultra-sharp 4K prompt emphasizing vibrant colors, crisp textile textures, zero outfit distortions (Default).\n"
            f"- 'flux_dev': 28-step natural language cinematic prompt with pristine garment draping specifics.\n"
            f"- 'flux_pro_ultra': Optical camera specifics (35mm Master Prime, f/1.4 shallow depth) and clean couture tailoring.\n"
            f"- 'imagen3': Google Imagen 3 photorealistic lighting and realistic textile detail prompt.\n"
            f"- 'midjourney': Stylized aesthetic prompt with aspect ratio flag --ar 16:9 and clean fashion lines.\n\n"
            f"CULTURALLY ALIGNED VISUAL EFFECTS & ANIMATIONS (animation_timeline - Rule 12):\n"
            f"Direct dynamic local visual animations authentic to the song's culture ({eff_culture}), setting, and mood across {duration_seconds}s. Provide 3-5 timed cues:\n"
            f"- camera_motion: 'slow_zoom_in', 'slow_zoom_out', 'pan_left_to_right', 'pan_right_to_left', 'subtle_breathe'\n"
            f"- effect_type: 'floating_petals_up', 'golden_fireflies', 'golden_light_leak', 'shimmering_sparkles', 'floating_petals_down', 'romantic_bokeh_drift', 'monsoon_rain_mist'.\n"
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
