import os
import re
import shutil
import time
import json
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.services.network_production_service import produce_channel_video
from src.services.job_manager import job_manager
from src.core.storage import storage_service
from src.core.telemetry import logger
from src.domain.repo import repo
from src.mcp.topic_memory.server import check_topic_duplicate, remember_topic
from src.providers.fal_storage import _fal_api_key
from src.services.storage_cleanup_service import cleanup_empty_parent_production, robust_remove_directory

router = APIRouter(prefix="/api/production", tags=["Local Production Engine"])


class LocalProduceRequest(BaseModel):
    """Payload for local video synthesis and storage persistence."""
    prompt: str = Field(..., description="Prompt concept, theme, or script")
    title: Optional[str] = None
    episode_id: Optional[str] = Field(None, description="Channel-scoped episode ID; generated when omitted")
    user_id: Optional[str] = "user_krishna_01"
    production_type: Optional[str] = "Theme"
    tier: Optional[str] = "low_cost"
    video_type: Optional[str] = "Travel Guide & Doc"
    format_type: Optional[str] = "Long (16:9)"
    style_type: Optional[str] = "Realistic (Photoreal)"
    youtube_url: Optional[str] = None
    youtube_reference_url: Optional[str] = None
    youtube_reference_link: Optional[str] = None
    duration_seconds: Optional[float] = 6.0
    enable_bgm: Optional[bool] = None
    bgm: Optional[bool] = None
    enable_tts: Optional[bool] = None
    tts: Optional[bool] = None
    enable_voice_over: Optional[bool] = None
    voice_over: Optional[bool] = None
    enable_lipsync: Optional[bool] = None
    lipsync: Optional[bool] = None
    voice_gender: Optional[str] = None
    narration_male: Optional[bool] = None
    narration_female: Optional[bool] = None
    language: Optional[str] = "en"
    country: Optional[str] = None
    culture: Optional[str] = None
    target_languages: Optional[list[str]] = None
    theme: Optional[str] = None
    idea: Optional[str] = None
    script: Optional[str] = None
    custom_script: Optional[str] = None
    channel_id: Optional[str] = None
    motion_model: Optional[str] = "wan_4k"
    allow_fallback: Optional[bool] = False
    num_shots: Optional[int] = 1
    long_play_hours: Optional[float] = None
    camera_motion: Optional[str] = "locked_tripod"
    genre: Optional[str] = None
    genre_label: Optional[str] = None
    sub_genre: Optional[str] = None
    sub_genre_label: Optional[str] = None
    primary_archetype: Optional[str] = None
    primary_archetype_label: Optional[str] = None
    image_model: Optional[str] = "zimage"
    script_only: Optional[bool] = False
    narration_only: Optional[bool] = False
    screenplay_only: Optional[bool] = False
    photos_only: Optional[bool] = False
    motion_only: Optional[bool] = False
    audio_only: Optional[bool] = False
    bgm_only: Optional[bool] = False
    master_only: Optional[bool] = False
    pipeline_strategy: Optional[str] = "manual"
    execution_mode: Optional[str] = "test"
    force_rerun: Optional[bool] = False
    enable_voiceover: Optional[bool] = False
    dual_editions: Optional[bool] = False
    weather: Optional[str] = "normal"
    production_name: Optional[str] = None
    format: Optional[str] = None
    format_slug: Optional[str] = None
    aspect_ratio: Optional[str] = None
    tts_model: Optional[str] = None
    vocal_gender: Optional[str] = None
    target_shot_index: Optional[int] = None


class LocalProduceResponse(BaseModel):
    """Response returned after local single-pass video render."""
    success: bool
    job_id: str
    episode_id: str
    title: str
    production_name: Optional[str] = None
    story: Optional[dict[str, Any]] = None
    screenplay: Optional[dict[str, Any]] = None
    script: Optional[dict[str, Any]] = None
    video_url: Optional[str] = None
    nature_video_url: Optional[str] = None
    storage_path: Optional[str] = None
    file_size_bytes: Optional[int] = 0
    duration_seconds: float
    render_time_seconds: float
    artifacts: list[dict[str, Any]]
    editions: Optional[list[dict[str, Any]]] = None
    long_play_hours: Optional[float] = None
    keyframes: Optional[list[dict[str, Any]]] = None
    audio_stems: Optional[list[dict[str, Any]]] = None
    motion_clips: Optional[list[dict[str, Any]]] = None
    current_stage: Optional[int] = 1
    stage: Optional[int] = 1


