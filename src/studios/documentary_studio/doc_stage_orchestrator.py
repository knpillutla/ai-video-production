"""Dedicated Stage Orchestrator for Blue-Chip Educational Documentary Format."""
from __future__ import annotations
import asyncio, json, re, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.storage import sanitize_container_name, storage_service
from src.core.telemetry import logger
from src.services.ambient_export_service import get_media_duration
from src.services.job_manager import job_manager
from src.services.soundtrack_service import soundtrack_service
from src.services.visual_batch_service import MotionClipTask, visual_batch_service
from src.studios.documentary_studio.doc_artifact_scanner import scan_documentary_artifacts
from src.studios.documentary_studio.doc_audio_mixer import build_active_chapters_voice_track, generate_documentary_subtitles, mix_documentary_audio
from src.studios.documentary_studio.doc_directorial_motion_service import execute_pass2_directorial_motion, translate_doc_drone_configs
from src.studios.documentary_studio.doc_export_service import assemble_documentary_4k_master
from src.studios.documentary_studio.doc_overlay_service import build_shot_documentary_hud
from src.studios.documentary_studio.doc_story_service import build_raw_documentary_story, persist_raw_documentary_story
from src.studios.documentary_studio.doc_voice_service import produce_documentary_narration_stage


def resolve_doc_episode_dir(user_id: str, channel_id: str, episode_id: str, production_name: Optional[str] = None, req: Any = None) -> Path:
    """Locate existing documentary episode directory or create one under the destination slug."""
    ep_dir = storage_service.find_episode_path(user_id=user_id, channel_id=channel_id, episode_id=episode_id, format_slug="documentary", production_name=production_name)
    if ep_dir and ep_dir.exists() and any((ep_dir / f).is_file() for f in ("raw_gemini_story.json", "raw_gemini_screenplay.json", "spoken_narration.mp3")): return ep_dir
    c_name = sanitize_container_name(user_id) if "@" in user_id else user_id
    dest = (production_name or getattr(req, "country", None) or "").strip()
    if not dest or dest.lower() in ("standalone", "destination") or re.match(r"^ep[-_]?\d+$", dest.lower()):
        from src.studios.documentary_studio.doc_geo_rotation import resolve_autonomous_geo_details
        _, _, _, picked = resolve_autonomous_geo_details(
            sub_genre=getattr(req, "sub_genre", None) or "europe_nations", archetype=getattr(req, "primary_archetype", None) or "countries",
            user_id=user_id, channel_id=channel_id, custom_prompt=getattr(req, "prompt", None) or dest,
        )
        dest = picked or "Norway"
    dest_slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", dest.lower()).strip("_") or "destination"
    base = storage_service.root_dir / c_name / "networks" / channel_id / "documentary" / dest_slug / episode_id.lower()
    base.mkdir(parents=True, exist_ok=True)
    return base


def _update_doc_pipeline_state(ep_dir: Path, stage_num: int, stage_key: str, status_val: str = "ready") -> None:
    """Persist documentary pipeline_state.json stage completion."""
    state_file = ep_dir / "pipeline_state.json"
    try: state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.is_file() else {}
    except Exception: state = {}
    state["current_stage"], state["stage_status"] = max(int(state.get("current_stage") or 1), stage_num), status_val
    completed, approvals = state.setdefault("stages_completed", {}), state.setdefault("stage_approvals", {})
    completed[stage_key] = approvals[stage_key] = True
    for k, alias in (("screenplay", "script"), ("keyframes", "photos"), ("bgm", "audio")):
        if stage_key == k: completed[alias] = True
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_screenplay_or_raise(ep_dir: Path) -> Dict[str, Any]:
    sp_file = ep_dir / "raw_gemini_screenplay.json"
    if not sp_file.is_file():
        raise RuntimeError(f"Documentary screenplay raw_gemini_screenplay.json not found in {ep_dir.name}. Run Stage 3 (screenplay) first.")
    return json.loads(sp_file.read_text(encoding="utf-8"))


