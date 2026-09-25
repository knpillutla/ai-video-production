"""Nature Documentary Genre Strategy (BBC Planet Earth / NatGeo Style).

Orchestration config: Gemini narration script → TTS voiceover → FLUX keyframes → Kling motion → FFmpeg 4K.
Audio: TTS authoritative narration + orchestral BGM. Lipsync: none.
FPS: 24 (cinematic film cadence). Directive 17.
"""

from typing import Any

from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check
from src.mcp.prompt_director.directorial_router import build_directorial_prompt


class NatureDocumentaryStrategy:
    """Genre strategy for blue-chip nature and wildlife documentaries."""

    genre_id = "nature_documentary"
    default_fps = 24
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
            topic=idea or title, genre=genre or "nature_documentary",
            video_format="nature_documentary",
            target_duration_seconds=duration_seconds, language=language,
        )
        return prompt

    def build_gemini_schema(self) -> dict:
        """Standard storyboard schema for narration-driven content."""
        scene = {
            "type": "OBJECT",
            "properties": {
                "scene_index": {"type": "INTEGER"},
                "duration_seconds": {"type": "NUMBER"},
                "location": {"type": "STRING"},
                "shot_type": {"type": "STRING"},
                "camera_movement": {"type": "STRING"},
                "motion_domain": {
                    "type": "STRING",
                    "enum": [
                        "landscape_solid",
                        "water_fluid",
                        "water_impact_collision",
                        "wildlife_animal",
                        "human_action",
                        "atmospheric_weather",
                        "macro_botanical",
                        "aerial_fpv",
                        "celestial_nightscape",
                    ],
                },
                "visual_prompt": {"type": "STRING"},
                "motion_prompt": {"type": "STRING"},
                "dialogue": {"type": "STRING"},
                "foley_sfx": {"type": "STRING"},
            },
            "required": ["scene_index", "duration_seconds", "location", "shot_type",
                         "motion_domain", "visual_prompt", "motion_prompt", "dialogue"],
        }
        character = {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING"}, "age": {"type": "INTEGER"},
                "gender": {"type": "STRING"}, "role": {"type": "STRING"},
                "relationship": {"type": "STRING"},
                "appearance_summary": {"type": "STRING"},
            },
            "required": ["name", "role"],
        }
        return {
            "type": "OBJECT",
            "properties": {
                "title_en": {"type": "STRING"}, "title_localized": {"type": "STRING"},
                "titles_multilingual": {"type": "OBJECT"},
                "hook_thesis": {"type": "STRING"},
                "recommended_fps": {"type": "INTEGER"},
                "vocal_gender": {"type": "STRING"},
                "characters": {"type": "ARRAY", "items": character},
                "scenes": {"type": "ARRAY", "items": scene},
            },
            "required": ["title_en", "title_localized", "hook_thesis",
                         "recommended_fps", "vocal_gender", "characters", "scenes"],
        }

    def validate_storyboard(self, storyboard: dict) -> list[str]:
        issues = default_storyboard_sanity_check(storyboard)
        # Nature docs must have narration dialogue in scenes
        scenes = storyboard.get("scenes", [])
        has_narration = any(s.get("dialogue") for s in scenes if isinstance(s, dict))
        if scenes and not has_narration:
            issues.append("nature documentary must include narration dialogue in scenes")
        return issues

    def get_directorial_template_name(self) -> str:
        return "nature_documentary.md"

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


__all__ = ["NatureDocumentaryStrategy"]