def _reserve_next_episode_id(
    user_id: str,
    channel_id: str,
    format_slug: Optional[str] = None,
    production_name: Optional[str] = None,
) -> str:
    """Reserve next sequential episode ID code strictly scoped to production_name/title (starts at EP-001)."""
    clean_fmt = re.sub(r"[^a-zA-Z0-9_-]", "_", str(format_slug or 'documentary').lower()).strip("_")
    clean_prod = re.sub(r"[^a-zA-Z0-9_-]", "_", str(production_name or '').lower()).strip("_")
    if not clean_prod or clean_prod in ("standalone", "none", "documentary", "relaxation"):
        return "EP-001"

    prod_dir = storage_service.get_channel_path(user_id, channel_id) / clean_fmt / clean_prod
    highest = 0
    if prod_dir.exists() and prod_dir.is_dir():
        for sub in prod_dir.iterdir():
            if sub.is_dir():
                m = re.search(r"ep[-_]?(\d+)", sub.name, re.IGNORECASE)
                if m:
                    highest = max(highest, int(m.group(1)))
    return f"ep-{highest + 1:03d}"


@router.post("/local-produce", response_model=LocalProduceResponse, status_code=status.HTTP_200_OK)
async def produce_video_locally(req: LocalProduceRequest):
    """Synthesize a complete broadcast-grade MP4 video with scenes and audio stems."""
    raw_dur = req.duration_seconds
    is_auto_dur = raw_dur is not None and (float(raw_dur) <= 0 or float(raw_dur) == -1)
    capped_duration = -1.0 if is_auto_dur else min(28800.0, max(4.0, float(raw_dur or 6.0)))
    eff_bgm = req.enable_bgm if req.enable_bgm is not None else (req.bgm if req.bgm is not None else True)
    user_id_val = req.user_id or "user_krishna_01"
    strat = req.pipeline_strategy or "manual"
    eff_script_only = bool(req.script_only)
    eff_photos_only = bool(req.photos_only)
    eff_motion_only = bool(req.motion_only)
    eff_audio_only = bool(req.audio_only)
    eff_master_only = bool(req.master_only)

    # In manual Stage-Gate mode: if no downstream stage (photos/motion/audio/master) is explicitly requested,
    # it MUST run Stage 1 only and pause for approval.
    if strat == "manual":
        if not (eff_photos_only or eff_motion_only or eff_audio_only or eff_master_only):
            eff_script_only = True

    eff_channel_id = req.channel_id
    if not eff_channel_id:
        user_obj = repo.get_user_by_email(user_id_val) if "@" in user_id_val else None
        if user_obj:
            user_chans = repo.list_channels(user_obj.id)
            if user_chans:
                eff_channel_id = user_chans[0].channel_slug
    eff_channel_id = eff_channel_id or "default_channel"
    eff_fmt_req = str(req.format_slug or req.format or "documentary").lower()
    eff_prod_req = req.production_name or req.prompt or req.title or ""
    episode_id = req.episode_id or _reserve_next_episode_id(
        user_id_val, eff_channel_id, format_slug=eff_fmt_req, production_name=eff_prod_req
    )
    title = (req.title or req.prompt or req.production_name or f"Episode {episode_id}").strip()
    if len(title) > 80:
        title = title[:77] + "..."
    if not title:
        title = f"Episode {episode_id}"

    topic_check = None
    if req.prompt.strip():
        topic_check = await check_topic_duplicate(
            topic=title, metadata={"video_type": req.video_type, "format_type": req.format_type, "style_type": req.style_type},
            final_story=req.prompt, user_id=user_id_val, channel_id=eff_channel_id, threshold=0.80,
        )
    if topic_check and topic_check.get("is_duplicate"):
        logger.info(f"topic_duplicate_pivot: {title} matches {topic_check.get('matched_episode')}. Auto-pivoting angle.")
        pivots = ["Golden Twilight & Evening Mist", "Morning Glacial Mist & Soft Sunlight", "Tranquil Sunset Glow", "Lush Rainforest Canopy"]
        pivot_tag = pivots[int(time.time()) % len(pivots)]
        title = f"{title} ~ {pivot_tag}"

    job_id = f"job_{episode_id.lower()}_{int(time.time())}"
    job_manager.create_job(job_id=job_id, episode_id=episode_id, title=title, channel_id=eff_channel_id, user_id=user_id_val)

    has_fal = bool(_fal_api_key())
    eff_fallback = bool(req.allow_fallback or not has_fal)
    eff_motion = req.motion_model if req.motion_model and req.motion_model != "auto" else ("wan" if (capped_duration > 0 and capped_duration <= 10.0) else "auto")

    t0 = time.time()
    logger.info(
        f"api_production_triggered: episode_id='{episode_id}' channel='{eff_channel_id}' "
        f"script_only={eff_script_only} photos_only={eff_photos_only} motion_only={eff_motion_only} "
        f"audio_only={eff_audio_only} master_only={eff_master_only} duration={capped_duration}s timestamp={t0}"
    )
    print(f"\n[API PRODUCTION TRIGGERED] Episode: {episode_id} | Channel: {eff_channel_id} | Flags: script={eff_script_only}, photos={eff_photos_only}, motion={eff_motion_only}, audio={eff_audio_only}, master={eff_master_only} | Duration: {capped_duration}s")

    req_g_lower = (req.genre or "").lower()
    is_req_travel = (
        req_g_lower.startswith("travel")
        or eff_channel_id == "skylinediariesindia4k"
        or (req.primary_archetype or "").lower() in ("cities", "tourist_places", "iconic_places", "spiritual_places", "natural_wonders", "remote_places")
        or req.num_shots == -1
    )
    eff_api_shots = -1 if is_req_travel else (req.num_shots or 0)
    if is_req_travel:
        logger.info(f"api_travel_shots_cadence: duration={capped_duration}s -> num_shots=-1 (autonomous cadence)")

    req_fmt = str(req.format_slug or req.format or "").lower()
    if req_fmt == "music_video" or req_g_lower.startswith(("music/", "dance/")):
        from src.studios.music_video_studio.music_pipeline import MusicVideoPipeline
        pipe = MusicVideoPipeline(
            user_id=user_id_val, channel_id=eff_channel_id, episode_id=episode_id,
            production_name=req.production_name or "standalone",
        )
        mv_res = await pipe.produce(
            genre=req.genre or "music/static_vocal", sub_genre=req.sub_genre, primary_archetype=req.primary_archetype,
            prompt=req.prompt, country=req.country, language=req.language, culture=req.culture,
            duration_seconds=capped_duration, num_shots=eff_api_shots if eff_api_shots > 0 else 1,
            tier=req.tier or "balanced", script_only=eff_script_only, photos_only=eff_photos_only,
            audio_only=eff_audio_only, master_only=eff_master_only,
        )
        eff_stage = mv_res.get("current_stage", 1)
        job_manager.update_job(
            job_id=job_id, stage=eff_stage, progress=100 if eff_stage >= 5 else eff_stage * 20,
            status="completed" if eff_stage >= 5 else "ready", keyframes=mv_res.get("keyframes", []),
            motion_clips=[], audio_stems=mv_res.get("audio_stems", []), video_url=mv_res.get("video_url"),
        )
        return LocalProduceResponse(**mv_res)

    try:
        result = await produce_channel_video(
            channel_id=eff_channel_id,
            prompt=req.prompt,
            duration_seconds=capped_duration,
            episode_id=episode_id,
            script_only=eff_script_only,
            photos_only=eff_photos_only,
            motion_only=eff_motion_only,
            audio_only=eff_audio_only,
            master_only=eff_master_only,
            pipeline_strategy=strat,
            no_bgm=not eff_bgm,
            enable_voiceover=bool(req.enable_voiceover),
            num_shots=eff_api_shots,
            allow_fallback=eff_fallback,
            user_id=user_id_val,
            motion_model=eff_motion,
            long_play_hours=req.long_play_hours,
            camera_motion=req.camera_motion or "locked_tripod",
            force_rerun=bool(req.force_rerun),
            genre=req.genre,
            sub_genre=req.sub_genre,
            primary_archetype=req.primary_archetype,
            selection_labels={
                "genre": req.genre_label or "",
                "sub_genre": req.sub_genre_label or "",
                "primary_archetype": req.primary_archetype_label or "",
            },
            image_model=req.image_model or "zimage",
            dual_editions=bool(req.dual_editions),
            tier=req.tier or "balanced",
            weather=req.weather or "normal",
            production_name=req.production_name,
            format_slug=req.format_slug or (req.format if req.format and req.format not in ("16:9", "9:16") else None),
            tts_model=req.tts_model,
            execution_mode=req.execution_mode or "test",
            target_shot_index=req.target_shot_index,
        )
        eff_job_id = result.get("job_id") or job_id
        if eff_script_only:
            job_manager.update_job(
                job_id=eff_job_id, stage=1, progress=15, status="ready",
                keyframes=[], motion_clips=[], audio_stems=[], video_url=None,
            )
        elif eff_photos_only:
            job_manager.update_job(
                job_id=eff_job_id, stage=2, progress=40, status="ready",
                keyframes=result.get("keyframes", []), motion_clips=[],
                audio_stems=[], video_url=None,
            )
        elif eff_audio_only:
            job_manager.update_job(
                job_id=eff_job_id, stage=3, progress=65, status="ready",
                keyframes=result.get("keyframes", []), motion_clips=[],
                audio_stems=result.get("audio_stems", []), video_url=None,
            )
        elif eff_motion_only:
            job_manager.update_job(
                job_id=eff_job_id, stage=4, progress=80, status="ready",
                keyframes=result.get("keyframes", []), motion_clips=result.get("motion_clips", []),
                audio_stems=result.get("audio_stems", []), video_url=None,
            )
        else:
            job_manager.update_job(
                job_id=eff_job_id, stage=5, progress=100, status="completed",
                keyframes=result.get("keyframes", []), motion_clips=result.get("motion_clips", []),
                audio_stems=result.get("audio_stems", []), video_url=result.get("video_url"),
            )
            await remember_topic(
                topic=result.get("title") or title, metadata={"video_type": req.video_type, "format_type": req.format_type, "style_type": req.style_type},
                final_story=req.prompt, episode_id=episode_id, user_id=user_id_val, channel_id=eff_channel_id,
            )
        total_dur = time.time() - t0
        logger.info(f"api_production_completed: episode_id='{episode_id}' total_duration={total_dur:.2f}s timestamp={time.time()}")
        print(f"[API PRODUCTION COMPLETED] Episode {episode_id} finished in {total_dur:.2f}s.\n")
        return LocalProduceResponse(**result)
    except HTTPException:
        total_dur = time.time() - t0
        logger.error(f"api_production_failed: episode_id='{episode_id}' duration={total_dur:.2f}s error='HTTPException' timestamp={time.time()}")
        job_manager.update_job(job_id=job_id, status="failed", error="HTTP Exception")
        raise
    except Exception as exc:
        total_dur = time.time() - t0
        logger.error(f"local_production_failed: episode_id='{episode_id}' duration={total_dur:.2f}s error='{exc}' timestamp={time.time()}", exc_info=True)
        job_manager.update_job(job_id=job_id, status="failed", error=str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Local production failed: {str(exc)}")


@router.get("/poll-artifacts")
async def poll_production_artifacts(
    channel_id: str,
    episode_id: str,
    format: Optional[str] = None,
    production_name: Optional[str] = None,
    user_id: str = "knpillutla@gmail.com",
):
    """Real-time disk scanner returning synthesized keyframes, motion clips, and audio as they finish."""
    c_dir = storage_service.find_episode_path(
        user_id=user_id,
        channel_id=channel_id,
        episode_id=episode_id,
        format_slug=format,
        production_name=production_name,
    )
    if not c_dir or not c_dir.exists():
        return {"keyframes": [], "motion_clips": [], "audio_stems": [], "video_url": None, "stage": 1}

    files = {f.name: f for f in c_dir.iterdir() if f.is_file()}
    def _file_url(f: Path) -> str:
        try:
            mtime = int(f.stat().st_mtime) if f.exists() else int(time.time())
            rel = f.resolve().relative_to(storage_service.root_dir.resolve())
            return f"/storage/{str(rel).replace('\\', '/')}?t={mtime}"
        except Exception:
            p_str = str(f.resolve()).replace("\\", "/")
            mtime = int(f.stat().st_mtime) if f.exists() else int(time.time())
            if "/storage/" in p_str:
                return f"/storage/{p_str.split('/storage/', 1)[1]}?t={mtime}"
            return f"/storage/{f.name}?t={mtime}"

    kfs = [{"name": f"Shot {k.replace('keyframe_p','').replace('.jpg','')}", "url": _file_url(files[k]), "filename": k} for k in sorted(files) if k.startswith("keyframe_p") and k.endswith(".jpg") and files[k].stat().st_size > 1000]
    if not kfs and (c_dir / "scenes").exists():
        kfs = [{"name": f"Scene {p.stem.replace('scene_', '')}", "url": _file_url(p), "filename": p.name} for p in sorted((c_dir / "scenes").glob("scene_*.jpg")) if p.stat().st_size > 1000]

    manifest_file = c_dir / "episode_manifest.json"
    m_data = json.loads(manifest_file.read_text("utf-8")) if manifest_file.exists() else {}
    m_mot_type = m_data.get("motion_model", "")
    if m_mot_type in ("ken_burns", "local", "local_drone", "local_zoompan"):
        m_model = "Local Drone"
    elif m_mot_type in ("wan", "wan_2_1") or m_data.get("duration_seconds", 5.0) <= 10.0:
        m_model = "Wan 2.1"
    else:
        m_model = "Kling v3 Pro"
    vids = [{"name": f"Motion {m.replace('motion_p','').replace('.mp4','')}", "url": _file_url(files[m]), "model": m_model} for m in sorted(files) if m.startswith("motion_p") and m.endswith(".mp4") and not m.endswith("_fwd_seamless.mp4") and files[m].stat().st_size > 1000]

    stems = []
    if "spoken_narration.mp3" in files and files["spoken_narration.mp3"].stat().st_size > 1000:
        stems.append({"name": "Neural Broadcast Narration", "filename": "spoken_narration.mp3", "url": _file_url(files["spoken_narration.mp3"]), "role": "narration", "stem_type": "narration", "type": "azure_speech", "voice_name": "en-GB-RyanNeural", "color": "indigo"})
    if "raw_soundtrack.mp3" in files and files["raw_soundtrack.mp3"].stat().st_size > 1000:
        stems.append({"name": "Suno Soundtrack", "filename": "raw_soundtrack.mp3", "url": _file_url(files["raw_soundtrack.mp3"]), "color": "cyan"})
    if "velvet_binaural_master_48k.mp3" in files and files["velvet_binaural_master_48k.mp3"].stat().st_size > 1000:
        stems.append({"name": "432Hz Velvet Binaural ASMR", "filename": "velvet_binaural_master_48k.mp3", "url": _file_url(files["velvet_binaural_master_48k.mp3"]), "color": "emerald"})
    if not stems and (c_dir / "stems").exists():
        stems = [{"name": "Suno Vocal Soundtrack" if "soundtrack" in a.name else a.stem, "filename": a.name, "url": _file_url(a), "color": "cyan"} for a in sorted((c_dir / "stems").glob("*.mp3")) if a.stat().st_size > 1000]

    has_narr_master = "master_4k_narration.mp4" in files and files["master_4k_narration.mp4"].stat().st_size > 1000
    has_amb_master = "master_4k_ambient.mp4" in files and files["master_4k_ambient.mp4"].stat().st_size > 1000
    has_nat_master = ("master_4k_nature.mp4" in files and files["master_4k_nature.mp4"].stat().st_size > 1000) or ("master_4k_ambient_nature_only.mp4" in files and files["master_4k_ambient_nature_only.mp4"].stat().st_size > 1000)
    nat_f = files.get("master_4k_nature.mp4") or files.get("master_4k_ambient_nature_only.mp4")
    master_url = _file_url(files["master_4k_narration.mp4"]) if has_narr_master else (_file_url(files["master_4k_ambient.mp4"]) if has_amb_master else None)
    nature_master_url = _file_url(nat_f) if has_nat_master else (_file_url(files["master_4k_ambient.mp4"]) if has_amb_master else None)
    if not master_url and (c_dir / "master_renders").exists():
        for m in sorted((c_dir / "master_renders").glob("*.mp4")):
            if m.stat().st_size > 1000:
                master_url = _file_url(m)
                break

    dur_str = f"{int(m_data.get('duration_seconds', 5))}s"
    editions = []
    if has_narr_master:
        editions.append({"edition_id": "master_narration", "name": f"🎙️ 4K Narrated Master ({dur_str})", "label": "4K Narrated Master (Voiceover + BGM)", "format": "4K UHD", "duration": dur_str, "url": _file_url(files["master_4k_narration.mp4"])})
    if has_amb_master:
        editions.append({"edition_id": "master_music", "name": f"🎵 4K Music Edition ({dur_str})", "label": "4K Ambient Master (Music Only)", "format": "4K UHD", "duration": dur_str, "url": _file_url(files["master_4k_ambient.mp4"])})
    if has_nat_master:
        editions.append({"edition_id": "master_nature", "name": f"🌿 4K Pure Nature Edition ({dur_str})", "label": "4K Pure Nature ASMR (Zero Music)", "format": "4K Nature", "duration": dur_str, "url": _file_url(nat_f)})
    if "short_9x16_teaser.mp4" in files and files["short_9x16_teaser.mp4"].stat().st_size > 1000:
        editions.append({"edition_id": "short_teaser", "name": "📱 9:16 Vertical Short Teaser (20s)", "label": "9:16 Vertical YouTube Short / Reel", "format": "9:16 Short", "duration": "20s", "url": _file_url(files["short_9x16_teaser.mp4"])})

    long_play_editions = []
    fmt_val = str(m_data.get("format") or "").lower()
    is_relax_fmt = fmt_val in ("relaxation", "relax") or "relax" in str(m_data.get("genre", "")).lower() or "/relaxation/" in c_dir.as_posix().lower()
    if is_relax_fmt:
        lp_patterns = [
            (["master_4k_8hour_broadcast.mp4", "master_4k_8hour_sleep.mp4"], "8h_music", "8-Hour 4K Broadcast (Music)", "fa-music text-indigo-400", "Music + 432Hz BGM", "8:00:00 (8h)", "16:9 Long-Play"),
            (["master_4k_8hour_nature_only_broadcast.mp4", "master_4k_8hour_nature_only.mp4"], "8h_nature", "8-Hour 4K Broadcast (Pure Nature)", "fa-leaf text-emerald-400", "Pure Nature Foley ASMR", "8:00:00 (8h)", "16:9 Long-Play"),
            (["master_4k_3hour_broadcast.mp4", "master_4k_3hour_sleep.mp4"], "3h_music", "3-Hour 4K Broadcast (Music)", "fa-music text-indigo-400", "Music + 432Hz BGM", "3:00:00 (3h)", "16:9 Long-Play"),
            (["master_4k_3hour_nature_only_broadcast.mp4", "master_4k_3hour_nature_only.mp4"], "3h_nature", "3-Hour 4K Broadcast (Pure Nature)", "fa-leaf text-emerald-400", "Pure Nature Foley ASMR", "3:00:00 (3h)", "16:9 Long-Play"),
        ]
        for fn_list, eid, name, icon, mode, dur, fmt in lp_patterns:
            target_f = next((files[fn] for fn in fn_list if fn in files and files[fn].stat().st_size > 1000), None)
            if target_f:
                sz_mb = round(target_f.stat().st_size / (1024 * 1024), 1)
                long_play_editions.append({"edition_id": eid, "name": name, "icon": icon, "audio_mode": mode, "duration": dur, "format": fmt, "status": "completed", "url": _file_url(target_f), "size_str": f"{sz_mb} MB" if sz_mb < 1000 else f"{round(sz_mb/1024, 2)} GB", "filename": target_f.name})

    raw_sp = c_dir / "raw_gemini_screenplay.json"
    screenplay_file = raw_sp if (raw_sp.exists() and raw_sp.stat().st_size > 100) else (c_dir / "screenplay.json" if (c_dir / "screenplay.json").exists() else c_dir / "storyboard.json")
    screenplay_data = json.loads(screenplay_file.read_text("utf-8")) if screenplay_file.exists() else None

    raw_story_file = c_dir / "raw_gemini_story.json"
    if not raw_story_file.exists():
        raw_story_file = c_dir / "story.json"
    story_data = json.loads(raw_story_file.read_text("utf-8")) if raw_story_file.exists() else None
    if not story_data and screenplay_data:
        ch_list = []
        seen = set()
        for sc in screenplay_data.get("scenes", []):
            ct = sc.get("chapter_title") or f"Chapter {len(ch_list) + 1}"
            if ct in seen:
                continue
            seen.add(ct)
            ch_list.append({
                "chapter_index": len(ch_list) + 1,
                "chapter_title": ct,
                "chapter_subtitle": sc.get("chapter_subtitle", ""),
                "chapter_stats": sc.get("chapter_stats", ""),
                "fact_badge": sc.get("fact_badge", ""),
                "narration": sc.get("narration_text", "") or sc.get("narration", ""),
            })
        story_data = {
            "episode_id": episode_id,
            "title": screenplay_data.get("title") or m_data.get("title"),
            "story_topic": screenplay_data.get("story_topic") or m_data.get("story_topic"),
            "destination_entity": screenplay_data.get("destination_entity") or m_data.get("production_name"),
            "synopsis": screenplay_data.get("story_topic") or m_data.get("prompt"),
            "chapters": ch_list,
            "spoken_narration_script": (screenplay_data.get("audio_master") or {}).get("spoken_narration_script", ""),
            "total_words_count": screenplay_data.get("total_words_count"),
            "pinned_comment": screenplay_data.get("pinned_comment"),
        }

    pipeline_state_file = c_dir / "pipeline_state.json"
    pipeline_state_data = json.loads(pipeline_state_file.read_text("utf-8")) if pipeline_state_file.exists() else None

    is_approved_val = bool(pipeline_state_data.get("is_approved") if pipeline_state_data else m_data.get("is_approved", False))
    eff_stage = pipeline_state_data.get("current_stage") if pipeline_state_data else (m_data.get("current_stage", 1) if m_data else 1)

    has_master_file = bool(master_url or ("master_4k_ambient.mp4" in files) or ("master_4k_nature.mp4" in files))
    ep_status = "completed" if has_master_file else (pipeline_state_data.get("status") if pipeline_state_data else "ready")
    eff_format = "relaxation" if is_relax_fmt else (m_data.get("format") or "relaxation")
    eff_genre = m_data.get("genre") or ("relax/rain" if "rain" in c_dir.name else "relax/nature")

    user_inputs_file = c_dir / "user_inputs.json"
    u_data = json.loads(user_inputs_file.read_text("utf-8")) if user_inputs_file.exists() else None

    gemini_story_inputs_file = c_dir / "gemini_story_inputs.json"
    g_story_inputs = json.loads(gemini_story_inputs_file.read_text("utf-8")) if gemini_story_inputs_file.exists() else None

    gemini_sp_inputs_file = c_dir / "gemini_screenplay_inputs.json"
    g_sp_inputs = json.loads(gemini_sp_inputs_file.read_text("utf-8")) if gemini_sp_inputs_file.exists() else None

    return {
        "keyframes": kfs, "motion_clips": vids, "audio_stems": stems,
        "video_url": master_url or nature_master_url, "nature_video_url": nature_master_url,
        "editions": editions, "long_play_editions": long_play_editions, "stage": eff_stage,
        "status": ep_status,
        "currentStage": eff_stage,
        "current_stage": eff_stage,
        "format": eff_format,
        "format_slug": eff_format,
        "genre": eff_genre,
        "script": screenplay_data if screenplay_data else (m_data if m_data else None),
        "screenplay": screenplay_data,
        "story": story_data,
        "pipeline_state": pipeline_state_data,
        "manifest": m_data if m_data else None,
        "user_inputs": u_data,
        "gemini_story_inputs": g_story_inputs,
        "gemini_screenplay_inputs": g_sp_inputs,
        "gemini_inputs": g_story_inputs,
        "production_name": (u_data.get("production_name") if u_data else (m_data.get("production_name") if m_data else (story_data.get("destination_entity") if story_data else None))),
        "is_approved": is_approved_val,
        "long_play_hours": m_data.get("long_play_hours"),
    }


@router.post("/episodes/{episode_id}/approve")
async def approve_episode(episode_id: str, channel_id: Optional[str] = None, user_id: str = "knpillutla@gmail.com"):
    """Mark an episode as approved in its disk manifest."""
    user_container = storage_service.get_user_container_path(user_id)
    scan_roots = [user_container / "networks", user_container / "channels"]
    target_dirs = []
    for root in scan_roots:
        if not root.exists():
            continue
        if channel_id and (root / channel_id / episode_id).exists():
            target_dirs.append(root / channel_id / episode_id)
        else:
            for ch_dir in root.iterdir():
                if ch_dir.is_dir() and (ch_dir / episode_id).exists():
                    target_dirs.append(ch_dir / episode_id)

    if not target_dirs:
        return {"success": True, "episode_id": episode_id, "is_approved": True, "persisted_disk": False}

    for ep_dir in target_dirs:
        pipe_file = ep_dir / "pipeline_state.json"
        data = {}
        if pipe_file.exists():
            try:
                data = json.loads(pipe_file.read_text("utf-8"))
            except Exception:
                pass
        data["is_approved"] = True
        data["approved_at"] = time.time()
        pipe_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {"success": True, "episode_id": episode_id, "is_approved": True, "message": f"Episode {episode_id} approved."}


@router.post("/episodes/{episode_id}/update-inputs")
async def update_episode_inputs(
    episode_id: str,
    payload: dict[str, Any],
    channel_id: Optional[str] = None,
    user_id: str = "knpillutla@gmail.com",
    format: Optional[str] = None,
    production_name: Optional[str] = None,
):
    """Persist updated execution_mode and pipeline_strategy to user_inputs.json immediately."""
    ep_dir = storage_service.find_episode_path(
        user_id=user_id,
        channel_id=channel_id or "",
        episode_id=episode_id,
        format_slug=format,
        production_name=production_name,
    )
    if not ep_dir:
        user_container = storage_service.get_user_container_path(user_id)
        clean_target = episode_id.lower().replace("-", "_")
        for cand in user_container.rglob("*"):
            if cand.is_dir() and (cand.name.lower() == episode_id.lower() or cand.name.lower() == clean_target):
                ep_dir = cand
                break

    if ep_dir and ep_dir.is_dir():
        u_file = ep_dir / "user_inputs.json"
        try:
            data = json.loads(u_file.read_text("utf-8")) if u_file.is_file() else {}
            for k, v in payload.items():
                data[k] = v
            u_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            pipe_file = ep_dir / "pipeline_state.json"
            p_data = json.loads(pipe_file.read_text("utf-8")) if pipe_file.is_file() else {}
            if "pipeline_strategy" in payload:
                p_data["pipeline_strategy"] = payload["pipeline_strategy"]
            if "execution_mode" in payload:
                p_data["execution_mode"] = payload["execution_mode"]
            pipe_file.write_text(json.dumps(p_data, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"user_inputs_updated: {u_file.name} with {payload}")
            return {"success": True, "episode_id": episode_id, "updated": payload}
        except Exception as e:
            logger.warning(f"user_inputs_update_error: {e}")

    return {"success": False, "episode_id": episode_id, "error": "Episode not found"}



@router.delete("/episodes/{episode_id}")
async def delete_episode_artifacts(
    episode_id: str,
    channel_id: Optional[str] = None,
    format: Optional[str] = None,
    production_name: Optional[str] = None,
    storage_path: Optional[str] = None,
    user_id: str = "knpillutla@gmail.com",
):
    """Delete synthesized artifacts and folder for a specific scoped episode from disk."""
    clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", str(episode_id).lower()).strip("_")
    user_container = storage_service.get_user_container_path(user_id)
    deleted_paths = []

    # 1. Exact storage path if provided
    if storage_path:
        rel_clean = storage_path.replace("\\", "/").strip("/.")
        for base_root in (user_container.parent, user_container):
            candidate = (base_root / rel_clean).resolve()
            if (str(user_container.parent) in str(candidate)) and candidate.is_dir() and candidate.name.lower() in (episode_id.lower(), clean_ep):
                p_dir = candidate.parent
                robust_remove_directory(candidate)
                cleanup_empty_parent_production(p_dir, user_container)
                deleted_paths.append(str(candidate))
                return {"success": True, "episode_id": episode_id, "deleted_paths": deleted_paths, "message": f"Episode {episode_id} deleted."}

    # 2. Targeted search using channel_id, format, and production_name
    search_dirs = []
    if channel_id:
        net_dir = storage_service.get_network_path(user_id, channel_id)
        chan_dir = user_container / "channels" / channel_id
        for base in (net_dir, chan_dir):
            if not base.exists():
                continue
            if format and production_name and production_name != "standalone":
                p_clean = production_name.replace(" ", "_").lower()
                for f_name in (format, format.lower()):
                    search_dirs.extend([base / f_name / p_clean / episode_id, base / f_name / p_clean / clean_ep])
            elif format:
                for f_name in (format, format.lower()):
                    search_dirs.extend([base / f_name / episode_id, base / f_name / clean_ep])
                    f_dir = base / f_name
                    if f_dir.is_dir():
                        for p_sub in f_dir.iterdir():
                            if p_sub.is_dir():
                                search_dirs.extend([p_sub / episode_id, p_sub / clean_ep])

    matched = [d for d in search_dirs if d.is_dir()]
    if matched:
        for m in matched:
            p_dir = m.parent
            robust_remove_directory(m)
            cleanup_empty_parent_production(p_dir, user_container)
            deleted_paths.append(str(m))
        return {"success": True, "episode_id": episode_id, "deleted_paths": deleted_paths, "message": f"Episode {episode_id} deleted."}

    # 3. Scoped search across roots with strict format/production filtering
    scan_roots = []
    if channel_id:
        scan_roots.extend([storage_service.get_network_path(user_id, channel_id), user_container / "channels" / channel_id])
    else:
        scan_roots.extend([user_container / "networks", user_container / "channels", user_container / "productions"])

    candidates = []
    for root in scan_roots:
        if not root.exists():
            continue
        try:
            for sub in list(root.rglob("*")):
                if sub.is_dir() and sub.name.lower() in (episode_id.lower(), clean_ep):
                    sub_str = str(sub).replace("\\", "/").lower()
                    if format and format.lower() not in sub_str:
                        continue
                    if production_name and production_name != "standalone" and production_name.lower().replace(" ", "_") not in sub_str:
                        continue
                    candidates.append(sub)
        except Exception as e:
            logger.warning(f"delete_episode_artifacts scan warning: {e}")

    for c in candidates:
        p_dir = c.parent
        robust_remove_directory(c)
        cleanup_empty_parent_production(p_dir, user_container)
        deleted_paths.append(str(c))

    return {"success": True, "episode_id": episode_id, "deleted_paths": deleted_paths, "message": f"Episode {episode_id} deleted."}


@router.post("/stop")
async def stop_production_job(payload: dict):
    """Mark production job as paused and signal cancellation."""
    return {"success": True, "episode_id": payload.get("episode_id", "EP-001"), "status": "paused"}


@router.get("/jobs/{job_id}")
async def get_production_job_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found.")
    return job


@router.get("/jobs/{job_id}/stream")
async def stream_production_job_progress(job_id: str):
    return StreamingResponse(job_manager.stream_job(job_id), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})
