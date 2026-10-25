"""Multilingual Gemini Prompt & Schema Engine for Live Stadium Concerts.

Constructs structured directorial prompt instructing Gemini to produce:
1. title_en (canonical English slug name for folder) & title_localized
2. Lyrical verse and catchy melodic hook couplets
3. Suno musical tags & vocal gender
4. Exactly 6 distinct physical camera descriptions (1 character, 5 cutaways)
5. Directorial broadcast cuts timeline
"""

from __future__ import annotations

import re
from typing import Any, Optional


from src.studios.concert_studio.concert_setting_catalog import (
    ConcertSettingPreset,
    resolve_concert_setting,
)
from src.studios.concert_studio.concert_style_catalog import (
    ConcertStylePreset,
    resolve_concert_style,
)


def detect_chorus_presence(storyboard_data: dict[str, Any] | None = None, lyrics: str = "", suno_tags: str = "") -> bool:
    """Detect whether song features a chorus / backing vocals requiring chorus singers on stage."""
    data = storyboard_data or {}
    if data.get("has_chorus") is True:
        return True
    comb_lyrics = f"{lyrics} {data.get('lyrics', '')}".lower()
    if any(k in comb_lyrics for k in ("[chorus", "[hook", "[refrain", "[pallavi", "chorus:", "hook:")):
        return True
    comb_tags = f"{suno_tags} {data.get('suno_tags', '')}".lower()
    if any(k in comb_tags for k in ("chorus", "choir", "backing", "harmonies", "harmony", "group vocals")):
        return True
    timeline = data.get("broadcast_timeline") or []
    return any(str(c.get("cut_type", "")).upper() in ("CHORUS", "HOOK", "CHORUS_INTENSE") for c in timeline)


from src.studios.concert_studio.concert_orbit_engine import build_contextual_orbit_prompt


def infer_artist_gender(name_or_chars: str | None, explicit_gender: str | None = None) -> str:
    """Infer artist gender ('female' or 'male') strictly matching Rule 12 & Rule 15."""
    if explicit_gender and explicit_gender.lower() in ("male", "female"):
        return explicit_gender.lower()
    val = (name_or_chars or "").lower()
    male_hints = ("male", "man", "boy", "arjun", "ram", "krishna", "vikram", "rahul", "david", "alex", "john", "ravi", "karthik", "prabhas", "mahesh", "allu", "ntr", "anirudh", "hero")
    return "male" if any(h in val for h in male_hints) else "female"