def _select_shots_within_user_duration(sp_data: Dict[str, Any], ep_dir: Path, req: Any = None) -> List[Tuple[int, Dict[str, Any], Dict[str, Any]]]:
    """Read (seq_num, chapter, shot) tuples from chapters[].shots whose combined duration_seconds is <= user_inputs.json duration_seconds (or all shots when -1/Auto)."""
    req_d = getattr(req, "duration_seconds", None)
    max_dur: Optional[float] = float(req_d) if (req_d is not None and float(req_d) > 0) else None
    ui_file = ep_dir / "user_inputs.json"
    if ui_file.is_file():
        try:
            ui = json.loads(ui_file.read_text(encoding="utf-8"))
            raw_d = ui.get("duration_seconds") if ui.get("duration_seconds") is not None else (ui.get("requested_duration_seconds") or ui.get("duration_secs"))
            if raw_d is not None: max_dur = float(raw_d) if float(raw_d) > 0 else None
        except Exception: pass
    selected: List[Tuple[int, Dict[str, Any], Dict[str, Any]]] = []
    elapsed, seq_num = 0.0, 1
    for ch in sp_data.get("chapters") or []:
        for shot in ch.get("shots") or []:
            dur = float(shot.get("duration_seconds") or 6.0)
            if max_dur and max_dur > 0 and selected and (elapsed + dur) > max_dur: return selected
            selected.append((seq_num, ch, shot)); elapsed += dur; seq_num += 1
    return selected


async def run_doc_story_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 1: Generate 21-chapter raw_gemini_story.json."""
    story_file = ep_dir / "raw_gemini_story.json"
    if not getattr(req, "force_rerun", False) and story_file.is_file() and story_file.stat().st_size > 200:
        story_dict = json.loads(story_file.read_text(encoding="utf-8"))
    else:
        from src.studios.documentary_studio.doc_geo_rotation import is_known_geo_entity, resolve_autonomous_geo_details
        dest = (getattr(req, "production_name", None) or getattr(req, "country", None) or "").strip()
        eff_sub = getattr(req, "sub_genre", None) or "europe_nations"
        eff_arch = getattr(req, "primary_archetype", None) or "countries"
        eff_ch = getattr(req, "channel_id", None) or "euro_discovery"
        if not dest or dest.lower() == "standalone" or re.match(r"^ep[-_]?\d+$", dest.lower()) or not is_known_geo_entity(dest):
            _, _, _, picked = resolve_autonomous_geo_details(
                sub_genre=eff_sub, archetype=eff_arch, user_id=getattr(req, "user_id", None) or "user_krishna_01",
                channel_id=eff_ch, custom_prompt=getattr(req, "prompt", None) or dest,
            )
            dest = picked or "Norway"
        story_dict = await asyncio.to_thread(
            build_raw_documentary_story, destination=dest, genre=getattr(req, "genre", None) or "doc/nations",
            sub_genre=eff_sub, archetype=eff_arch, custom_prompt=getattr(req, "prompt", None) or "", channel_id=eff_ch,
        )
        persist_raw_documentary_story(ep_dir, story_dict)
    _update_doc_pipeline_state(ep_dir, 1, "story")
    return {"current_stage": 1, "story": story_dict}


async def run_doc_narration_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 2: Synthesize per-chapter narration stems and spoken_narration.mp3."""
    narr_res = await produce_documentary_narration_stage(
        ep_dir=ep_dir, voice_id="en-GB-RyanNeural", tts_model=getattr(req, "tts_model", None) or "azure_speech",
        force_rerun=bool(getattr(req, "force_rerun", False)), execution_mode=getattr(req, "execution_mode", None) or "test",
    )
    _update_doc_pipeline_state(ep_dir, 2, "narration")
    return {"current_stage": 2, "duration_seconds": float(narr_res.get("total_duration", 60.0)), "story": narr_res.get("story")}


