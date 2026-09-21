"""Comedy / Web Series Genre Strategy.

Orchestration config: Gemini dialogue script → Multi-character TTS → FLUX keyframes → Kling motion → LatentSync (speech) → FFmpeg 4K.
Audio: Multi-character TTS dialogue + BGM. Lipsync: speech (driven by dialogue TTS).
FPS: 24 (cinematic drama cadence).
"""

from typing import Any

from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check
from src.mcp.prompt_director.directorial_router import build_directorial_prompt


class ComedyStrategy:
    """Genre strategy for comedy, web series, sitcoms, and dialogue-driven drama."""

    genre_id = "comedy"
    default_fps = 24
    audio_mode = "dialogue"
    lipsync_mode = "speech"
    enable_voice_over = True
    enable_bgm = True

    def build_gemini_prompt(
        self, title: str, duration_seconds: int, language: str,
        genre: str, idea: str | None, art_style: str | None,
        culture_ctx: Any | None, **kwargs: Any,
    ) -> str:
        prompt, _ = build_directorial_prompt(
            topic=idea or title, genre=genre or "comedy",
            video_format="web_series",
            target_duration_seconds=duration_seconds, language=language,
        )
        return prompt

    def build_gemini_schema(self) -> dict:
        """Schema for dialogue-driven content with multi-character scenes."""
        dialogue_line = {
            "type": "OBJECT",
            "properties": {
                "character": {"type": "STRING"},
                "text": {"type": "STRING"},
                "emotion": {"type": "STRING"},
            },
            "required": ["character", "text"],
        }
        scene = {
            "type": "OBJECT",
            "properties": {
                "scene_index": {"type": "INTEGER"},
                "duration_seconds": {"type": "NUMBER"},
                "location": {"type": "STRING"},
                "shot_type": {"type": "STRING"},
                "visual_prompt": {"type": "STRING"},
                "motion_prompt": {"type": "STRING"},
                "dialogue": {"type": "ARRAY", "items": dialogue_line},
            },
            "required": ["scene_index", "duration_seconds", "location",
                         "visual_prompt", "dialogue"],
        }
        character = {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING"}, "age": {"type": "INTEGER"},
                "gender": {"type": "STRING"},
                "body_composition": {"type": "STRING"}, "height": {"type": "STRING"},
                "role": {"type": "STRING"}, "relationship": {"type": "STRING"},
                "appearance_summary": {"type": "STRING"},
            },
            "required": ["name", "age", "gender", "role", "appearance_summary"],
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
        scenes = storyboard.get("scenes", [])
        has_dialogue = any(s.get("dialogue") for s in scenes if isinstance(s, dict))
        if scenes and not has_dialogue:
            issues.append("comedy/web_series must include character dialogue")
        return issues

    def get_directorial_template_name(self) -> str:
        return "narrative_satire.md"

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


__all__ = ["ComedyStrategy"]