def build_concert_gemini_prompt(
    language: str = "te",
    chars: str = "Radha",
    prompt: Optional[str] = None,
    title: Optional[str] = None,
    duration_seconds: float = 60.0,
    instrument: str = "mic",
    has_orchestra: bool = True,
    theme: Optional[str] = None,
    style: Optional[str] = None,
    setting: Optional[str] = None,
    venue_type: Optional[str] = None,
    time_of_day: Optional[str] = None,
    stage_setting: Optional[str] = None,
    background: Optional[str] = None,
    weather: Optional[str] = None,
    network: str = "telugu_rhythms",
    gender: Optional[str] = None,
    position: Optional[str] = None,
    is_dj: bool = False,
) -> str:
    """Build structured directorial prompt for Gemini LLM in any language."""
    lang_map = {
        "te": "Telugu", "hi": "Hindi", "ta": "Tamil", "kn": "Kannada", "ml": "Malayalam",
        "pa": "Punjabi", "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati", "en": "English",
        "es": "Spanish", "fr": "French", "de": "German",
    }
    lang_full = lang_map.get(language.lower(), language.capitalize())
    eff_inst = (instrument or "mic").lower()
    inst_name = "DJ Console / CDJ Mixer Setup" if (is_dj and eff_inst == "mic") else eff_inst.replace("_", " ").title()

    preset = resolve_concert_style(style or ("dj" if is_dj else theme), prompt)
    v_preset = resolve_concert_setting(
        setting, venue_type=venue_type, time_of_day=time_of_day,
        stage_setting=stage_setting, background=background, weather=weather,
    )
    eff_theme = f"Live Electronic DJ Set ({preset.display_name})" if is_dj else preset.display_name
    eff_prompt = preset.prompt
    stage_ensemble = "Illuminated DJ booth console riser, multi-channel CDJ mixer, jog wheels, LED visual wall, laser banks" if is_dj else preset.stage_ensemble
    wardrobe_guidance = "Sleek modern DJ performance streetwear / bomber jacket with over-ear DJ headphones and left-wrist watch" if is_dj else preset.wardrobe_guidance

    eff_gender = infer_artist_gender(chars, gender)
    artist_physique = "Male, age 25, striking handsome stage presence, lean-athletic fit build" if eff_gender == "male" else "Female, age 24, striking stage presence, natural fit medium-slender build"
    vocal_directive = "MALE VOCALS (deep energetic vocal delivery)" if eff_gender == "male" else "FEMALE VOCALS (sweet melodic emotive vocal delivery)"
    eff_pos = (position or getattr(preset, "default_position", "standing")).lower().strip()
    if is_dj:
        pos_desc = "STANDING behind illuminated DJ console with multi-channel CDJ mixer, jog wheels, and over-ear headphones, cueing beats and hyping crowd"
        lead_artist_line = f"LEAD ARTIST: DJ {chars} ({artist_physique}) - Live DJ & Producer behind a professional illuminated DJ console setup with over-ear headphones"
    else:
        pos_desc = "SEATED cross-legged on an ornate Persian stage carpet or carved wooden dais with classical mudras" if eff_pos == "sitting" else "STANDING tall centerstage at a chrome stand microphone with dynamic presence"
        lead_artist_line = f"LEAD ARTIST: {chars} ({artist_physique})"

    desc_clause = f"USER CREATIVE CONCEPT & PROMPT: {eff_prompt}\n" if eff_prompt else ""
    title_clause = f"USER SUGGESTED TITLE: {title}\n" if title else ""

    has_custom_inst = bool(instrument and instrument.lower() not in ("mic", "none", "vocal", "vocals"))
    is_outdoor = v_preset.venue_type == "outdoor" or any(k in f"{v_preset.stage_setting} {v_preset.background}".lower() for k in ("beach", "ocean", "outdoor", "garden", "mountain", "desert", "roof"))
    outdoor_ban = ", indoor, indoor stadium, arena trusses, steel rafters, ceiling, enclosed walls, dark room, concrete stadium bowl" if is_outdoor else ""
    v_ctx = f"Stage architecture is an authentic {v_preset.stage_environment} at {v_preset.display_name} directly overlooking {v_preset.background.replace('_', ' ')} under {v_preset.lighting_environment} ({v_preset.time_of_day}). Eye-level wide broadcast framing."

    if is_dj:
        inst_role = "Live DJ & Producer cueing tracks on illuminated CDJ mixer console with over-ear headphones"
        plate_1_desc = f"DJ {chars} centerstage behind an illuminated DJ console with multi-channel CDJ mixer, jog wheels, and over-ear headphones. {v_ctx}"
        plate_1_neg = f"solo portrait, single person, missing dj booth, missing headphones, tight crop, close-up{outdoor_ban}"
        suno_inst_req = "Electronic DJ live concert anthem, driving beats, drops, and stadium crowd hype."
    elif has_custom_inst:
        inst_role = f"SINGER-INSTRUMENTALIST ({inst_name.upper()} + VOCALS). Main artist {chars} plays {inst_name} while singing. 'suno_tags' MUST prominently feature virtuosic {inst_name} solos. Scene 1 visual prompts MUST show {chars} playing {inst_name}."
        plate_1_desc = f"Lead Singer-Instrumentalist {chars} centerstage playing {inst_name} with microphone lowered strictly below chin at chest level, flanked side-by-side by the live backing rhythm section, accompanists, and 2-3 backing chorus vocalists standing at their microphones singing harmonies. Microphone positioned strictly below chin level at upper-chest height with clear open separation so lips, mouth, and chin are completely open, visible and unobstructed for lip sync camera tracking. ALL musicians arranged side-by-side on stage in a wide cinematic frame. {v_ctx}"
        plate_1_neg = f"solo portrait, single person, missing {inst_name.lower()}, empty hands, missing orchestra, missing chorus, missing accompanists, empty carpet, tight crop, close-up, microphone covering mouth, microphone blocking lips, mic covering face, microphone in front of lips, hand covering mouth, obstructed lips{outdoor_ban}"
        suno_inst_req = f"'suno_tags' MUST prominently feature virtuosic {inst_name.lower()} solos, {inst_name.lower()} leads, and {eff_gender} vocals. Lyrics and structure MUST include explicit [{inst_name.title()} Solo Interlude] breaks. Timeline cuts during interludes direct camera to showcase {chars} performing virtuosic {inst_name} solos at the mic."
    else:
        inst_role = f"VOCALIST ONLY (MICROPHONE ONLY). Main artist {chars} strictly sings with classical hand mudras and DOES NOT play any instruments. The backing orchestra plays all instruments (violin, mridangam, drums). Scene 1 prompt MUST forbid singer from holding or playing any instrument."
        plate_1_desc = f"Lead Singer centerstage holding microphone gracefully down at upper-chest level strictly below chin height (with clear visible separation between chin and microphone), leaving the entire face, closed lips, mouth, teeth, and jawline completely visible and unobstructed. Flanked by live backing orchestra (acoustic violinist and mridangam percussionists), and 2-3 backing chorus vocalists on stage at their standing microphones singing harmonies. ALL musicians arranged side-by-side on stage. Lead singer MUST have microphone held strictly below chin (NEVER in front of mouth or lips). {v_ctx}"
        plate_1_neg = f"solo portrait, single person, missing chorus, missing backing vocalists, singer playing violin, singer holding instrument, missing orchestra, missing accompanists, empty carpet, tight crop, close-up, microphone covering mouth, microphone blocking lips, mic covering face, microphone in front of lips, hand covering mouth, obstructed lips, blocked mouth{outdoor_ban}"
        suno_inst_req = f"Lead vocalist only. 'suno_tags' style: '{preset.suno_tags_template}', {eff_gender} vocals with live orchestra accompaniment and chorus. Backing orchestra plays all musical interludes."

    example_orbit, _ = build_contextual_orbit_prompt(
        style=eff_theme, setting=setting or v_preset.setting_id, venue_type=v_preset.venue_type,
        background=v_preset.background, weather=v_preset.weather, chars=chars, instrument=instrument,
        position=eff_pos, has_chorus=True,
    )

    return f"""You are the Grand Director of Live Stadium Concert Broadcasts for network '{network}'.
Direct a complete, broadcast-ready 4K Multi-Camera Live Concert in language: {lang_full} ({language.upper()}).

{desc_clause}{title_clause}CONCERT STYLE: {eff_theme}
CONCERT VENUE: {v_preset.display_name}
ENVIRONMENT & LIGHTING: {v_preset.lighting_environment}
STAGE ARCHITECTURE: {v_preset.stage_environment}
AUDIENCE ENVIRONMENT: {v_preset.audience_environment}
{lead_artist_line}
STAGE POSTURE & SETUP: {eff_pos.upper()} - {pos_desc}. Scene 1 visual prompts MUST frame this performer setup.
VOCAL GENDER REQUIREMENT: {vocal_directive} - 'vocal_gender' MUST be '{eff_gender}' and 'suno_tags' MUST include '{eff_gender} vocals'.
LEAD ARTIST ROLE & INSTRUMENT: {inst_role}
STAGE ENSEMBLE: {stage_ensemble}
DURATION: {int(duration_seconds)}s

DIRECTORIAL REQUIREMENTS:
1. CANONICAL ENGLISH & LOCALIZED TITLES:
   - 'title_en': Creative, poetic, authentic English transliterated song title organically derived from the unique lyrical theme, emotional bhava, and musical style. Must be completely original and unique. NEVER copy fixed examples or output generic words like 'Concert Song' or 'Live Concert'.
   - 'title_localized': Authentic title in native {lang_full} script accurately matching 'title_en'.
2. LYRICS & HOOK COUPLETS (MANDATORY {lang_full.upper()} LANGUAGE):
   - 'lyrics': MUST be written 100% in {lang_full} ({language.upper()}) using authentic native {lang_full} script.
   - STRICT BAN ON ENGLISH: NEVER write lyrics in English for {lang_full}. All couplets, hooks, and chorus MUST be purely in {lang_full}.
   - Write vibrant, rhyming lyrics with rhythmic meter (prasa), emotional bhava, and catchy chorus refrain.
   - Include [Hook], [Verse 1], [Chorus], and [Outro].
3. SUNO MUSICAL TAGS & INSTRUMENTATION:
   - {suno_inst_req}
4. AUTONOMOUS WARDROBE & ACCESSORIES:
   - Direct an attractive, beautiful, elegant professional concert outfit matching: {wardrobe_guidance}
   - Non-exposing, dignified, advertiser-safe (zero cleavage, covered chest and torso).

5. SINGLE 4K MASTER STAGE PLATE (1 UNIFIED PHYSICAL SET) & 360° ORBIT PIPELINE:
   - Only ONE master stage plate ('singer_orchestra_stage') is generated by image models.
   - All other angles (audience, accompanists, vista) are extracted downstream from the 10-second 360° orbital flight ('stadium_3d_flight.mp4').
   - 'camera_orbit_prompt': MUST direct a continuous 10-second 360-degree circular camera trajectory matching the venue and genre:
     "{example_orbit}"
   - Plate 1 ('singer_orchestra_stage'): WIDE-ANGLE MASTER SHOT OF ENTIRE PERFORMANCE STAGE. {plate_1_desc}
   - Plate 1 Negative Constraints: '{plate_1_neg}'.

6. CRITICAL BELOW-CHIN MICROPHONE PLACEMENT RULE (FOR WAV2LIP LIP-SYNC):
   - Because this is a concert performance requiring AI mouth synchronization (Wav2Lip), the microphone MUST be placed strictly BELOW THE CHIN at upper-chest height, angled gently upward.
   - The lips, mouth opening, teeth, and facial expression MUST be 100% visible with crystal-clear line-of-sight to the camera. If the microphone covers the mouth or lips, AI lip-sync (Wav2Lip) will fail or glitch.
   - All image prompts MUST specify: 'chrome stand microphone positioned below chin level at upper chest, lips and mouth fully visible and unobstructed'.
   - All negative prompts MUST include: 'microphone covering mouth, microphone blocking lips, mic covering face, microphone in front of lips, hand covering mouth, obstructed lips, blocked mouth'.

7. MODEL-SPECIFIC PROMPTS FOR SCENE 1 MASTER STAGE PLATE & LIVING LIP-SYNC MOTION:
   - 'image_prompts': Tailored for 'flux_dev', 'flux_pro_ultra', 'z_image'. Each prompt MUST explicitly incorporate the exact venue setting ({v_preset.display_name}), stage architecture ({v_preset.stage_environment}), background scenery ({v_preset.background.replace('_', ' ')}), and lighting ({v_preset.lighting_environment}) at wide-angle eye-level framing. Negative prompts MUST enforce: '{plate_1_neg}'.
   - 'motion_prompts': Tailored for 'wan_2_1', 'kling_prod', 'kling_4k'. This video serves as the continuous LIVING BASE PLATE FOR LIP-SYNC: rock-steady locked-off front eye-level broadcast camera view, lead singer centerstage with lips gently closed, natural breathing, subtle torso micro-sway, emotive face, live orchestra accompanists actively playing instruments in background (bowing violin, tapping mridangam drums), backing chorus vocalists swaying gently in rhythm at microphones, and background environment motion ({v_preset.background.replace('_', ' ')}). Forbids open mouth, mouth flapping, camera wobble, drone zoom.

8. VENUE & AUDIENCE AUTHENTICITY (SERENE ATMOSPHERE VS STADIUM):
   - For Carnatic, Carnatic fusion, Hindustani, or classical styles: The audience atmosphere is SERENE and DIGNIFIED (listeners seated attentively, appreciating with gentle head nods, zero lightsticks, zero glowing sticks, zero rave lasers).
   - For beach, outdoor, or garden settings: DO NOT show an indoor stadium, concrete stadium bowl, arena trusses, or steel stadium roof. Depict an authentic open-air seaside stage deck overlooking rolling ocean waves with warm ambient lanterns.
   - 2-3 backing chorus vocalists MUST be present on stage at microphones alongside the orchestra when the song features a chorus or harmonies.

Return STRICT valid JSON conforming to the schema.
"""


