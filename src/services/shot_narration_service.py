"""Shot-Aligned Narration & Audio Cadence Service.

Synchronizes per-shot voiceover stems, enforces anti-fatigue pauses,
and dynamically extends shot and video duration when narration exceeds planned length.
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import imageio_ffmpeg
from src.core.step_logger import log_pipeline_step
from src.providers.tts.azure_speech import AzureSpeechTTSAdapter
from src.services.ambient_export_service import get_media_duration

logger = logging.getLogger("video_studio")


async def synthesize_shot_aligned_narration(
    scenes: List[Any],
    ep_dir: Path,
    fallback_script: Optional[str] = None,
    total_target_sec: Optional[float] = None,
    voice_id: str = "en-US-JennyNeural",
    lead_in_sec: float = 0.8,
    min_tail_pause_sec: float = 2.0,
    force_rerun: bool = False,
) -> Dict[str, Any]:
    """Synthesize shot-aligned voiceover with anti-fatigue pauses and dynamic duration extension.
    
    Returns:
        dict containing:
            - narration_path: Path to master spoken_narration.mp3
            - shot_durations: List[float] duration per shot matching visual timeline
            - total_duration: float total master duration
    """
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    out_master = ep_dir / "spoken_narration.mp3"
    tts_adapter = AzureSpeechTTSAdapter()

    # Collect texts per scene
    scene_texts: List[str] = []
    planned_durs: List[float] = []

    for sc in scenes:
        txt = (getattr(sc, "narration_text", None) or "").strip()
        dur = float(getattr(sc, "duration_seconds", 0.0) or 20.0)
        scene_texts.append(txt)
        planned_durs.append(dur)

    # Fallback to paragraph splitting if scene narration_text is missing
    has_scene_texts = any(bool(t) for t in scene_texts)
    if not has_scene_texts and fallback_script:
        paras = [p.strip() for p in fallback_script.split("\n\n") if p.strip()]
        if len(paras) == len(scenes):
            scene_texts = paras
        elif len(paras) > 0:
            # Distribute paragraphs across scenes
            scene_texts = paras[:len(scenes)]
            while len(scene_texts) < len(scenes):
                scene_texts.append("")

    # If still completely empty, fallback to single unified script
    if not any(bool(t) for t in scene_texts):
        raw_text = fallback_script or ""
        if not raw_text:
            return {"narration_path": None, "shot_durations": planned_durs, "total_duration": sum(planned_durs)}
        if not out_master.is_file() or force_rerun:
            await tts_adapter.synthesize_to_file(raw_text, output_path=out_master, voice_id=voice_id)
        raw_dur = get_media_duration(out_master) or 0.0
        eff_total = max(float(total_target_sec or sum(planned_durs)), raw_dur + lead_in_sec + min_tail_pause_sec)
        n = max(1, len(scenes))
        return {
            "narration_path": out_master,
            "shot_durations": [round(eff_total / n, 2)] * n,
            "total_duration": round(eff_total, 2),
        }

    effective_shot_durs: List[float] = []
    padded_part_paths: List[Path] = []
    stem_dir = ep_dir / "narration_stems"
    stem_dir.mkdir(parents=True, exist_ok=True)

    for idx, (text, p_dur) in enumerate(zip(scene_texts, planned_durs)):
        part_raw = stem_dir / f"shot_{idx + 1}_raw.mp3"
        part_padded = stem_dir / f"shot_{idx + 1}_padded.mp3"

        log_pipeline_step("checking audio", f"Shot {idx + 1} Narration Stem", "started", metadata={"file": part_padded.name})
        if not force_rerun and part_padded.is_file() and part_padded.stat().st_size > 1000:
            padded_dur = get_media_duration(part_padded) or p_dur
            effective_shot_durs.append(round(padded_dur, 2))
            padded_part_paths.append(part_padded)
            log_pipeline_step("checking audio", f"Shot {idx + 1} Narration Stem", "completed", "narration stem exists, TTS not recreated", {"file": part_padded.name, "duration": round(padded_dur, 2), "cost": "$0.00"})
            continue

        if text:
            if not part_raw.is_file() or force_rerun:
                await tts_adapter.synthesize_to_file(text, output_path=part_raw, voice_id=voice_id)
            speech_dur = get_media_duration(part_raw) or 0.0
        else:
            speech_dur = 0.0

        # Anti-fatigue rule: shot must be at least speech_dur + lead_in + min_tail_pause
        needed_shot_dur = speech_dur + lead_in_sec + min_tail_pause_sec if speech_dur > 0 else p_dur
        final_shot_dur = max(p_dur, needed_shot_dur)
        effective_shot_durs.append(round(final_shot_dur, 2))

        # Pad audio with lead-in delay and trailing silence
        delay_ms = int(lead_in_sec * 1000)
        if speech_dur > 0:
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-i", str(part_raw),
                "-af", f"adelay={delay_ms}|{delay_ms},apad=whole_dur={final_shot_dur:.2f}",
                "-t", f"{final_shot_dur:.2f}",
                "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
                str(part_padded),
            ]
        else:
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-t", f"{final_shot_dur:.2f}",
                "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
                str(part_padded),
            ]
        subprocess.run(cmd, check=True)
        padded_part_paths.append(part_padded)
        log_pipeline_step("checking audio", f"Shot {idx + 1} Narration Stem", "completed", "narration stem synthesized", {"file": part_padded.name, "duration": final_shot_dur})

    # Concat all padded shots into master spoken_narration.mp3
    log_pipeline_step("checking audio", "Master Narration Concat", "started", metadata={"shots": len(padded_part_paths)})
    total_master_dur = sum(effective_shot_durs)
    if not force_rerun and out_master.is_file() and out_master.stat().st_size > 1000:
        log_pipeline_step("checking audio", "Master Narration Concat", "completed", "master narration exists, concat not recreated", {"file": out_master.name, "cost": "$0.00"})
    else:
        concat_list = ep_dir / "narration_concat.txt"
        concat_list.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in padded_part_paths), encoding="utf-8")
        cmd_concat = [
            ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c", "copy",
            str(out_master),
        ]
        subprocess.run(cmd_concat, check=True)
        log_pipeline_step("checking audio", "Master Narration Concat", "completed", "concatenated spoken_narration.mp3 from padded stems", {"file": out_master.name, "total_duration": round(total_master_dur, 2), "cost": "$0.00"})

    logger.info(
        f"shot_aligned_narration_synthesized: episode_id='{ep_dir.name}' "
        f"shots={len(effective_shot_durs)} total_dur={total_master_dur:.2f}s "
        f"shot_durs={effective_shot_durs}"
    )

    return {
        "narration_path": out_master,
        "shot_durations": effective_shot_durs,
        "total_duration": round(total_master_dur, 2),
    }
