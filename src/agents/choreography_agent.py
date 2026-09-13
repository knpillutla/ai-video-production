"""Choreography Agent: Generates audio-synchronized dance motion & pose sequences."""

from __future__ import annotations
import math
from pathlib import Path
from typing import Any, Dict, List
from src.core.telemetry import logger
from src.providers.dance.fal_mimicmotion import mimicmotion_adapter


class ChoreographyAgent:
    """Orchestrates musical beat alignment, dance pose choreography, and motion synthesis."""

    def __init__(self) -> None:
        self.dance_styles = {
            "hiphop": ["bounce_groove", "popping_chest", "footwork_glide", "freeze_pose"],
            "bollywood": ["thumka_sway", "bhangra_kick", "spin_elevation", "namaste_hold"],
            "tollywood_mass": ["mass_step", "lungi_swag", "fast_feet_hook", "slow_tilt"],
            "cinematic": ["fluid_waltz", "pirouette", "dramatic_reach", "epic_crescendo"],
        }

    def detect_beat_grid(
        self,
        tempo_bpm: float = 120.0,
        duration_sec: float = 8.0,
    ) -> List[float]:
        """Compute deterministic beat timestamps and downbeats for motion synchronization."""
        beat_interval = 60.0 / max(tempo_bpm, 60.0)
        num_beats = int(math.ceil(duration_sec / beat_interval))
        return [round(i * beat_interval, 3) for i in range(num_beats)]

    def plan_choreography(
        self,
        genre: str = "tollywood_mass",
        tempo_bpm: float = 128.0,
        duration_sec: float = 8.0,
    ) -> Dict[str, Any]:
        """Create a structured choreography beat sheet synchronized to musical phrases."""
        beats = self.detect_beat_grid(tempo_bpm, duration_sec)
        style_moves = self.dance_styles.get(genre, self.dance_styles["tollywood_mass"])

        sections: List[Dict[str, Any]] = []
        step_duration = max(1.5, duration_sec / len(style_moves))

        current_time = 0.0
        for i, move in enumerate(style_moves):
            end_time = min(duration_sec, round(current_time + step_duration, 2))
            # Find beats falling within this move's time window
            move_beats = [b for b in beats if current_time <= b < end_time]
            sections.append({
                "sequence_index": i + 1,
                "move_name": move,
                "start_time": round(current_time, 2),
                "end_time": end_time,
                "sync_beats": move_beats,
                "energy_level": "high" if i in (1, 2) else "medium",
            })
            current_time = end_time
            if current_time >= duration_sec:
                break

        return {
            "genre": genre,
            "tempo_bpm": tempo_bpm,
            "total_duration": duration_sec,
            "total_sections": len(sections),
            "choreography": sections,
        }

    async def execute_dance_synthesis(
        self,
        character_image: Path | str,
        audio_stem: Path | str,
        output_clip_path: Path | str,
        genre: str = "tollywood_mass",
        duration_sec: float = 6.0,
    ) -> Dict[str, Any]:
        """Execute pose transfer and render synchronized dance clip."""
        # Enforce cost guard: clamp to <= 10.0s
        clamped_duration = min(duration_sec, 10.0)
        plan = self.plan_choreography(genre=genre, duration_sec=clamped_duration)

        logger.info(f"choreography_agent_executing: {genre} for {clamped_duration}s")
        rendered_path = await mimicmotion_adapter.transfer_dance_motion(
            character_image_path=character_image,
            motion_or_audio_path=audio_stem,
            output_path=output_clip_path,
            duration_seconds=clamped_duration,
        )

        return {
            "status": "success",
            "choreography_plan": plan,
            "video_path": str(rendered_path),
            "duration_sec": clamped_duration,
            "beat_sync_count": len(plan["choreography"]),
        }


choreography_agent = ChoreographyAgent()

__all__ = ["ChoreographyAgent", "choreography_agent"]