def build_concert_gemini_schema() -> dict[str, Any]:
    """JSON Schema contract for concert song & stage screenplay (Stage 1)."""
    return {
        "type": "OBJECT",
        "properties": {
            "title_en": {"type": "STRING"},
            "title_localized": {"type": "STRING"},
            "hook_thesis": {"type": "STRING"},
            "suno_tags": {"type": "STRING"},
            "vocal_gender": {"type": "STRING"},
            "lyrics": {"type": "STRING"},
            "camera_orbit_prompt": {"type": "STRING"},
            "character_wardrobe": {
                "type": "OBJECT",
                "properties": {
                    "outfit_description": {"type": "STRING"},
                    "accessories": {"type": "STRING"},
                    "color_palette": {"type": "STRING"},
                    "neckline_style": {"type": "STRING"},
                },
                "required": ["outfit_description", "accessories", "color_palette", "neckline_style"],
            },
            "scenes": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "scene_index": {"type": "INTEGER"},
                        "camera_id": {"type": "STRING"},
                        "camera_angle": {"type": "STRING"},
                        "visual_prompt": {"type": "STRING"},
                        "negative_prompt": {"type": "STRING"},
                        "image_prompts": {
                            "type": "OBJECT",
                            "properties": {
                                "flux_dev": {"type": "OBJECT", "properties": {"prompt": {"type": "STRING"}, "negative_prompt": {"type": "STRING"}}, "required": ["prompt", "negative_prompt"]},
                                "flux_pro_ultra": {"type": "OBJECT", "properties": {"prompt": {"type": "STRING"}, "negative_prompt": {"type": "STRING"}}, "required": ["prompt", "negative_prompt"]},
                                "z_image": {"type": "OBJECT", "properties": {"prompt": {"type": "STRING"}, "negative_prompt": {"type": "STRING"}}, "required": ["prompt", "negative_prompt"]},
                            },
                            "required": ["flux_dev", "flux_pro_ultra", "z_image"],
                        },
                        "motion_prompts": {
                            "type": "OBJECT",
                            "properties": {
                                "wan_2_1": {"type": "OBJECT", "properties": {"prompt": {"type": "STRING"}, "negative_prompt": {"type": "STRING"}}, "required": ["prompt", "negative_prompt"]},
                                "kling_prod": {"type": "OBJECT", "properties": {"prompt": {"type": "STRING"}, "negative_prompt": {"type": "STRING"}}, "required": ["prompt", "negative_prompt"]},
                                "kling_4k": {"type": "OBJECT", "properties": {"prompt": {"type": "STRING"}, "negative_prompt": {"type": "STRING"}}, "required": ["prompt", "negative_prompt"]},
                            },
                            "required": ["wan_2_1", "kling_prod", "kling_4k"],
                        },
                    },
                    "required": ["scene_index", "camera_id", "visual_prompt", "negative_prompt", "image_prompts", "motion_prompts"],
                },
            },
        },
        "required": ["title_en", "title_localized", "lyrics", "suno_tags", "character_wardrobe", "scenes"],
    }


