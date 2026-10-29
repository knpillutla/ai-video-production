"""Screenplay Duration & Narration-First Cadence Calibration Service.

Calculates chapter and screenplay total durations deterministically
based on voiceover narration word count (~120 WPM / 2.0 words/sec) + visual padding,
guaranteeing raw Gemini screenplay JSON has the rough production video duration.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def calibrate_screenplay_durations(
    screenplay_data: Dict[str, Any],
    speech_words_per_sec: float = 2.0,
    fallback_dur_per_scene: float = 12.0,
    default_visual_padding: float = 3.0,
    is_auto_duration: bool = False,
) -> Tuple[Dict[str, Any], float]:
    """Calculates and embeds narration-derived durations into raw screenplay data.

    Returns:
        Tuple of (calibrated_screenplay_dict, total_calculated_duration_seconds)
    """
    data = dict(screenplay_data)
    chapters = data.get("chapters") or data.get("scenes") or []
    if not chapters:
        curr_total = float(data.get("total_duration_seconds") or 0.0)
        fallback_tot = fallback_dur_per_scene if curr_total <= 0 else curr_total
        data["total_duration_seconds"] = fallback_tot
        return data, fallback_tot

    eff_wps = max(0.5, speech_words_per_sec or 2.0)
    total_voice_seconds = 0.0
    total_chapter_seconds = 0.0
    total_words = 0

    for idx, ch in enumerate(chapters, 1):
        narr = (ch.get("narration_text") or ch.get("narration") or ch.get("audio_narration") or "").strip()
        words = narr.split()
        w_cnt = len(words)
        total_words += w_cnt

        est_speech_dur = round(w_cnt / eff_wps, 2) if w_cnt > 0 else 0.0
        vis_pad = float(ch.get("visual_padding_seconds") or default_visual_padding)
        current_dur = float(ch.get("duration_seconds", 0.0) or 0.0)

        # In auto mode, or if duration is missing/smaller than needed speech + padding
        needed_dur = round(est_speech_dur + vis_pad, 2) if est_speech_dur > 0 else fallback_dur_per_scene
        if is_auto_duration or current_dur <= 0 or (est_speech_dur > 0 and current_dur < needed_dur):
            final_ch_dur = needed_dur
        else:
            final_ch_dur = round(current_dur, 2)

        ch["estimated_narration_seconds"] = est_speech_dur
        ch["visual_padding_seconds"] = vis_pad
        ch["duration_seconds"] = final_ch_dur

        total_voice_seconds += est_speech_dur
        total_chapter_seconds += final_ch_dur

    tot_calc_dur = round(total_chapter_seconds, 2)
    tot_calc_voice = round(total_voice_seconds, 2)

    data["total_duration_seconds"] = tot_calc_dur
    data["estimated_narration_duration_seconds"] = tot_calc_voice
    data["total_words_count"] = total_words

    return data, tot_calc_dur


__all__ = ["calibrate_screenplay_durations"]
