"""Documentary Chapter & Audio-First Shot Cadence Service.

Manages hierarchical screenplay chapters (chapters[] -> shots[]),
flattens them into broadcast timeline scenes, and dynamically sizes sub-shots
to mathematically match the narration audio duration (audio is the master clock).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.telemetry import logger
from src.studios.documentary_studio.doc_templates import DocScene


from src.studios.documentary_studio.doc_shot_cadence_calc import (
    compute_chapter_shot_durations,
    is_ai_diffusion_shot,
)


def flatten_chapters_to_timeline(
    raw_data: Dict[str, Any],
    fallback_dur_per_scene: float = 12.0,
) -> Tuple[List[Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    """Unpacks hierarchical chapters[] -> shots[] into flat timeline scenes.
    
    Returns:
        Tuple of (flattened_shots, chapter_heads_map)
        chapter_heads_map maps timeline_index -> chapter metadata for dossier cards.
    """
    raw_chapters = raw_data.get("chapters")
    raw_scenes = raw_data.get("scenes") or []

    # If already flat scenes without sub-shots, return as-is
    has_sub_shots = any(bool(sc.get("shots")) for sc in (raw_chapters or raw_scenes))
    if not raw_chapters and not has_sub_shots:
        flat_scenes: List[Dict[str, Any]] = []
        ch_map: Dict[int, Dict[str, Any]] = {}
        for idx, sc in enumerate(raw_scenes):
            sc_copy = dict(sc)
            sc_copy["timeline_index"] = idx + 1
            sc_copy["is_chapter_head"] = True
            flat_scenes.append(sc_copy)
            ch_map[idx] = {
                "chapter_title": sc.get("chapter_title"),
                "chapter_subtitle": sc.get("chapter_subtitle"),
                "fact_badge": sc.get("fact_badge"),
                "chapter_stats": sc.get("chapter_stats"),
            }
        return flat_scenes, ch_map

    containers = raw_chapters if raw_chapters else raw_scenes
    flattened: List[Dict[str, Any]] = []
    chapter_map: Dict[int, Dict[str, Any]] = {}
    curr_shot_idx = 0

    for ch_idx, ch in enumerate(containers, 1):
        ch_title = ch.get("chapter_title") or ch.get("title") or f"CHAPTER {ch_idx:02d}"
        ch_subtitle = ch.get("chapter_subtitle") or ch.get("subtitle")
        ch_badge = ch.get("fact_badge") or ch.get("badge")
        ch_stats = ch.get("chapter_stats") or ch.get("stats")
        ch_narr = ch.get("narration_text") or ch.get("narration") or ""
        sub_shots = ch.get("shots") or []

        if not sub_shots:
            # Chapter is its own single shot
            shot_copy = dict(ch)
            shot_copy["timeline_index"] = curr_shot_idx + 1
            shot_copy["chapter_index"] = ch_idx
            shot_copy["is_chapter_head"] = True
            shot_copy["narration_text"] = ch_narr
            shot_copy["chapter_title"] = ch_title
            shot_copy["chapter_subtitle"] = ch_subtitle
            shot_copy["fact_badge"] = ch_badge
            shot_copy["chapter_stats"] = ch_stats
            chapter_map[curr_shot_idx] = {
                "chapter_title": ch_title, "chapter_subtitle": ch_subtitle,
                "fact_badge": ch_badge, "chapter_stats": ch_stats,
            }
            flattened.append(shot_copy)
            curr_shot_idx += 1
            continue

        # Multiple sub-shots in this chapter
        planned_dur = float(ch.get("duration_seconds", fallback_dur_per_scene) or fallback_dur_per_scene)
        initial_durs = compute_chapter_shot_durations(sub_shots, planned_dur)

        for s_idx, (s_dict, s_dur) in enumerate(zip(sub_shots, initial_durs), 1):
            shot_copy = dict(s_dict)
            shot_copy["timeline_index"] = curr_shot_idx + 1
            shot_copy["chapter_index"] = ch_idx
            shot_copy["sub_shot_index"] = s_idx
            shot_copy["duration_seconds"] = s_dur
            if not shot_copy.get("image_model_configs"):
                from src.studios.directorial_configs import build_default_image_model_configs
                vp = shot_copy.get("visual_prompt") or ""
                shot_copy["image_model_configs"] = ch.get("image_model_configs") or (build_default_image_model_configs(vp, ch_title or "Scene") if vp else {})

            # Only head shot gets the dossier badge & metadata
            if s_idx == 1:
                shot_copy["is_chapter_head"] = True
                shot_copy["chapter_title"] = ch_title
                shot_copy["chapter_subtitle"] = ch_subtitle
                shot_copy["fact_badge"] = ch_badge
                shot_copy["chapter_stats"] = ch_stats
                shot_copy["narration_text"] = ch_narr
                chapter_map[curr_shot_idx] = {
                    "chapter_title": ch_title, "chapter_subtitle": ch_subtitle,
                    "fact_badge": ch_badge, "chapter_stats": ch_stats,
                }
            else:
                shot_copy["is_chapter_head"] = False
                shot_copy["chapter_title"] = None
                shot_copy["chapter_subtitle"] = None
                shot_copy["fact_badge"] = None
                shot_copy["chapter_stats"] = None
                # Visual continuation during continuous VO
                shot_copy["narration_text"] = ""

            flattened.append(shot_copy)
            curr_shot_idx += 1

    return flattened, chapter_map


async def synthesize_chapter_aligned_narration(
    scenes: List[Any],
    ep_dir: Path,
    voice_id: str,
    speech_rate: str = "-16%",
    lead_in_sec: float = 0.8,
    min_tail_pause_sec: float = 2.5,
    force_rerun: bool = False,
    tts_model: Optional[str] = None,
    execution_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Synthesizes voiceover per chapter and deterministically sizes sub-shots to match audio."""
    import subprocess
    import sys
    import imageio_ffmpeg
    from src.core.step_logger import log_pipeline_step
    from src.providers.tts.tts_router import get_tts_adapter
    from src.services.ambient_export_service import get_media_duration

    # Resolve execution mode from user_inputs.json if not passed
    if not execution_mode:
        ui_path = ep_dir / "user_inputs.json"
        if ui_path.is_file():
            try:
                execution_mode = json.loads(ui_path.read_text("utf-8")).get("execution_mode", "prod")
            except Exception:
                execution_mode = "prod"
        else:
            execution_mode = "prod"

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    out_master = ep_dir / "spoken_narration.mp3"
    tts_adapter = get_tts_adapter(tts_model)
    stem_dir = ep_dir / "narration_stems"
    stem_dir.mkdir(parents=True, exist_ok=True)

    # Group scenes into chapters
    chapters_dict: Dict[int, List[Any]] = {}
    for idx, sc in enumerate(scenes):
        ch_idx = getattr(sc, "chapter_index", None) or (sc.get("chapter_index") if isinstance(sc, dict) else None) or (idx + 1)
        chapters_dict.setdefault(ch_idx, []).append(sc)

    chapter_durations: Dict[int, float] = {}
    effective_shot_durs: List[float] = []
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    import asyncio
    sem = asyncio.Semaphore(4)

    async def _synthesize_one_chapter(ch_idx: int, ch_scenes: List[Any]) -> Tuple[int, float, Path]:
        ch_head = ch_scenes[0]
        text = (
            getattr(ch_head, "narration_text", None)
            or getattr(ch_head, "narration", None)
            or (ch_head.get("narration_text") if isinstance(ch_head, dict) else None)
            or (ch_head.get("narration") if isinstance(ch_head, dict) else None)
            or ""
        ).strip()
        part_raw = stem_dir / f"chapter_{ch_idx}_raw.mp3"
        part_padded = stem_dir / f"chapter_{ch_idx}_padded.mp3"

        async with sem:
            log_pipeline_step("checking audio", f"Chapter {ch_idx} Narration Stem", "started", metadata={"file": part_padded.name})
            if text:
                if not part_raw.is_file() or force_rerun:
                    await tts_adapter.synthesize_to_file(text, output_path=part_raw, voice_id=voice_id, speech_rate=speech_rate)
                speech_dur = get_media_duration(part_raw) or 0.0
            else:
                speech_dur = 0.0

            planned_ch_dur = sum(
                float(
                    getattr(s, "duration_seconds", None)
                    or (s.get("duration_seconds") if isinstance(s, dict) else None)
                    or 10.0
                )
                for s in ch_scenes
            )
            needed_ch_dur = speech_dur + lead_in_sec + min_tail_pause_sec if speech_dur > 0 else planned_ch_dur
            final_ch_dur = round(needed_ch_dur, 2) if speech_dur > 0 else planned_ch_dur
            delay_ms = int(lead_in_sec * 1000)

            if not part_padded.is_file() or part_padded.stat().st_size < 1000 or force_rerun or abs((get_media_duration(part_padded) or 0.0) - final_ch_dur) > 2.0:
                if speech_dur > 0:
                    cmd = [
                        ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                        "-i", str(part_raw),
                        "-af", f"adelay={delay_ms}|{delay_ms},apad=whole_dur={final_ch_dur:.2f}",
                        "-t", f"{final_ch_dur:.2f}",
                        "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
                        str(part_padded),
                    ]
                else:
                    cmd = [
                        ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                        "-t", f"{final_ch_dur:.2f}",
                        "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
                        str(part_padded),
                    ]
                await asyncio.to_thread(subprocess.run, cmd, check=True, creationflags=flags)

            log_pipeline_step(
                "checking audio",
                f"Chapter {ch_idx} Narration Stem",
                "completed",
                "narration synthesized",
                {"file": part_padded.name, "duration": final_ch_dur, "sub_shots": len(ch_scenes)},
            )
            return ch_idx, final_ch_dur, part_padded

    ordered_items = sorted(chapters_dict.items(), key=lambda kv: kv[0])
    if (ep_dir / "user_inputs.json").is_file():
        try:
            u_dur = float(json.loads((ep_dir / "user_inputs.json").read_text("utf-8")).get("duration_seconds") or -1)
            if u_dur > 0:
                kept, acc = [], 0.0
                for k, v in ordered_items:
                    est = sum(float(getattr(s, "duration_seconds", None) or (s.get("duration_seconds") if isinstance(s, dict) else None) or 12.0) for s in v)
                    if kept and (acc + est * 0.65) > u_dur:
                        break
                    kept.append((k, v))
                    acc += est
                if kept:
                    ordered_items = kept
        except Exception:
            pass
    results = await asyncio.gather(*(_synthesize_one_chapter(k, v) for k, v in ordered_items))
    padded_part_paths: List[Path] = []
    for ch_idx, final_ch_dur, part_padded in sorted(results, key=lambda r: r[0]):
        chapter_durations[ch_idx] = final_ch_dur
        padded_part_paths.append(part_padded)

    # Concat all padded chapter stems into master spoken_narration.mp3
    concat_list = ep_dir / "narration_concat.txt"
    concat_list.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in padded_part_paths), encoding="utf-8")
    if not out_master.is_file() or out_master.stat().st_size < 1000 or force_rerun:
        cmd_concat = [
            ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c", "copy",
            str(out_master),
        ]
        await asyncio.to_thread(subprocess.run, cmd_concat, check=True, creationflags=flags)

    for ch_idx, ch_scenes in ordered_items:
        shot_dicts = [s.__dict__ if hasattr(s, "__dict__") else (s if isinstance(s, dict) else {}) for s in ch_scenes]
        sized = compute_chapter_shot_durations(shot_dicts, chapter_durations[ch_idx])
        for sc, s_dur in zip(ch_scenes, sized):
            if isinstance(sc, dict):
                sc["duration_seconds"] = s_dur
            else:
                sc.duration_seconds = s_dur
            effective_shot_durs.append(s_dur)

    total_master_dur = sum(effective_shot_durs)
    logger.info(f"chapter_aligned_narration_synthesized: episode='{ep_dir.name}' chapters={len(chapters_dict)} total_dur={total_master_dur:.2f}s shots={len(effective_shot_durs)}")
    return {
        "narration_path": out_master,
        "shot_durations": effective_shot_durs,
        "total_duration": round(total_master_dur, 2),
    }


__all__ = [
    "is_ai_diffusion_shot",
    "compute_chapter_shot_durations",
    "flatten_chapters_to_timeline",
    "synthesize_chapter_aligned_narration",
]