def get_offline_concert_broadcast_timeline(duration_seconds: float = 60.0) -> list[dict[str, Any]]:
    """Generate deterministic broadcast cut sequence demonstrating smooth transitions without looping ($0.00 spend)."""
    pattern = [
        {"camera_id": "overall_stage_vista", "cut_type": "motion", "is_singing": False, "drone": "wide_stage_pullback", "curve": "cosine", "trans": "motion_to_local_drone", "lip_sync": False},
        {"camera_id": "singer_orchestra_stage", "cut_type": "local_drone", "is_singing": True, "drone": "zoom_in_singer", "curve": "ramp-down", "trans": "local_drone_to_lipsync", "lip_sync": False},
        {"camera_id": "singer_orchestra_stage", "cut_type": "lipsync", "is_singing": True, "drone": "steady_eye_level", "curve": "cosine", "trans": "lipsync_to_local_drone", "lip_sync": True},
        {"camera_id": "singer_orchestra_stage", "cut_type": "local_drone", "is_singing": False, "drone": "orbit_stage_to_audience", "curve": "cosine", "trans": "vocal_done_orbit_stage_to_audience", "lip_sync": False},
        {"camera_id": "singer_orchestra_stage", "cut_type": "motion", "is_singing": False, "drone": "pan_to_drummer", "curve": "linear", "trans": "motion_to_motion", "lip_sync": False},
        {"camera_id": "stadium_audience_crowd", "cut_type": "motion", "is_singing": False, "drone": "steady_eye_level", "curve": "cosine", "trans": "motion_to_local_drone", "lip_sync": False},
        {"camera_id": "singer_orchestra_stage", "cut_type": "local_drone", "is_singing": True, "drone": "zoom_in_singer", "curve": "ramp-down", "trans": "local_drone_to_lipsync", "lip_sync": False},
        {"camera_id": "singer_orchestra_stage", "cut_type": "lipsync", "is_singing": True, "drone": "steady_eye_level", "curve": "cosine", "trans": "lipsync_to_motion", "lip_sync": True},
        {"camera_id": "overall_stage_vista", "cut_type": "motion", "is_singing": False, "drone": "wide_stage_pullback", "curve": "cosine", "trans": "climax_outro", "lip_sync": False},
    ]
    target_cut_dur = 4.2
    n_cuts = max(1, int(round(duration_seconds / target_cut_dur)))
    cut_dur = round(duration_seconds / n_cuts, 2)
    cuts = []
    t_curr = 0.0
    for i in range(n_cuts):
        pat = pattern[i % len(pattern)]
        end_t = round(duration_seconds, 2) if i == n_cuts - 1 else round(t_curr + cut_dur, 2)
        cuts.append({
            "cut_index": i + 1,
            "start_time": round(t_curr, 2),
            "end_time": end_t,
            "duration_seconds": round(end_t - t_curr, 2),
            "camera_id": pat["camera_id"],
            "cut_type": pat["cut_type"],
            "is_singing": pat["is_singing"],
            "lip_sync": pat["lip_sync"],
            "lyrics_line": "Catchy melodic concert refrain" if pat["is_singing"] else "",
            "local_drone_motion": pat["drone"],
            "motion_curve": pat.get("curve", "cosine"),
            "transition_to_next": pat["trans"],
        })
        t_curr = end_t
    return cuts


__all__ = [
    "resolve_concert_style",
    "ConcertStylePreset",
    "build_concert_gemini_prompt",
    "build_concert_gemini_schema",
    "get_offline_concert_broadcast_timeline",
    "detect_chorus_presence",
    "build_contextual_orbit_prompt",
]
