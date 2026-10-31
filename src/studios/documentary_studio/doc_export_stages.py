"""Downstream Motion and 4K Master broadcast assembly stages for documentary format."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.services.visual_batch_service import MotionClipTask, visual_batch_service
from src.studios.documentary_studio.doc_audio_mixer import (
    build_active_chapters_voice_track,
    generate_documentary_subtitles,
    mix_documentary_audio,
)
from src.studios.documentary_studio.doc_directorial_motion_service import translate_doc_drone_configs
from src.studios.documentary_studio.doc_export_service import assemble_documentary_4k_master
from src.studios.documentary_studio.doc_stage_helpers import (
    load_screenplay_or_raise,
    select_shots_within_user_duration,
    update_doc_pipeline_state,
)


async def run_doc_motion_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 6: Render camera motion clips for each shot using Kling / Wan 2.1."""
    sp_data = load_screenplay_or_raise(ep_dir)
    shots = select_shots_within_user_duration(sp_data, ep_dir, req)
    target_idx = getattr(req, "target_shot_index", None)
    force_rerun = bool(getattr(req, "force_rerun", False))

    clip_tasks = []
    for s, ch, shot in shots:
        if target_idx is not None and int(target_idx) != s:
            continue
        kf_img = ep_dir / f"keyframe_p{s}.jpg"
        out_mp4 = ep_dir / f"motion_p{s}.mp4"
        d_cfg = translate_doc_drone_configs(shot.get("camera_motion", "slow_forward_glide"), shot.get("visual_prompt", ""))
        clip_tasks.append(
            MotionClipTask(
                prompt=f"{d_cfg['prompt']}, 4k resolution, smooth film cadence",
                image_url=str(kf_img),
                output_path=out_mp4,
                duration_seconds=float(shot.get("duration_seconds") or 6.0),
                index=s,
            )
        )
    if clip_tasks:
        await visual_batch_service.render_motion_clips_batch(
            tasks=clip_tasks,
            model_tier="balanced",
            motion_model=getattr(req, "motion_model", None) or "auto",
            force_rerun=force_rerun or (target_idx is not None),
        )
    update_doc_pipeline_state(ep_dir, 6, "motion")
    return {"current_stage": 6, "screenplay": sp_data, "script": sp_data}


async def run_doc_master_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 7: Assemble Single-Pass Broadcast 4K Master MP4 with voice, BGM, and subtitles."""
    sp_data = load_screenplay_or_raise(ep_dir)
    shots = select_shots_within_user_duration(sp_data, ep_dir, req)
    master_path = ep_dir / "master_4k_narration.mp4"
    audio_mix_path = ep_dir / "final_mixed_audio.wav"
    active_voice_path = ep_dir / "active_spoken_narration.mp3"
    subtitles_path = ep_dir / "subtitles.srt"

    build_active_chapters_voice_track(ep_dir, shots, active_voice_path)
    generate_documentary_subtitles(ep_dir, shots, subtitles_path)
    tot_dur = sum(float(s.get("duration_seconds") or 6.0) for _, _, s in shots)
    await mix_documentary_audio(
        voice_path=active_voice_path,
        bgm_path=ep_dir / "raw_soundtrack.mp3",
        output_path=audio_mix_path,
        total_duration=tot_dur,
    )
    clip_paths = [ep_dir / f"motion_p{s}.mp4" for s, _, _ in shots if (ep_dir / f"motion_p{s}.mp4").is_file()]
    await assemble_documentary_4k_master(
        clip_paths=clip_paths,
        audio_path=audio_mix_path,
        subtitles_path=subtitles_path if subtitles_path.is_file() else None,
        output_path=master_path,
        fps=24,
    )
    update_doc_pipeline_state(ep_dir, 7, "master")
    return {"current_stage": 7, "master_video_path": str(master_path), "screenplay": sp_data, "script": sp_data}

