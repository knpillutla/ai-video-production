"""Shot-Aligned Narration & Audio Cadence Service.

Synchronizes per-shot voiceover stems, enforces anti-fatigue pauses,
and dynamically extends shot and video duration when narration exceeds planned length.
"""
from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import imageio_ffmpeg
from src.core.step_logger import log_pipeline_step
from src.providers.tts.tts_router import get_tts_adapter
from src.services.ambient_export_service import get_media_duration

logger = logging.getLogger("video_studio")


async def synthesize_shot_aligned_narration(
    scenes: List[Any],
    ep_dir: Path,
    fallback_script: Optional[str] = None,
    total_target_sec: Optional[float] = None,
    voice_id: Optional[str] = None,
    lead_in_sec: float = 0.8,
    min_tail_pause_sec: float = 2.8,
    speech_rate: str = "-16%",
    force_rerun: bool = False,
    is_documentary: bool = False,
    tts_model: Optional[str] = None,
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
    tts_adapter = get_tts_adapter(tts_model)
    eff_model = (tts_model or getattr(settings.voice, "default_tts_model", "gemini") or "gemini").lower()

    # Default voice selection tailored per engine
    if not voice_id:
        if "gemini" in eff_model:
            voice_id = getattr(settings.voice, "gemini_tts_voice", "Charon")
        elif "kokoro" in eff_model:
            voice_id = getattr(settings.voice, "kokoro_voice", "bm_george")
        else:
            # Check ep_dir path or user_inputs.json to detect documentary format if not passed explicitly
            if not is_documentary:
                p_str = str(ep_dir).lower()
                if "documentary" in p_str or "doc" in p_str:
                    is_documentary = True
                else:
                    ui_file = ep_dir / "user_inputs.json"
                    if ui_file.is_file():
                        try:
                            u_d = json.loads(ui_file.read_text("utf-8"))
                            fmt = str(u_d.get("format", "")).lower()
                            gnr = str(u_d.get("genre", "")).lower()
                            if "documentary" in fmt or "documentary" in gnr or "doc" in fmt or "doc" in gnr:
                                is_documentary = True
                        except Exception:
                            pass
            voice_id = "en-GB-RyanNeural" if is_documentary else "en-US-JennyNeural"

    # Collect texts per scene
    scene_texts: List[str] = []
    planned_durs: List[float] = []

    for sc in scenes:
        txt = (getattr(sc, "narration_text", None) or "").strip()
        dur = float(getattr(sc, "duration_seconds", 0.0) or 20.0)
        scene_texts.append(txt)
        planned_durs.append(dur)

    # Fallback to paragraph or sentence splitting if scene narration_text is missing
    has_scene_texts = any(bool(t) for t in scene_texts)
    if not has_scene_texts and fallback_script:
        paras = [p.strip() for p in fallback_script.split("\n\n") if p.strip()]
        if len(paras) == len(scenes):
            scene_texts = paras
        else:
            sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', fallback_script) if s.strip()]
            if len(sents) == len(scenes):
                scene_texts = sents
            elif len(sents) > 0:
                scene_texts = [""] * len(scenes)
                for idx_s, sent in enumerate(sents):
                    target_idx = min(idx_s * len(scenes) // len(sents), len(scenes) - 1)
                    scene_texts[target_idx] = f"{scene_texts[target_idx]} {sent}".strip()
            elif len(paras) > 0:
                scene_texts = paras[:len(scenes)]
                while len(scene_texts) < len(scenes):
                    scene_texts.append("")
        for sc, txt in zip(scenes, scene_texts):
            if not getattr(sc, "narration_text", None):
                sc.narration_text = txt

    # If still completely empty, fallback to single unified script
    if not any(bool(t) for t in scene_texts):
        raw_text = fallback_script or ""
        if not raw_text:
            return {"narration_path": None, "shot_durations": planned_durs, "total_duration": sum(planned_durs)}
        if not out_master.is_file() or force_rerun:
            await tts_adapter.synthesize_to_file(raw_text, output_path=out_master, voice_id=voice_id, speech_rate=speech_rate)
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

    # Invalidate cached voice stems if speech_rate, lead_in_sec, or min_tail_pause_sec changed
    meta_path = stem_dir / "cadence_meta.json"
    cached_meta = {}
    if meta_path.is_file():
        try:
            cached_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            cached_meta = {}

    current_meta = {
        "speech_rate": speech_rate,
        "lead_in_sec": lead_in_sec,
        "min_tail_pause_sec": min_tail_pause_sec,
        "voice_id": voice_id,
    }
    if cached_meta != current_meta:
        logger.info(f"narration_cadence_changed: old={cached_meta} new={current_meta}. Invalidating stems.")
        for f in stem_dir.glob("*.mp3"):
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass
        if out_master.is_file():
            try:
                out_master.unlink(missing_ok=True)
            except Exception:
                pass
        meta_path.write_text(json.dumps(current_meta, indent=2), encoding="utf-8")

    for idx, (text, p_dur) in enumerate(zip(scene_texts, planned_durs)):
        part_raw = stem_dir / f"shot_{idx + 1}_raw.mp3"
        part_padded = stem_dir / f"shot_{idx + 1}_padded.mp3"

        log_pipeline_step("checking audio", f"Shot {idx + 1} Narration Stem", "started", metadata={"file": part_padded.name})
        if text:
            if not part_raw.is_file() or force_rerun:
                await tts_adapter.synthesize_to_file(text, output_path=part_raw, voice_id=voice_id, speech_rate=speech_rate)
                import asyncio
                await asyncio.sleep(0.3)
            speech_dur = get_media_duration(part_raw) or 0.0
        else:
            speech_dur = 0.0

        # Anti-fatigue rule: shot must be at least speech_dur + lead_in + min_tail_pause
        needed_shot_dur = speech_dur + lead_in_sec + min_tail_pause_sec if speech_dur > 0 else p_dur
        final_shot_dur = max(p_dur, needed_shot_dur)

        # Check existing padded stem: MUST have valid duration >= needed_shot_dur and newer than raw stem
        if not force_rerun and part_padded.is_file() and part_padded.stat().st_size > 1000:
            padded_dur = get_media_duration(part_padded) or 0.0
            if padded_dur >= (speech_dur + lead_in_sec + 0.1):
                effective_shot_durs.append(round(padded_dur, 2))
                padded_part_paths.append(part_padded)
                log_pipeline_step("checking audio", f"Shot {idx + 1} Narration Stem", "completed", "narration stem exists, TTS not recreated", {"file": part_padded.name, "duration": round(padded_dur, 2), "cost": "$0.00"})
                continue

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
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.run(cmd, check=True, creationflags=flags)
        padded_part_paths.append(part_padded)
        effective_shot_durs.append(round(final_shot_dur, 2))
        log_pipeline_step("checking audio", f"Shot {idx + 1} Narration Stem", "completed", "narration stem synthesized", {"file": part_padded.name, "duration": final_shot_dur})

    # Concat all padded shots into master spoken_narration.mp3
    log_pipeline_step("checking audio", "Master Narration Concat", "started", metadata={"shots": len(padded_part_paths)})
    total_master_dur = sum(effective_shot_durs)
    cur_m_dur = get_media_duration(out_master) if out_master.is_file() else 0.0
    if not force_rerun and out_master.is_file() and out_master.stat().st_size > 1000 and abs(cur_m_dur - total_master_dur) <= 1.0:
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
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.run(cmd_concat, check=True, creationflags=flags)
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