async def run_doc_screenplay_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 3: Formulate 3-shot directorial screenplay (raw_gemini_screenplay.json) from story + measured narration."""
    sp_file = ep_dir / "raw_gemini_screenplay.json"
    force_rerun = bool(getattr(req, "force_rerun", False))
    if not force_rerun and sp_file.is_file() and sp_file.stat().st_size > 200:
        sp_data = json.loads(sp_file.read_text(encoding="utf-8"))
        _update_doc_pipeline_state(ep_dir, 3, "screenplay")
        return {"current_stage": 3, "screenplay": sp_data, "script": sp_data}

    story_file = ep_dir / "raw_gemini_story.json"
    if not story_file.is_file():
        await run_doc_story_stage(ep_dir, req)
    story_data = json.loads(story_file.read_text(encoding="utf-8"))

    # Measure per-chapter audio durations from narration_stems
    stems_dir = ep_dir / "narration_stems"
    ch_durations: Dict[int, float] = {}
    chapters = story_data.get("chapters") or []
    for idx, ch in enumerate(chapters, 1):
        c_idx = int(ch.get("chapter_index") or idx)
        raw_stem = stems_dir / f"chapter_{c_idx}_raw.mp3"
        pad_stem = stems_dir / f"chapter_{c_idx}_padded.mp3"
        if raw_stem.is_file() and raw_stem.stat().st_size > 500:
            ch_durations[c_idx] = round(float(get_media_duration(raw_stem) or 15.0), 2)
        elif pad_stem.is_file() and pad_stem.stat().st_size > 500:
            ch_durations[c_idx] = max(6.0, round(float(get_media_duration(pad_stem) or 18.0) - 3.0, 2))
        else:
            ch_durations[c_idx] = float(ch.get("duration_seconds") or 18.0)

    exec_mode = getattr(req, "execution_mode", None) or "test"
    directed = await execute_pass2_directorial_motion(
        screenplay_data=story_data, chapter_durations=ch_durations, raw_output_path=sp_file, execution_mode=exec_mode, allow_fallback=True,
    )
    _update_doc_pipeline_state(ep_dir, 3, "screenplay")
    return {"current_stage": 3, "screenplay": directed, "script": directed}


async def run_doc_photos_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 4: Read documentary shots from chapters[].shots within user duration limit and render keyframes."""
    sp_data = _load_screenplay_or_raise(ep_dir)
    shots = _select_shots_within_user_duration(sp_data, ep_dir, req)
    target_idx = getattr(req, "target_shot_index", None)
    force_rerun = bool(getattr(req, "force_rerun", False))

    kf_tasks = []
    for s_idx, ch, shot in shots:
        if target_idx is not None and int(target_idx) != s_idx:
            continue
        vp = shot.get("visual_prompt") or shot.get("visual_description") or shot.get("description") or ch.get("visual_directive") or "Documentary vista"
        kf_tasks.append((vp, ep_dir / f"keyframe_p{s_idx}.jpg", ep_dir / f"fal_req_p{s_idx}.json", s_idx))

    if kf_tasks:
        exec_mode = str(getattr(req, "execution_mode", None) or "test").lower()
        await visual_batch_service.render_keyframes_batch(
            tasks=kf_tasks, aspect_ratio="16:9", force_rerun=force_rerun or (target_idx is not None),
            image_model=getattr(req, "image_model", None) or "zimage", enable_4k_upscale=(exec_mode == "prod"),
        )
    _update_doc_pipeline_state(ep_dir, 4, "keyframes")
    return {"current_stage": 4, "screenplay": sp_data, "script": sp_data}


