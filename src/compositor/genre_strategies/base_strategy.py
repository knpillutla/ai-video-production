"""Genre Strategy Protocol & Base Infrastructure.

Each content genre (dance, nature, walking tour, comedy, etc.) implements the
GenreStrategy protocol. The pipeline resolves the right strategy via classify,
then delegates prompt building, schema, audio mode, and FFmpeg chain to it.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class GenreStrategy(Protocol):
    """Protocol that every genre strategy must implement."""

    genre_id: str
    default_fps: int
    audio_mode: str       # "song" | "narration" | "dialogue" | "ambient"
    lipsync_mode: str     # "musical" | "speech" | "none"
    enable_voice_over: bool
    enable_bgm: bool

    def build_gemini_prompt(
        self, title: str, duration_seconds: int, language: str,
        genre: str, idea: str | None, art_style: str | None,
        culture_ctx: Any | None,
    ) -> str:
        """Build the Gemini Tier-2 prompt for this genre's storyboard."""
        ...

    def build_gemini_schema(self) -> dict:
        """Return the Gemini-compatible JSON schema for structured output."""
        ...

    def validate_storyboard(self, storyboard: dict) -> list[str]:
        """Lightweight sanity check — has required fields? Returns list of issues."""
        ...

    def get_directorial_template_name(self) -> str:
        """Return the prompt director template filename for this genre."""
        ...

    def get_ffmpeg_filter_args(self, fps: int, duration: float) -> list[str]:
        """Return FFmpeg filter_complex and output args for final mastering."""
        ...


def default_storyboard_sanity_check(storyboard: dict) -> list[str]:
    """Universal lightweight storyboard sanity check shared across strategies."""
    issues: list[str] = []
    if not storyboard.get("scenes"):
        issues.append("storyboard has no scenes")
    if not storyboard.get("characters"):
        issues.append("storyboard has no characters")
    scenes = storyboard.get("scenes", [])
    for i, scene in enumerate(scenes):
        if not scene.get("visual_prompt"):
            issues.append(f"scene {i} has no visual_prompt")
    return issues


__all__ = ["GenreStrategy", "default_storyboard_sanity_check"]
