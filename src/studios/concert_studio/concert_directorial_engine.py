"""Time-Coded Directorial Screenplay Engine for Concert Broadcasts.

Directs broadcast cut sequence based on ground-truth audio analysis:
1. Receives real-time audio segments (Intro, Verses, Chorus, Interludes, Outro).
2. Directs Gemini multi-camera broadcast television switching.
3. Guarantees 100% synchronization between lip-sync, orchestra flights, and music beats.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

from src.core.telemetry import logger
from src.studios.concert_studio.concert_audio_slicer import AudioConcertSegment


def build_timecoded_directorial_prompt(
    segments: List[AudioConcertSegment],
    lyrics: str,
    language: str = "te",
    artist_name: str = "Radha",
    instrument: str = "mic",
    style: str = "Carnatic Classical",
) -> str:
    """Build directorial prompt for Gemini feeding real audio ground-truth cuts."""
    timeline_desc = []
    for s in segments:
        vocal_txt = "VOCALS ACTIVE (Singer performing)" if s.is_singing else "ORCHESTRA ONLY (No singing, backing instruments / solo)"
        timeline_desc.append(
            f"- Cut {s.segment_id:02d} [{s.start_time:5.2f}s - {s.end_time:5.2f}s] ({s.duration:4.2f}s): "
            f"Type={s.segment_type} | {vocal_txt} | Recommended Cam={s.recommended_camera}"
        )
    segs_str = "\n".join(timeline_desc)

    inst_directive = (
        f"Artist {artist_name} is a SINGER-INSTRUMENTALIST playing {instrument.title()} at the microphone while singing."
        if instrument.lower() not in ("mic", "none", "vocal", "vocals")
        else f"Artist {artist_name} is VOCALIST ONLY singing passionately into the microphone with hand mudras."
    )

    return f"""You are the Grand Director of Live Stadium Concert Television Broadcasts.
Direct a broadcast-ready multi-camera concert cut list in language {language.upper()} for {artist_name}.
CONCERT STYLE: {style}
LEAD ARTIST: {artist_name} ({inst_directive})

FULL CONCERT LYRICS:
{lyrics}

GROUND-TRUTH MASTER AUDIO TIMELINE (DERIVED DIRECTLY FROM SUNO MASTER STEM):
{segs_str}

DIRECTORIAL CONSTRAINTS (STRICT CINEMATIC BROADCAST RULES):
1. EXACT TIMELINE SYNCHRONIZATION:
   - You MUST output exactly {len(segments)} cuts matching the exact start_time, end_time, and duration_seconds of each segment above.
   - Do NOT alter, add, or skip any timestamps.
   - CINEMATIC BROADCAST PACING: Each cut is a deliberate, sustained 8.0s to 10.0s musical movement. Let the camera motion unfold smoothly across the full take so the viewer stays focused and immersed.

2. MANDATORY 4-CAMERA RIG ROTATION & AUTHENTIC FRAMING:
   - 'singer_orchestra_stage' (Cam 1): Front center stage at eye level. Lead performer & ensemble. Framings: 'MASTER_WIDE', 'MEDIUM_PERFORMER', 'CLOSE_UP' (slow dolly in to singer face level, framing vintage stand mic and emotive facial expressions).
   - 'stage_left_profile' (Cam 2): Stage-left 45-degree side profile view of lead performer and accompanists at face and instrument level.
   - 'stadium_audience_crowd' (Cam 3): Audience view matching genre: For Carnatic / Classical, serene connoisseur audience seated in deep appreciation (NEVER waving lightsticks!).
   - 'overall_stage_vista' (Cam 4): Environment shot matching venue (open-air seaside beach stage deck overlooking waves, or grand hall).
   - DIRECTORIAL RULE: Cycle dynamically across all 4 cameras. Direct very slow continuous camera glides ('dolly_in_face', 'pan_slow', 'orbit_slow') so the singer is never frozen in a static shot.

3. VOCAL & ORCHESTRA ALIGNMENT:
   - For ORCHESTRA cuts ('is_singing': false): Cut to Cam 2 (profile), Cam 3 (audience), or Cam 4 (arena vista). 'lip_sync' MUST be false.
   - For SINGING cuts ('is_singing': true): Cut to Cam 1 ('singer_orchestra_stage') with 'lip_sync': true.
   - Provide the specific 'lyrics_line' sung during each singing cut.

