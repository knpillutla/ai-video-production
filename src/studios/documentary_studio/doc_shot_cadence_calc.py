"""Documentary Shot Cadence & Mathematical Allocation Utilities.

Pure calculation functions for sizing sub-shots within chapters.
"""
from __future__ import annotations
from typing import Any, Dict, List


def is_ai_diffusion_shot(shot: Dict[str, Any]) -> bool:
    """Check if a shot requires paid living AI video diffusion."""
    m_type = str(shot.get("motion_type", "")).lower().strip()
    rec = str(shot.get("recommended_model", "")).lower().strip()
    return m_type in ("ai_diffusion", "diffusion", "neural", "neural_diffusion") or rec in (
        "kling_v3_4k", "kling_v3", "kling_pro", "h3_max", "wan_2_1", "wan_4k", "minimax"
    )


def compute_chapter_shot_durations(
    shots: List[Dict[str, Any]],
    chapter_audio_duration: float,
    diffusion_clip_sec: float = 5.0,
    min_shot_sec: float = 3.0,
) -> List[float]:
    """Dynamically sizes sub-shots so their sum exactly equals the chapter audio duration."""
    n_shots = max(1, len(shots))
    if n_shots == 1:
        return [round(chapter_audio_duration, 2)]

    diff_indices = [i for i, s in enumerate(shots) if is_ai_diffusion_shot(s)]
    n_diff = len(diff_indices)
    n_ken = n_shots - n_diff

    if n_diff == 0:
        base_dur = round(chapter_audio_duration / n_shots, 2)
        durs = [base_dur] * n_shots
        durs[-1] = round(chapter_audio_duration - sum(durs[:-1]), 2)
        return durs

    if n_ken == 0:
        base_dur = round(chapter_audio_duration / n_diff, 2)
        durs = [base_dur] * n_diff
        durs[-1] = round(chapter_audio_duration - sum(durs[:-1]), 2)
        return durs

    total_diff_alloc = min(chapter_audio_duration - (n_ken * min_shot_sec), n_diff * diffusion_clip_sec)
    per_diff = round(total_diff_alloc / n_diff, 2) if n_diff > 0 else 0.0

    rem_for_ken = max(n_ken * min_shot_sec, chapter_audio_duration - (per_diff * n_diff))
    per_ken = round(rem_for_ken / n_ken, 2)

    durations: List[float] = []
    for i, s in enumerate(shots):
        durations.append(per_diff if i in diff_indices else per_ken)

    drift = round(chapter_audio_duration - sum(durations), 2)
    if abs(drift) > 0.001 and len(durations) > 0:
        ken_indices = [i for i in range(len(shots)) if i not in diff_indices]
        adj_idx = ken_indices[-1] if ken_indices else -1
        durations[adj_idx] = round(durations[adj_idx] + drift, 2)

    return durations


__all__ = ["is_ai_diffusion_shot", "compute_chapter_shot_durations"]
