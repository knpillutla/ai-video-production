"""Dance Video Genre Strategy.

Orchestration config: Gemini lyrics → Suno music → FLUX keyframes → Kling motion → LatentSync → FFmpeg 4K.
Audio: Suno-composed song from Gemini lyrics. Lipsync: musical (driven by song vocal track).
"""

from typing import Any

from src.compositor.dance_schema import gemini_dance_schema
from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check
from src.compositor.pipeline_prompts import build_dance_storyboard_prompt


class DanceStrategy:
    """Genre strategy for musical dance videos (folk, mass, romantic, choreography)."""

    genre_id = "dance"
    default_fps = 30
    audio_mode = "song"
    lipsync_mode = "musical"
    enable_voice_over = False
    enable_bgm = True

    def build_gemini_prompt(
        self, title: str, duration_seconds: int, language: str,
        genre: str, idea: str | None, art_style: str | None,
        culture_ctx: Any | None, character_name: str | None = None, **kwargs: Any,
    ) -> str:
        return build_dance_storyboard_prompt(
            title=title, duration_seconds=duration_seconds,
            language=language, genre=genre, idea=idea, art_style=art_style,
            character_name=character_name,
        )

    def build_gemini_schema(self) -> dict:
        return gemini_dance_schema()

    def validate_storyboard(self, storyboard: dict) -> list[str]:
        issues = default_storyboard_sanity_check(storyboard)
        if not storyboard.get("lyrics"):
            issues.append("dance storyboard has no lyrics")
        if not storyboard.get("suno_tags"):
            issues.append("dance storyboard has no suno_tags")
        # Ensure at least one medium/close shot for face lipsync detection
        scenes = storyboard.get("scenes", [])
        has_face_shot = any(
            s.get("shot_type") in ("medium_shot", "close_up") for s in scenes if isinstance(s, dict)
        )
        if scenes and not has_face_shot:
            issues.append("at least one medium_shot or close_up is required for lip-sync")
        return issues

    def get_directorial_template_name(self) -> str:
        return "dance_choreography.md"

    def get_ffmpeg_filter_args(self, fps: int, duration: float) -> list[str]:
        return [
            "-filter_complex",
            "[0:v]scale=3840:2160:flags=lanczos,unsharp=5:5:0.8:5:5:0.0[v_out];"
            "[1:a]loudnorm=I=-14.0:TP=-1.0:LRA=7.0[a_out]",
            "-map", "[v_out]", "-map", "[a_out]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-b:v", "35M",
            "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-t", str(duration),
            "-movflags", "+faststart",
        ]


__all__ = ["DanceStrategy"]