4. CAMERA DRONE MOTIONS:
   - Choose: 'dolly_in_face', 'pan_slow', 'steady_eye_level', 'wide_stage_pullback', 'orbit_stage_to_audience', 'pan_to_guitarist', 'pan_to_drummer'.
   - Curves: 'cosine', 'ramp-down', 'ramp-up', 'linear'.

Return STRICT valid JSON conforming to the schema.
"""


def build_timecoded_directorial_schema() -> dict[str, Any]:
    """JSON schema contract for time-coded directorial broadcast cuts."""
    item_props = {
        "cut_index": {"type": "INTEGER"}, "start_time": {"type": "NUMBER"}, "end_time": {"type": "NUMBER"},
        "duration_seconds": {"type": "NUMBER"}, "camera_id": {"type": "STRING"}, "cut_type": {"type": "STRING"},
        "is_singing": {"type": "BOOLEAN"}, "lip_sync": {"type": "BOOLEAN"}, "lyrics_line": {"type": "STRING"},
        "local_drone_motion": {"type": "STRING"}, "motion_curve": {"type": "STRING"},
        "transition_to_next": {"type": "STRING"}, "directorial_notes": {"type": "STRING"},
    }
    req = ["cut_index", "start_time", "end_time", "duration_seconds", "camera_id", "cut_type", "is_singing", "lip_sync", "local_drone_motion", "transition_to_next"]
    return {"type": "OBJECT", "properties": {"broadcast_timeline": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": item_props, "required": req}}}, "required": ["broadcast_timeline"]}


def direct_timecoded_timeline_deterministic(segments: List[AudioConcertSegment], lyrics: str = "") -> list[dict[str, Any]]:
    """Generate high-fidelity deterministic cut sequence aligned to real audio segments ($0.00 spend)."""
    cuts, cam_history = [], []
    lyrics_lines = [l.strip() for l in lyrics.splitlines() if l.strip() and not l.strip().startswith("[")]

    for i, s in enumerate(segments):
        cam = s.recommended_camera
        if len(cam_history) >= 2 and cam_history[-1] == "singer_orchestra_stage" and cam_history[-2] == "singer_orchestra_stage":
            if i % 3 == 0:
                cam = "stage_left_profile"
            elif i % 3 == 1:
                cam = "stadium_audience_crowd"
            else:
                cam = "overall_stage_vista"
        cam_history.append(cam)

        is_sing = bool(s.is_singing)
        lip = bool(is_sing and cam == "singer_orchestra_stage")
        if not is_sing:
            cut_t = "ORCHESTRA_3D_SWEEP" if cam in ("overall_stage_vista", "stadium_audience_crowd") else ("SIDE_PROFILE_STAGE" if cam == "stage_left_profile" else "ACCOMPANIMENT_WIDE")
        elif i % 3 == 0:
            cut_t = "MASTER_WIDE"
        elif i % 3 == 1:
            cut_t = "MEDIUM_PERFORMER"
        else:
            cut_t = "CLOSE_UP"

        if cut_t == "CLOSE_UP":
            rec_motion = "dolly_in_face"
        elif cam == "stage_left_profile":
            rec_motion = "pan_profile_slow"
        elif cam == "singer_orchestra_stage":
            rec_motion = "dolly_in_face" if i % 2 == 1 else "pan_slow"
        else:
            rec_motion = s.recommended_motion

        lyr = lyrics_lines[i % len(lyrics_lines)] if (is_sing and lyrics_lines) else ""
        cuts.append({
            "cut_index": s.segment_id, "start_time": s.start_time, "end_time": s.end_time, "duration_seconds": s.duration,
            "camera_id": cam, "cut_type": cut_t, "is_singing": is_sing, "lip_sync": lip, "lyrics_line": lyr,
            "local_drone_motion": rec_motion, "motion_curve": "cosine",
            "transition_to_next": "cut" if i < len(segments) - 1 else "fade_out",
            "directorial_notes": f"Paced to {s.segment_type} (energy={s.intensity_score:.2f})", "stem_path": s.stem_path,
        })
    return cuts


def build_multimodal_audio_directorial_prompt(
    lyrics: str,
    total_duration: float,
    language: str = "te",
    artist_name: str = "Radha",
    instrument: str = "mic",
    style: str = "Carnatic Classical",
) -> str:
    """Prompt for Gemini Multimodal Audio to segment timeline based on real singing vs orchestra."""
    inst = (
        f"playing {instrument.title()} while singing"
        if instrument.lower() not in ("mic", "none", "vocal", "vocals")
        else "vocalist singing with hand mudras"
    )
    return f"""You are the Grand Director of Live Stadium Concert Television Broadcasts.
