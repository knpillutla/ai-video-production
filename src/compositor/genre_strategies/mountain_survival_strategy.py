"""Mountain & Extreme Climate Survival Documentary Strategy (BBC Human Planet / NatGeo Style).

Orchestration config: Gemini survival narration → TTS → FLUX keyframes → Kling motion → FFmpeg 4K.
Audio: TTS authoritative narration + sparse melancholic acoustic score. Lipsync: none.
FPS: 24 (heavy cinematic film cadence). Directive 18.
"""

from typing import Any

from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check
from src.mcp.prompt_director.directorial_router import build_directorial_prompt


class MountainSurvivalStrategy:
    """Genre strategy for extreme climate survival documentaries."""

    genre_id = "mountain_survival"
    default_fps = 24
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
            topic=idea or title, genre=genre or "mountain_survival",
            video_format="mountain_survival",
            target_duration_seconds=duration_seconds, language=language,
        )
        return prompt

    def build_gemini_schema(self) -> dict:
        """Schema for survival documentaries — atmospheric, foley-rich."""
        scene = {
            "type": "OBJECT",
            "properties": {
                "scene_index": {"type": "INTEGER"},
                "duration_seconds": {"type": "NUMBER"},
                "location": {"type": "STRING"},
                "shot_type": {"type": "STRING"},
                "visual_prompt": {"type": "STRING"},
                "motion_prompt": {"type": "STRING"},
                "dialogue": {"type": "STRING"},
                "foley_sfx": {"type": "STRING"},
                "atmospheric_detail": {"type": "STRING"},
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
        issues = default_storyboard_sanity_check(storyboard)
        scenes = storyboard.get("scenes", [])
        has_narration = any(s.get("dialogue") for s in scenes if isinstance(s, dict))
        if scenes and not has_narration:
            issues.append("survival documentary must include narration (YPP anti-demonetization)")
        return issues

    def get_directorial_template_name(self) -> str:
        return "mountain_survival.md"

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


__all__ = ["MountainSurvivalStrategy"]
