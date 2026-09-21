"""Epic Cinematic Genre Strategy (Bahubali / Avatar / Blockbuster Scale).

Orchestration config: Gemini dramatic script → TTS dialogue → FLUX VFX keyframes → Kling motion → LatentSync → FFmpeg 4K.
Audio: Multi-character TTS + orchestral score + SFX. Lipsync: speech.
FPS: 24 (cinematic film cadence).
"""

from typing import Any

from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check
from src.mcp.prompt_director.directorial_router import build_directorial_prompt


class EpicCinematicStrategy:
    """Genre strategy for epic cinematic productions, blockbusters, and VFX-heavy films."""

    genre_id = "epic_cinematic"
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
            topic=idea or title, genre=genre or "epic_action",
            video_format="movie_cinematic",
            target_duration_seconds=duration_seconds, language=language,
        )
        return prompt

    def build_gemini_schema(self) -> dict:
        """Schema for epic cinematic: VFX-intensive, battle choreography, massive scale."""
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
                "vfx_elements": {"type": "STRING"},
                "visual_prompt": {"type": "STRING"},
                "motion_prompt": {"type": "STRING"},
                "dialogue": {"type": "ARRAY", "items": dialogue_line},
                "sfx_description": {"type": "STRING"},
            },
            "required": ["scene_index", "duration_seconds", "location",
                         "visual_prompt", "motion_prompt"],
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
        return default_storyboard_sanity_check(storyboard)

    def get_directorial_template_name(self) -> str:
        return "narrative_satire.md"

    def get_ffmpeg_filter_args(self, fps: int, duration: float) -> list[str]:
        return [
            "-filter_complex",
            "[0:v]scale=3840:2160:flags=lanczos,unsharp=3:3:0.5:3:3:0.0[v_out];"
            "[1:a]loudnorm=I=-14.0:TP=-1.0:LRA=7.0[a_out]",
            "-map", "[v_out]", "-map", "[a_out]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-b:v", "35M",
            "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-t", str(duration),
            "-movflags", "+faststart",
        ]


__all__ = ["EpicCinematicStrategy"]