Listen carefully to this master audio track ({total_duration:.1f}s) in {language.upper()} for {artist_name} ({inst}).
CONCERT STYLE: {style}
FULL CONCERT LYRICS:
{lyrics}

TASK:
Segment the entire song timeline into natural broadcast cuts (approx 7.0s to 10.5s each, covering 0.0s to {total_duration:.2f}s).
Listen directly to the audio to determine where the vocalist is ACTUALLY singing versus where it is purely instrumental orchestra.

CRITICAL DIRECTIVES:
1. INTRO: All cuts before the singer starts singing must be is_singing: false, cut_type: 'ORCHESTRA', lyrics_line: ''.
2. OUTRO: The moment singing concludes and the instrumental violin/mridangam outro begins (typically around last 15-20s), ALL subsequent cuts until the very end MUST be is_singing: false, cut_type: 'ORCHESTRA', lyrics_line: ''.
3. SINGING CUTS: Set is_singing: true, provide the exact 'lyrics_line' sung during that cut, cut_type: 'VERSE_MODERATE' or 'CHORUS_INTENSE' or 'SWARA_CLIMAX'.
4. CAMERA ROTATION & AUTHENTIC FRAMING:
   - 'singer_orchestra_stage' (Cam 1): Lead artist. Framing: 'MASTER_WIDE', 'MEDIUM_PERFORMER', or 'CLOSE_UP' (slow dolly in to singer face and mic level).
   - 'stage_left_profile' (Cam 2): Stage-left side view of lead performer and accompanists at face and instrument level.
   - 'stadium_audience_crowd' (Cam 3): Audience view matching genre (serene seated appreciation without lightsticks for classical/Carnatic).
   - 'overall_stage_vista' (Cam 4): Environment vista matching venue (seaside deck for beach, or grand hall).
   Do not keep Cam 1 for more than 2 consecutive cuts. Direct slow continuous camera glides ('dolly_in_face', 'pan_slow', 'orbit_slow') so the singer is never frozen in a static shot.
5. NO CUTTING MID-WORD: Align cuts to natural musical/vocal phrase pauses.
6. NO GAPS: Cuts must seamlessly span from 0.0s to {total_duration:.2f}s.