async def run_doc_bgm_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 5: Synthesize background music stem via shared soundtrack_service."""
    sp_data = _load_screenplay_or_raise(ep_dir)
    shots = _select_shots_within_user_duration(sp_data, ep_dir, req)
    tot_dur = sum(float(s.get("duration_seconds") or 6.0) for _, _, s in shots) or float(sp_data.get("total_duration_seconds") or 120.0)
    title = sp_data.get("title") or f"Documentary {ep_dir.name}"
    await soundtrack_service.synthesize_ambient_soundtrack(
        title=title, tags="orchestral documentary score, atmospheric strings, cinematic ambient",
        out_path=ep_dir / "raw_soundtrack.mp3", total_duration=min(tot_dur, 240.0),
        genre="documentary orchestral", episode_id=ep_dir.name, force_rerun=bool(getattr(req, "force_rerun", False)),
    )
    _update_doc_pipeline_state(ep_dir, 5, "bgm")
    return {"current_stage": 5, "screenplay": sp_data, "script": sp_data}


async def run_doc_motion_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 6: Read documentary shots from chapters[].shots within user duration limit and render motion clips."""
    sp_data = _load_screenplay_or_raise(ep_dir)
    shots = _select_shots_within_user_duration(sp_data, ep_dir, req)
    target_idx = getattr(req, "target_shot_index", None)
    force_rerun = bool(getattr(req, "force_rerun", False))
    req_model = getattr(req, "motion_model", None) or "auto"

    motion_tasks: List[MotionClipTask] = []
    for s_idx, ch, shot in shots:
        if target_idx is not None and int(target_idx) != s_idx:
            continue
        kf_path, out_clip = ep_dir / f"keyframe_p{s_idx}.jpg", ep_dir / f"motion_p{s_idx}.mp4"
        shot_rec = shot.get("recommended_model") or ("local_drone" if shot.get("motion_type") == "ken_burns" else "h3_max")
        sc_model = req_model if (target_idx is not None and req_model not in ("auto", "")) else shot_rec
        raw_cfgs = shot.get("model_configs") if isinstance(shot.get("model_configs"), dict) else {}
        m_cfgs, cam_mov = translate_doc_drone_configs(raw_cfgs)
        vp = shot.get("visual_prompt") or shot.get("visual_description") or shot.get("description") or ch.get("visual_directive") or ""
        mp = shot.get("motion_prompt") or (m_cfgs.get("ai_diffusion") or {}).get("motion_prompt") or vp
        hud = build_shot_documentary_hud(sp_data, ch, shot)
        base_dur = float(shot.get("duration_seconds") or 6.0)
        eff_dur = round(base_dur + (0.5 if sc_model == "local_drone" else 0.0), 2)
        motion_tasks.append(
            MotionClipTask(
                image_path=kf_path, motion_prompt=mp, visual_prompt=vp, output_path=out_clip,
                duration_seconds=eff_dur, model=sc_model,
                req_file=ep_dir / f"fal_diff_req_p{s_idx}.json", allow_fallback=True,
                force_rerun=force_rerun or (target_idx is not None), model_configs=m_cfgs,
                camera_movement=cam_mov, is_relaxation=False, lower_third_hud=hud,
            )
        )
    if motion_tasks:
        await visual_batch_service.render_motion_batch(motion_tasks)
    _update_doc_pipeline_state(ep_dir, 6, "motion")
    return {"current_stage": 6, "screenplay": sp_data, "script": sp_data}


