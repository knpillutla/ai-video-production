"""Walking Tour Genre Strategy (POV Scenic / Travel).

Orchestration config: Gemini narration script → TTS commentary → FLUX keyframes → Kling motion → FFmpeg 4K.
Audio: TTS educational commentary + ambient BGM. Lipsync: none (no on-screen character).
FPS: 60 (fluid immersive POV). Directives 13, 14.
"""

from typing import Any

from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check
from src.mcp.prompt_director.directorial_router import build_directorial_prompt


class WalkingTourStrategy:
    """Genre strategy for first-person POV walking tours and scenic drives."""

    genre_id = "walking_tour"
    default_fps = 60
    audio_mode = "narration"
    lipsync_mode = "none"
    enable_voice_over = True
    enable_bgm = True

    def build_gemini_prompt(
        self, title: str, duration_seconds: int, language: str,
        genre: str, idea: str | None, art_style: str | None,
        culture_ctx: Any | None, **kwargs: Any,
    ) -> str:
        prompt, _ = build_directorial_prompt(
            topic=idea or title, genre=genre or "scenic_walking_tour",
            video_format="walking_tour",
            target_duration_seconds=duration_seconds, language=language,
        )
        target_scenes = max(1, round(duration_seconds / 10.0))
        strict_pov = (
            f"\n\nCRITICAL DIRECTIVES FOR WALKING TOURS (Directives 11, 13, 14):\n"
            f"0. TARGET SCENE COUNT & PACING: For a {duration_seconds}-second video, you MUST generate EXACTLY {target_scenes} scenes of 10.0 seconds each (or 15s for long form), perfectly summing to {duration_seconds}s total.\n"
            "1. STRICT FIRST-PERSON EYE-LEVEL POV (ZERO FOREGROUND AVATAR OBSTRUCTION): The camera IS the viewer walking forward at an ultra-slow, peaceful 1.5–2.0 km/h cadence. "
            "Never place a single synthetic character or avatar directly in front of the camera lens. The 'characters' array MUST BE AN EMPTY LIST []. "
            "All shots are viewed from the direct eye-level perspective of the viewer exploring the environment.\n"
            "2. AUTHENTIC URBAN BACKGROUND LIFE & UNOBSTRUCTED WALKING PATH: "
            "The center walking path directly ahead of the camera MUST remain open, clear, and unobstructed for smooth steadycam exploration. "
            "In urban settings, place natural background life along the perimeter: locals seated at sidewalk cafe terraces, people standing under shop awnings, browsing store windows, or seated on benches in the distant background depth. "
            "Strictly prohibit pedestrians walking directly into the camera lens or crossing the immediate center path, preventing AI motion ghosting and transparent human diffusion artifacts. "
            "In wilderness/alpine settings, the trail remains pristine and tranquil.\n"
            "3. NATURAL DAYLIGHT & AUTHENTIC PRECIPITATION INTENSITY: Outdoor scenes MUST default to crisp, balanced natural open-air daylight (5400K–5600K color temperature, natural balanced lighting). "
            "For HEAVY RAIN / THUNDERSTORM: render torrential diagonal rain downpour, stormy clouds, flooded streets with deep reflective puddles, raindrops bouncing off pavements, and heavy splashing foley. "
            "For LIGHT RAIN / GENTLE DRIZZLE: render fine delicate micro-raindrops, soft overcast daylight, glistening damp pavement with subtle sheen (NO deep flooded sheets), and soothing drizzle pitter-patter. Strictly PROHIBIT artificial yellow lens flares or muddy lighting.\n"
            "4. ULTRA-SLOW TRANQUIL WALKING CADENCE & DYNAMIC WEATHER PHYSICS: Every scene's 'motion_prompt' MUST strictly enforce ultra-slow, gentle steadycam forward glide at ~1.5–2.0 km/h with subtle natural human footstep sway, clear unobstructed walkway ahead, tack-sharp background architecture. In addition, whenever weather or atmospheric elements are present, 'motion_prompt' MUST explicitly command dynamic environmental physics: for heavy rain, forceful continuous falling rain streaks and splashing puddle ripples; for light rain/drizzle, fine delicate micro-raindrops drifting down with gentle water sheen; for snow blizzard, intense swirling wind gusts and blowing powder snow; for gentle snow, delicate drifting crystalline flakes floating slowly down; for cloudy/overcast, moody low-hanging clouds drifting across the sky; for mist/fog, rolling tendrils of atmospheric mist shifting across the path.\n"
            "5. TACK-SHARP OPTICAL CLARITY (5500K / 24MM PRIME): Every scene's 'visual_prompt' must specify edge-to-edge optical clarity, fine architectural textures, crystal reflections, and zero atmospheric haze.\n"
            "6. SPOKEN TRAIL NARRATION (AZURE SPEECH): Under YouTube Partner Program monetization standards, every single scene's 'dialogue' field MUST contain engaging, spoken educational trail guide commentary explaining geological history, landscape features, or cultural lore. Off-screen narration voiceover only.\n"
            "7. DIRECTORIAL 3-TIER PACING BLUEPRINT (ANCHOR, TRANSITION, CUTAWAY):\n"
            "   - TIER 1 THE ANCHOR (STATIC + SUBTLE ZOOM): Flawless 4K wide establishing shot of a landmark ('steadycam_vista', 'slow_zoom_in' scale 100% to 105%), mimicking a steady camera operator on a tripod.\n"
            "   - TIER 2 THE TRANSITION (BALANCED AI MOTION): Dynamic image-to-video motion clip ('kinetic_video') with gentle forward movement, walking cadence, and live atmosphere.\n"
            "   - TIER 3 THE CUTAWAY (MACRO DETAIL REST FRAME): Tightly cropped macro shot of local architectural details, historical statues, street cafes, or clock towers ('steadycam_vista', 'pan_left', 'pan_right', or 'tilt_up') to give the viewer's eyes a complete rest from forward traveling motion.\n"
            "8. CRISP STATIONARY BACKGROUND PEDESTRIAN POSTURES (NO MID-STRIDE MOTION BLUR): Background pedestrians in both 'steadycam_vista' and 'kinetic_video' scenes MUST be rendered in crisp, grounded postures—standing admiring architecture, seated at cafe tables, or resting on benches in deep background depth. NEVER generate motion-blurred, mid-stride, or transparent human figures.\n"
            "9. ARCHITECTURAL GEOMETRY & KEN BURNS CAMERA MOVEMENT SELECTION: For every scene, analyze the architectural geometry and spatial framing to command the ideal 'camera_movement':\n"
            "   - 'pan_left' or 'pan_right': For wide horizontal facades, panoramic town squares, riverfronts, and market streets.\n"
            "   - 'tilt_up' or 'tilt_down': For tall vertical architecture (Gothic cathedral spires, high clock towers, monument pillars).\n"
            "   - 'slow_zoom_in': For deep vanishing-point corridors, narrow cobblestone alleys, or archway portals.\n"
            "   - 'slow_zoom_out': For grand opening reveals and expansive courtyard vistas.\n"
            "10. CINEMATIC SCENE ORDERING & SHOT PROGRESSION: Always open Scene 0 with the Tier 1 Anchor shot. Alternate cyclically between Tier 2 Transitions (kinetic glides) and Tier 3 Cutaways (macro detail pans), culminating in a grand closing reveal.\n"
        )
        return prompt + strict_pov

    def build_gemini_schema(self) -> dict:
        """Schema for POV walking tour: location-centric, no characters on screen."""
        scene = {
            "type": "OBJECT",
            "properties": {
                "scene_index": {"type": "INTEGER"},
                "duration_seconds": {"type": "NUMBER"},
                "location": {"type": "STRING"},
                "pov_perspective": {"type": "STRING"},
                "motion_type": {"type": "STRING", "description": "'kinetic_video' for active moving shots or 'steadycam_vista' for serene 4K panoramic vista glides"},
                "camera_movement": {"type": "STRING", "description": "'slow_zoom_in', 'slow_zoom_out', 'pan_left', 'pan_right', 'tilt_up', or 'tilt_down' based on architectural composition"},
                "visual_prompt": {"type": "STRING"},
                "motion_prompt": {"type": "STRING"},
                "dialogue": {"type": "STRING"},
                "ambient_sfx": {"type": "STRING"},
            },
            "required": ["scene_index", "duration_seconds", "location", "motion_type",
                         "camera_movement", "visual_prompt", "motion_prompt", "dialogue"],
        }
        return {
            "type": "OBJECT",
            "properties": {
                "title_en": {"type": "STRING"}, "title_localized": {"type": "STRING"},
                "titles_multilingual": {"type": "OBJECT"},
                "hook_thesis": {"type": "STRING"},
                "recommended_fps": {"type": "INTEGER"},
                "vocal_gender": {"type": "STRING"},
                "characters": {"type": "ARRAY", "items": {"type": "OBJECT"}},
                "scenes": {"type": "ARRAY", "items": scene},
            },
            "required": ["title_en", "title_localized", "hook_thesis",
                         "recommended_fps", "scenes"],
        }

    def validate_storyboard(self, storyboard: dict) -> list[str]:
        issues = [i for i in default_storyboard_sanity_check(storyboard) if "no characters" not in i]
        storyboard["characters"] = []
        scenes = storyboard.get("scenes", [])
        for s in scenes:
            if isinstance(s, dict):
                s["characters_present"] = []
        has_commentary = any(s.get("dialogue") for s in scenes if isinstance(s, dict))
        if scenes and not has_commentary:
            issues.append("walking tour must include educational commentary (YPP anti-demonetization)")
        return issues

    def get_directorial_template_name(self) -> str:
        return "scenic_walking_tour.md"

    def get_ffmpeg_filter_args(self, fps: int, duration: float) -> list[str]:
        return [
            "-filter_complex",
            "[0:v]scale=3840:2160:flags=lanczos[v_out];"
            "[1:a]loudnorm=I=-14.0:TP=-1.0:LRA=7.0[a_out]",
            "-map", "[v_out]", "-map", "[a_out]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-t", str(duration),
            "-movflags", "+faststart",
        ]


__all__ = ["WalkingTourStrategy"]
