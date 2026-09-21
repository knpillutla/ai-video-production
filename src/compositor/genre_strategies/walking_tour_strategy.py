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
        culture_ctx: Any | None,
    ) -> str:
        prompt, _ = build_directorial_prompt(
            topic=idea or title, genre=genre or "scenic_walking_tour",
            video_format="walking_tour",
            target_duration_seconds=duration_seconds, language=language,
        )
        strict_pov = (
            "\n\nCRITICAL DIRECTIVES FOR WALKING TOURS (Directives 11, 13):\n"
            "1. STRICT FIRST-PERSON EYE-LEVEL POV (ZERO ON-SCREEN CHARACTERS): The camera IS the viewer walking forward along the trail at an ultra-slow, peaceful 1.5–2.0 km/h stroll. "
            "There are ZERO on-screen characters, actors, hosts, or guides in frame. The 'characters' array MUST BE AN EMPTY LIST []. "
            "Every scene's 'visual_prompt' and 'motion_prompt' must describe ONLY the pristine path, trail, water, cliffs, architecture, and scenery viewed forward from an eye-level POV perspective.\n"
            "2. NATURAL OPEN-AIR DAYLIGHT MANDATE (5500K): Outdoor scenes MUST strictly default to crisp, balanced natural open-air daylight (5400K–5600K color temperature, natural blue sky, realistic environmental lighting). Strictly PROHIBIT night, twilight, dusk, blue hour, street lamps, lanterns, or dark lighting.\n"
            "3. ULTRA-SLOW TRANQUIL WALKING CADENCE (1.5–2.0 KM/H): Every scene's 'motion_prompt' MUST strictly enforce ultra-slow, gentle steadycam forward glide at ~1.5–2.0 km/h with subtle natural human footstep sway, unhurriedly lingering over the scenery. Strictly PROHIBIT fast movement, running, drone rushes, or sudden turns.\n"
            "4. TACK-SHARP OPTICAL CLARITY (5500K / 24MM PRIME): Every scene's 'visual_prompt' must specify edge-to-edge optical clarity, fine architectural textures, crystal reflections, and zero atmospheric haze.\n"
            "5. SPOKEN TRAIL NARRATION (AZURE SPEECH): Under YouTube Partner Program monetization standards, every single scene's 'dialogue' field MUST contain engaging, spoken educational trail guide commentary explaining geological history, landscape features, or cultural lore. Off-screen narration voiceover only.\n"
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
                "visual_prompt": {"type": "STRING"},
                "motion_prompt": {"type": "STRING"},
                "dialogue": {"type": "STRING"},
                "ambient_sfx": {"type": "STRING"},
            },
            "required": ["scene_index", "duration_seconds", "location",
                         "visual_prompt", "motion_prompt", "dialogue"],
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
