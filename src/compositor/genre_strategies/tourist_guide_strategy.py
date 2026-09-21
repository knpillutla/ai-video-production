"""Tourist Attractions & City Guide Genre Strategy.

Orchestration config: Gemini countdown/itinerary script → TTS educational guide voiceover → FLUX 4K keyframes → Kling motion → FFmpeg 4K.
Audio: Authoritative/energetic travel commentary + upbeat regional BGM. Lipsync: none.
FPS: 30 (broadcast television travel guide standard).
"""

from typing import Any

from src.compositor.genre_strategies.base_strategy import default_storyboard_sanity_check
from src.compositor.pipeline_prompts import extract_dialogue_text
from src.mcp.prompt_director.directorial_router import build_directorial_prompt


class TouristGuideStrategy:
    """Genre strategy for tourist attractions, top 10 destination countdowns, and multi-day city guides."""

    genre_id = "tourist_guide"
    default_fps = 30
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
            topic=idea or title,
            genre=genre or "travel_tourism",
            video_format="travel_guide",
            target_duration_seconds=duration_seconds,
            language=language,
        )
        return prompt

    def build_gemini_schema(self) -> dict:
        """Schema for curated city itinerary / tourist attractions countdown."""
        scene = {
            "type": "OBJECT",
            "properties": {
                "scene_index": {"type": "INTEGER"},
                "duration_seconds": {"type": "NUMBER"},
                "location": {"type": "STRING"},
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
                "title_en": {"type": "STRING"},
                "title_localized": {"type": "STRING"},
                "titles_multilingual": {"type": "OBJECT"},
                "hook_thesis": {"type": "STRING"},
                "recommended_fps": {"type": "INTEGER"},
                "scenes": {"type": "ARRAY", "items": scene},
            },
            "required": ["title_en", "title_localized", "hook_thesis",
                         "recommended_fps", "scenes"],
        }

    def validate_storyboard(self, storyboard: dict) -> list[str]:
        issues = default_storyboard_sanity_check(storyboard)
        scenes = storyboard.get("scenes", [])
        for i, s in enumerate(scenes):
            if isinstance(s, dict) and not extract_dialogue_text(s).strip():
                issues.append(f"scene {i} has no guide commentary dialogue")
        return issues

    def get_directorial_template_name(self) -> str:
        return "tech_explainer.md"

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


__all__ = ["TouristGuideStrategy"]