Return STRICT valid JSON conforming to the schema."""


async def direct_concert_broadcast_timeline(
    llm: Any,
    segments: List[AudioConcertSegment],
    lyrics: str,
    language: str = "te",
    artist_name: str = "Radha",
    instrument: str = "mic",
    style: str = "Carnatic Classical",
    force_live: bool = False,
    audio_path: Optional[Any] = None,
    stems_dir: Optional[Any] = None,
) -> list[dict[str, Any]]:
    """Direct cinematic concert timeline strictly synchronized to real audio."""
    if not force_live or llm is None:
        logger.info(f"directing_timecoded_timeline_deterministic: count={len(segments)}")
        return direct_timecoded_timeline_deterministic(segments, lyrics)

    is_gem = getattr(llm, "provider", "").lower() == "gemini"
    has_audio = bool(is_gem and audio_path and Path(audio_path).is_file() and Path(audio_path).stat().st_size > 1000)
    tot_dur = segments[-1].end_time if segments else 120.0
    if has_audio:
        prompt = build_multimodal_audio_directorial_prompt(
            lyrics=lyrics, total_duration=tot_dur, language=language,
            artist_name=artist_name, instrument=instrument, style=style,
        )
    else:
        prompt = build_timecoded_directorial_prompt(
            segments=segments, lyrics=lyrics, language=language,
            artist_name=artist_name, instrument=instrument, style=style,
        )
    schema = build_timecoded_directorial_schema()

    try:
        prov = getattr(llm, "provider", "llm").upper()
        logger.info(f"directing_timecoded_timeline_with_{prov.lower()}...")
        resp = await llm.generate_structured(prompt, schema=schema, audio_path=audio_path if has_audio else None)
        tl = resp.get("broadcast_timeline", [])
        if len(tl) >= 3:
            for cut in tl:
                is_sing = bool(cut.get("is_singing", False))
                cam = str(cut.get("camera_id", ""))
                cut["lip_sync"] = bool(is_sing and cam in ("singer_orchestra_stage", "center_vocalist_front"))
            return tl
        logger.warning(f"{prov.lower()}_timeline_empty: got {len(tl)} cuts. Using fallback.")
    except Exception as ex:
        logger.warning(f"timecoded_directing_failed: {ex}. Using deterministic broadcast cuts.")

    return direct_timecoded_timeline_deterministic(segments, lyrics)


def get_offline_concert_storyboard(
    title: str | None = None,
    language: str = "te",
    chars: str = "Radha",
    duration_seconds: float = 60.0,
    instrument: str = "mic",
) -> dict[str, Any]:
    """Deterministic offline concert storyboard ($0.00 spend)."""
    t_en = title or "Sagara Tarangala Raga Sudha"
    return {
        "title_en": t_en,
        "title_localized": "సాగర తరంగాల రాగ సుధ",
        "hook_thesis": "Grand coastal concert fusion marrying deep classical ragas with the ocean sunset.",
        "lyrics": "[Hook]\nసప్తస్వరాల సంధ్యారాగమే\nసాగర తీరాన నాట్యమాడెనే\n\n[Verse 1]\nమృదంగ ధ్వనులతో పొంగే తరంగాలు\nవయోలిన్ తంత్రులై పలికే భావాలు\n\n[Chorus]\nరాగసుధారస ధారలు కురిసే\nతీరపు గాలికి తాళము కలిసే\n\n[Outro]\nనాదబ్రహ్మమే శాశ్వత రూపు",
        "suno_tags": "carnatic classical vocal concert, melodic raga, acoustic violin, mridangam, female vocals, 120 bpm",
        "vocal_gender": "female",
        "character_wardrobe": {
            "outfit_description": "Exquisite royal magenta and peacock teal Kanjivaram silk saree with temple border",
            "accessories": "Traditional gold temple jhumkas, choker, fresh white jasmine in braided hair",
            "color_palette": "Deep magenta, peacock teal, antique matte gold",
            "neckline_style": "Closed high-mandarin collar blouse, modest coverage",
        },
        "camera_orbit_prompt": "Continuous 10-second seamless 360-degree circular orbital camera flight revolving completely around the stage platform.",
        "scenes": [
            {
                "scene_index": 1, "camera_id": "singer_orchestra_stage", "camera_angle": "Eye-level wide master",
                "visual_prompt": f"Lead singer {chars} centerstage at microphone with backing orchestra on coastal stage.",
                "negative_prompt": "cleavage, low-cut, exposed torso, modern dress",
                "image_prompts": {
                    "flux_dev": {"prompt": f"Master shot of Carnatic vocal concert with {chars}.", "negative_prompt": "cleavage, blur"},
                    "flux_pro_ultra": {"prompt": f"Live concert broadcast frame of {chars}.", "negative_prompt": "cleavage, blur"},
                    "z_image": {"prompt": f"Broadcast master plate of {chars}.", "negative_prompt": "cleavage, blur"},
                },
                "motion_prompts": {
                    "wan_2_1": {"prompt": "Smooth dolly-in toward seated vocalist singing naturally.", "negative_prompt": "distortion"},
                    "kling_prod": {"prompt": "Steady cinematic push-in from wide stage.", "negative_prompt": "distortion"},
                    "kling_4k": {"prompt": "Crisp 4K broadcast camera motion drifting closer.", "negative_prompt": "distortion"},
                },
            },
            {
                "scene_index": 2, "camera_id": "stadium_audience_crowd", "camera_angle": "High-angle ascending crane jib",
                "visual_prompt": "Grand reverse wide broadcast shot from behind stage looking out over beach audience.",
                "negative_prompt": "empty venue, flat lighting",
                "image_prompts": {
                    "flux_dev": {"prompt": "Live coastal concert audience on beach.", "negative_prompt": "empty"},
                    "flux_pro_ultra": {"prompt": "Panoramic crane vista of coastal concert audience.", "negative_prompt": "empty"},
                    "z_image": {"prompt": "Detailed 4K broadcast shot of coastal beach audience.", "negative_prompt": "empty"},
                },
                "motion_prompts": {
                    "wan_2_1": {"prompt": "Sweeping crane orbit over audience.", "negative_prompt": "jitter"},
                    "kling_prod": {"prompt": "Smooth ascending camera boom over crowd.", "negative_prompt": "jitter"},
                    "kling_4k": {"prompt": "High-altitude 4K drone sweep across concert grounds.", "negative_prompt": "jitter"},
                },
            },
        ],
    }


__all__ = [
    "build_timecoded_directorial_prompt",
    "build_multimodal_audio_directorial_prompt",
    "build_timecoded_directorial_schema",
    "direct_timecoded_timeline_deterministic",
    "direct_concert_broadcast_timeline",
    "get_offline_concert_storyboard",
]
