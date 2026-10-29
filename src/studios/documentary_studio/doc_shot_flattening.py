"""Documentary Shot Flattening & Scene Extraction Service.

In-memory shot selector sequentially extracting shots from Chapter 1 Shot 1 downwards.
Handles duration constraints, shot counts, and geographic coordinates propagation.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def _normalize_coords(coords: Any) -> List[float]:
    """Normalize dict {'lat', 'lng'} or sequence into [lat, lng] float list."""
    if isinstance(coords, dict):
        lat = coords.get("lat") if coords.get("lat") is not None else coords.get("latitude", 0.0)
        lng = coords.get("lng") if coords.get("lng") is not None else (coords.get("lon") if coords.get("lon") is not None else coords.get("longitude", 0.0))
        try:
            return [float(lat), float(lng)]
        except Exception:
            return [0.0, 0.0]
    if isinstance(coords, (list, tuple)) and len(coords) >= 2:
        try:
            return [float(coords[0]), float(coords[1])]
        except Exception:
            return [0.0, 0.0]
    return [0.0, 0.0]


def flatten_chapters_to_scenes(
    chapters: List[Dict[str, Any]],
    target_duration: Optional[float] = None,
    num_shots: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """In-memory shot selector sequentially extracting shots from Chapter 1 Shot 1 downwards.

    If target_duration > 0 and != -1, accumulates shots fitting within target_duration.
    Once accumulated duration reaches or exceeds target_duration, stops and returns.
    If target_duration is None, <= 0, or -1, returns all shots across all chapters.
    """
    scenes: List[Dict[str, Any]] = []
    accumulated_duration = 0.0
    scene_idx = 1

    for ch in chapters:
        ch_idx = ch.get("chapter_index") or 1
        ch_title = ch.get("chapter_title") or f"Chapter {ch_idx}"
        ch_sub = ch.get("chapter_subtitle") or ""
        ch_badge = ch.get("fact_badge") or ""
        ch_stats = ch.get("chapter_stats") or ""
        ch_narr = ch.get("narration_text") or ch.get("narration") or ""
        ch_coords = _normalize_coords(ch.get("origin_coords"))
        shots = ch.get("shots") or []

        if not shots:
            shots = [{
                "shot_index": 1,
                "shot_type": ch.get("shot_type") or "wide_aerial_panoramic",
                "duration_seconds": float(ch.get("chapter_total_duration") or ch.get("duration_seconds") or 15.0),
                "origin_coords": ch_coords,
                "visual_prompt": ch.get("visual_prompt") or ch_narr or ch_title,
                "motion_type": ch.get("motion_type", "ken_burns"),
                "recommended_model": ch.get("recommended_model", "local_drone"),
                "camera_movement": ch.get("camera_movement", "slow_drone_forward"),
                "model_configs": ch.get("model_configs") or {},
            }]

        for s in shots:
            s_idx = s.get("shot_index") or 1
            s_dur = float(s.get("duration_seconds") or 15.0)

            coords = _normalize_coords(s.get("origin_coords")) if s.get("origin_coords") else ch_coords
            loc_hub = s.get("location_hub") or ch.get("location_hub") or f"{ch_title} - {s.get('shot_type', f'Shot {s_idx}')}"
            prompt = s.get("visual_prompt") or s.get("visual_description") or s.get("description") or ch.get("visual_directive") or ch_title
            m_prompt = s.get("motion_prompt") or s.get("visual_description") or s.get("description") or prompt

            sc = {
                "scene_index": scene_idx,
                "shot_index": s_idx,
                "shot_type": s.get("shot_type") or "wide_aerial_panoramic",
                "location_hub": loc_hub,
                "visual_prompt": prompt,
                "motion_prompt": m_prompt,
                "motion_type": s.get("motion_type", "ken_burns"),
                "recommended_model": s.get("recommended_model", "local_drone"),
                "camera_movement": s.get("camera_movement", "slow_drone_forward"),
                "model_configs": s.get("model_configs") or {},
                "image_model_configs": s.get("image_model_configs") or {},
                "duration_seconds": s_dur,
                "origin_coords": coords,
                "chapter_index": ch_idx,
                "chapter_title": ch_title,
                "chapter_subtitle": ch_sub if s_idx == 1 else None,
                "fact_badge": ch_badge if s_idx == 1 else None,
                "chapter_stats": ch_stats if s_idx == 1 else None,
                "narration_text": ch_narr if s_idx == 1 else "",
                "is_chapter_head": (s_idx == 1),
            }
            if target_duration and target_duration > 0 and target_duration != -1 and scenes and (accumulated_duration + s_dur) > target_duration:
                return scenes

            scenes.append(sc)
            accumulated_duration += s_dur
            scene_idx += 1

            if target_duration and target_duration > 0 and target_duration != -1 and accumulated_duration >= target_duration:
                return scenes

            if num_shots and num_shots > 0 and num_shots != -1 and len(scenes) >= num_shots:
                return scenes

    return scenes


def extract_documentary_shots(
    screenplay_data: Dict[str, Any],
    target_duration: Optional[float] = None,
    num_shots: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Read documentary shots directly from screenplay_data['chapters'][i]['shots'] in-memory."""
    chapters = screenplay_data.get("chapters") or []
    return flatten_chapters_to_scenes(chapters, target_duration=target_duration, num_shots=num_shots)


__all__ = ["flatten_chapters_to_scenes", "extract_documentary_shots", "_normalize_coords"]
