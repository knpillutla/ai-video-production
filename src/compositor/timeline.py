"""Multi-Track Scene Timeline Compiler for Single-Pass Compositing."""

from dataclasses import dataclass, field
from pathlib import Path

from src.scripts.local_pan_zoom import CameraMovement, assign_scene_camera_movement


@dataclass
class SceneTrackItem:
    """Individual scene layout element on the production timeline."""

    scene_index: int
    duration_seconds: float
    start_time: float
    end_time: float
    image_path: Path | None = None
    voice_path: Path | None = None
    shot_type: str = "medium"
    camera_movement: CameraMovement = CameraMovement.SLOW_ZOOM_IN
    dialogue_text: str = ""


@dataclass
class CompiledTimeline:
    """Compiled timeline ready for single-pass FFmpeg graph construction."""

    scenes: list[SceneTrackItem]
    total_duration_seconds: float
    speech_intervals: list[tuple[float, float]] = field(default_factory=list)
    bgm_path: Path | None = None
    subtitle_path: Path | None = None
    target_resolution: tuple[int, int] = (1920, 1080)
    fps: int = 30


def compile_timeline_from_scenes(
    scene_data: list[dict],
    bgm_path: Path | str | None = None,
    subtitle_path: Path | str | None = None,
    target_resolution: tuple[int, int] = (1920, 1080),
    fps: int = 30,
) -> CompiledTimeline:
    """Compile ordered scenes into a synchronized multi-track timeline layout."""
    track_items: list[SceneTrackItem] = []
    speech_intervals: list[tuple[float, float]] = []
    current_time = 0.0

    for idx, sc in enumerate(scene_data):
        dur = float(sc.get("duration_seconds", 4.0))
        shot_type = sc.get("shot_type", "medium")
        movement = assign_scene_camera_movement(idx, shot_type)

        item = SceneTrackItem(
            scene_index=idx,
            duration_seconds=dur,
            start_time=current_time,
            end_time=current_time + dur,
            image_path=Path(sc["image_path"]) if "image_path" in sc and sc["image_path"] else None,
            voice_path=Path(sc["voice_path"]) if "voice_path" in sc and sc["voice_path"] else None,
            shot_type=shot_type,
            camera_movement=movement,
            dialogue_text=sc.get("dialogue", ""),
        )
        track_items.append(item)

        # Record speech interval for audio ducking
        if item.voice_path and (not hasattr(item.voice_path, "exists") or item.voice_path.exists()):
            speech_intervals.append((current_time, current_time + dur))

        current_time += dur

    return CompiledTimeline(
        scenes=track_items,
        total_duration_seconds=round(current_time, 2),
        speech_intervals=speech_intervals,
        bgm_path=Path(bgm_path) if bgm_path else None,
        subtitle_path=Path(subtitle_path) if subtitle_path else None,
        target_resolution=target_resolution,
        fps=fps,
    )


__all__ = [
    "SceneTrackItem",
    "CompiledTimeline",
    "compile_timeline_from_scenes",
]
