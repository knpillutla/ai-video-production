"""Audio & Foley Mastering Agent for ducking curves, stem isolation, and mix leveling."""

from pathlib import Path
from typing import Any
from src.core.telemetry import logger
from src.providers.audio.demucs_adapter import demucs_separator
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.scripts.local_audio_ducking import (
    build_sidechain_ducking_filter,
    build_timeline_volume_expression,
    calculate_ducking_volume_db,
)


class AudioFoleyAgent:
    """Specialized Agent for audio ducking math, vocal separation, and BGM foley dynamics."""

    def __init__(self):
        self.music = SunoMusicAdapter()

    async def score_soundtrack(
        self,
        output_path: Path | str,
        genre: str = "cinematic comedy",
        duration_seconds: float = 12.0,
    ) -> Path:
        """Compose commercially cleared background soundtrack."""
        return await self.music.generate_to_file(output_path, genre=genre, duration_seconds=duration_seconds)

    async def separate_vocal_and_instrumental_stems(
        self,
        audio_path: Path | str,
        output_dir: Path | str,
    ) -> dict[str, Path]:
        """Isolate vocal lines from background instrumentals using Demucs."""
        return await demucs_separator.separate_stems(audio_path, output_dir)

    def compute_ducking_graph(
        self,
        speech_intervals: list[tuple[float, float]],
        base_volume: float = 0.25,
        ducked_volume: float = 0.07,
    ) -> dict[str, Any]:
        """Compute deterministic FFmpeg volume expressions to dip BGM under dialogue."""
        vol_expr = build_timeline_volume_expression(
            speech_intervals,
            base_volume=base_volume,
            ducked_volume=ducked_volume,
        )
        sidechain = build_sidechain_ducking_filter("[voice]", "[bgm]", "[ducked]")

        return {
            "volume_expression": vol_expr,
            "sidechain_filter": sidechain,
            "base_db": calculate_ducking_volume_db(speech_active=False),
            "ducked_db": calculate_ducking_volume_db(speech_active=True),
            "speech_intervals_count": len(speech_intervals),
        }


audio_foley_agent = AudioFoleyAgent()

__all__ = ["AudioFoleyAgent", "audio_foley_agent"]