async def run_doc_master_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 7: Mix narration + BGM and assemble 4K documentary master MP4 from rendered shots."""
    sp_data = _load_screenplay_or_raise(ep_dir)
    shots = _select_shots_within_user_duration(sp_data, ep_dir, req)
    clips = [ep_dir / f"motion_p{s_idx}.mp4" for s_idx, _, _ in shots]
    clips = [c for c in clips if c.is_file() and c.stat().st_size > 1000]
    if not clips:
        raise RuntimeError("Cannot assemble 4K master: no rendered motion_p*.mp4 clips found.")
    ch_indices = [int(ch.get("chapter_index") or 1) for _, ch, _ in shots[:len(clips)]]
    ch_durs: Dict[int, float] = {}
    for (_, ch, _), c_path in zip(shots[:len(clips)], clips):
        cid = int(ch.get("chapter_index") or 1)
        ch_durs[cid] = round(ch_durs.get(cid, 0.0) + max(1.0, float(get_media_duration(c_path) or 6.0) - 0.5), 2)
    voice_path = await asyncio.to_thread(build_active_chapters_voice_track, ep_dir, ch_indices, ch_durs)
    bgm_path = ep_dir / "raw_soundtrack.mp3" if (ep_dir / "raw_soundtrack.mp3").is_file() else None
    mixed_audio, srt_path, master_path = ep_dir / "master_audio_48k.aac", ep_dir / "subtitles.srt", ep_dir / "master_4k_documentary.mp4"
    await asyncio.to_thread(mix_documentary_audio, voice_path, bgm_path, mixed_audio, -14.0, None, None, True)
    await asyncio.to_thread(
        generate_documentary_subtitles,
        [str((ch.get("narration_text") or ch.get("narration") or "") if shot.get("shot_index") == 1 else "") for _, ch, shot in shots[:len(clips)]],
        [float(shot.get("duration_seconds") or 6.0) for _, _, shot in shots[:len(clips)]],
        srt_path,
    )
    await asyncio.to_thread(assemble_documentary_4k_master, clips, mixed_audio, master_path, srt_path)
    _update_doc_pipeline_state(ep_dir, 7, "master")
    return {"current_stage": 7, "master_video_path": str(master_path), "screenplay": sp_data, "script": sp_data}


async def dispatch_documentary_stage(req: Any, stage_name: Optional[str] = None) -> Dict[str, Any]:
    """Route a documentary stage request to its dedicated stage handler and return standardized response."""
    t0 = time.time()
    user_id = req.user_id if (getattr(req, "user_id", None) and "@" in str(req.user_id)) else (getattr(req, "user_id", None) or "knpillutla@gmail.com")
    channel_id = getattr(req, "channel_id", None) or "euro_discovery"
    episode_id = getattr(req, "episode_id", None) or "ep-001"
    ep_dir = resolve_doc_episode_dir(user_id, channel_id, episode_id, getattr(req, "production_name", None), req)

    st = (stage_name or "").strip().lower()
    if not st:
        if getattr(req, "screenplay_only", False): st = "screenplay"
        elif getattr(req, "narration_only", False) or (getattr(req, "audio_only", False) and not getattr(req, "bgm_only", False) and "suno" not in str(getattr(req, "prompt", "") or "").lower()): st = "narration"
        elif getattr(req, "photos_only", False): st = "photos"
        elif getattr(req, "bgm_only", False) or getattr(req, "audio_only", False): st = "bgm"
        elif getattr(req, "motion_only", False): st = "motion"
        elif getattr(req, "master_only", False): st = "master"
        elif getattr(req, "script_only", False): st = "story"
        else: st = "screenplay"

    job_id = f"job_doc_{episode_id.lower()}_{st}_{int(time.time())}"
    job_manager.create_job(job_id=job_id, episode_id=episode_id, title=getattr(req, "title", None) or f"Documentary {episode_id}", channel_id=channel_id, user_id=user_id)
    handlers = {
        "story": run_doc_story_stage, "script": run_doc_story_stage, "narration": run_doc_narration_stage,
        "screenplay": run_doc_screenplay_stage, "photos": run_doc_photos_stage, "keyframes": run_doc_photos_stage,
        "bgm": run_doc_bgm_stage, "audio": run_doc_bgm_stage, "motion": run_doc_motion_stage, "master": run_doc_master_stage,
    }
    stage_res = await handlers.get(st, run_doc_screenplay_stage)(ep_dir, req)
    scanned = scan_documentary_artifacts(
        channel_id=channel_id, episode_id=episode_id, format_slug="documentary",
        production_name=getattr(req, "production_name", None), user_id=user_id,
    )
    eff_stage = int(stage_res.get("current_stage") or scanned.get("current_stage") or 3)
    job_manager.update_job(job_id=job_id, stage=eff_stage, progress=100, status="ready")

    return {
        "success": True, "job_id": job_id, "episode_id": episode_id,
        "title": scanned.get("title") or getattr(req, "title", None) or f"Documentary {episode_id}",
        "production_name": scanned.get("production_name") or getattr(req, "production_name", None),
        "current_stage": eff_stage, "stage": eff_stage,
        "duration_seconds": float(stage_res.get("duration_seconds") or (scanned.get("screenplay") or {}).get("active_duration_seconds") or 120.0),
        "render_time_seconds": round(time.time() - t0, 2), "master_video_url": scanned.get("master_url"),
        "keyframes": scanned.get("keyframes", []), "motion_clips": scanned.get("motion_clips", []),
        "audio_stems": scanned.get("audio_stems", []), "artifacts": scanned.get("artifacts", []),
        "story": stage_res.get("story") or scanned.get("story"),
        "screenplay": stage_res.get("screenplay") or scanned.get("screenplay"),
        "script": stage_res.get("script") or scanned.get("screenplay") or scanned.get("script"),
    }

