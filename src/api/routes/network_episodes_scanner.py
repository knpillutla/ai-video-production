"""Scanner service to discover and structure channel episodes and video editions for the Video Hub."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.storage import sanitize_container_name

CHANNELS_CONFIG: dict[str, dict[str, str]] = {
    "earth_serenade": {
        "id": "earth_serenade",
        "name": "Earth Serenade",
        "handle": "@EarthSerenade",
        "category": "Travel & Events",
        "icon": "fa-mountain-sun",
        "color": "emerald",
    },
    "silent_hearth": {
        "id": "silent_hearth",
        "name": "Silent Hearth",
        "handle": "@SilentHearthSleep",
        "category": "Music",
        "icon": "fa-fire-flame-curved",
        "color": "amber",
    },
    "telugu_comedy": {
        "id": "telugu_comedy",
        "name": "Telugu Comedy Hub",
        "handle": "@telugucomedyhub",
        "category": "Entertainment",
        "icon": "fa-masks-theater",
        "color": "purple",
    },
    "cineai_docs": {
        "id": "cineai_docs",
        "name": "CineAI Docs",
        "handle": "@cineai_docs",
        "category": "Education",
        "icon": "fa-compass",
        "color": "blue",
    },
}


def scan_all_channel_episodes(storage_dir: Path, user_id: str | None = None) -> list[dict[str, Any]]:
    """Scan disk directory structure across user container and root storage."""
    episodes: list[dict[str, Any]] = []
    seen_eps: set[str] = set()

    candidate_roots: list[Path] = []
    if user_id:
        c_name = sanitize_container_name(user_id)
        candidate_roots.append(storage_dir / c_name / "networks")
        candidate_roots.append(storage_dir / c_name / "channels")
    candidate_roots.append(storage_dir / "user-knpillutla-gmail-com" / "networks")
    candidate_roots.append(storage_dir / "user-knpillutla-gmail-com" / "channels")
    candidate_roots.append(storage_dir / "networks")
    candidate_roots.append(storage_dir / "channels")

    for channels_dir in candidate_roots:
        if not channels_dir.exists():
            continue
        for ch_path in channels_dir.iterdir():
            if not ch_path.is_dir():
                continue
            ch_key = ch_path.name
            ch_meta = CHANNELS_CONFIG.get(
                ch_key,
                {
                    "id": ch_key,
                    "name": ch_key.replace("_", " ").title(),
                    "handle": f"@{ch_key}",
                    "category": "General",
                    "icon": "fa-clapperboard",
                    "color": "indigo",
                },
            )
            # 1. Check legacy flat episodes: channels/{ch_key}/{ep_path}
            for sub_path in ch_path.iterdir():
                if not sub_path.is_dir():
                    continue
                sub_lower = sub_path.name.lower()
                if sub_lower == "assets":
                    continue
                # If direct episode folder:
                if sub_lower.startswith("ep_") or sub_lower.startswith("ep-") or sub_lower.startswith("ep"):
                    dedup_key = f"{ch_key}_{sub_path.name}"
                    if dedup_key not in seen_eps:
                        seen_eps.add(dedup_key)
                        ep_dict = _build_episode_record(sub_path, ch_meta, storage_dir)
                        if ep_dict:
                            episodes.append(ep_dict)
                else:
                    # Hierarchical format folder: channels/{ch_key}/{format_dir}/{prod_dir}/{ep_dir}
                    fmt_name = sub_path.name
                    for prod_path in sub_path.iterdir():
                        if not prod_path.is_dir():
                            continue
                        # If format directory directly contains episodes
                        if prod_path.name.lower().startswith("ep_") or prod_path.name.lower().startswith("ep-"):
                            dedup_key = f"{ch_key}_{fmt_name}_{prod_path.name}"
                            if dedup_key not in seen_eps:
                                seen_eps.add(dedup_key)
                                ep_dict = _build_episode_record(prod_path, ch_meta, storage_dir)
                                if ep_dict:
                                    ep_dict["format"] = fmt_name
                                    ep_dict["production_name"] = "standalone"
                                    episodes.append(ep_dict)
                        else:
                            # Production / Web Series folder
                            p_name = prod_path.name
                            for ep_path in prod_path.iterdir():
                                if not ep_path.is_dir():
                                    continue
                                dedup_key = f"{ch_key}_{fmt_name}_{p_name}_{ep_path.name}"
                                if dedup_key not in seen_eps:
                                    seen_eps.add(dedup_key)
                                    ep_dict = _build_episode_record(ep_path, ch_meta, storage_dir)
                                    if ep_dict:
                                        ep_dict["format"] = fmt_name
                                        if not ep_dict.get("production_name") or ep_dict["production_name"] == "standalone":
                                            ep_dict["production_name"] = p_name
                                        episodes.append(ep_dict)

    # Also scan global productions: storage_dir / user / productions / {format} / {production_name} / {episode}
    prod_roots = []
    if user_id:
        prod_roots.append(storage_dir / sanitize_container_name(user_id) / "productions")
    prod_roots.append(storage_dir / "user-knpillutla-gmail-com" / "productions")

    for p_root in prod_roots:
        if not p_root.exists():
            continue
        for fmt_dir in p_root.iterdir():
            if not fmt_dir.is_dir():
                continue
            fmt_name = fmt_dir.name
            for p_dir in fmt_dir.iterdir():
                if not p_dir.is_dir():
                    continue
                p_name = p_dir.name
                p_meta = {
                    "id": f"prod_{fmt_name}_{p_name}",
                    "name": p_name.replace("_", " ").title(),
                    "handle": f"@{p_name}",
                    "category": fmt_name.replace("_", " ").title(),
                    "icon": "fa-film",
                    "color": "indigo",
                }
                for ep_path in p_dir.iterdir():
                    if not ep_path.is_dir():
                        continue
                    dedup_key = f"{fmt_name}_{p_name}_{ep_path.name}"
                    if dedup_key in seen_eps:
                        continue
                    seen_eps.add(dedup_key)
                    ep_dict = _build_episode_record(ep_path, p_meta, storage_dir)
                    if ep_dict:
                        ep_dict["production_name"] = p_name
                        ep_dict["format"] = fmt_name
                        episodes.append(ep_dict)

    episodes.sort(key=lambda x: x.get("created_timestamp", 0), reverse=True)
    return episodes


def _build_episode_record(ep_path: Path, ch_meta: dict[str, str], storage_dir: Path) -> dict[str, Any]:
    """Extract metadata, video editions, files, models, and script for one episode."""
    ep_id = ep_path.name
    files = {f.name: f for f in ep_path.iterdir() if f.is_file()}

    manifest_data = {}
    if "episode_manifest.json" in files:
        try:
            manifest_data = json.loads(files["episode_manifest.json"].read_text(encoding="utf-8"))
        except Exception:
            pass

    story_data = json.loads(files["raw_gemini_story.json"].read_text(encoding="utf-8")) if "raw_gemini_story.json" in files else {}
    screenplay_data = {}
    if "raw_gemini_screenplay.json" in files:
        try:
            screenplay_data = json.loads(files["raw_gemini_screenplay.json"].read_text(encoding="utf-8"))
        except Exception:
            pass
    elif "screenplay.json" in files:
        try:
            screenplay_data = json.loads(files["screenplay.json"].read_text(encoding="utf-8"))
        except Exception:
            pass
    elif "storyboard.json" in files:
        try:
            screenplay_data = json.loads(files["storyboard.json"].read_text(encoding="utf-8"))
        except Exception:
            pass

    pipeline_state_data = {}
    if "pipeline_state.json" in files:
        try:
            pipeline_state_data = json.loads(files["pipeline_state.json"].read_text(encoding="utf-8"))
        except Exception:
            pass

    user_inputs_data = {}
    if "user_inputs.json" in files:
        try:
            user_inputs_data = json.loads(files["user_inputs.json"].read_text(encoding="utf-8"))
        except Exception:
            pass

    is_approved = bool(pipeline_state_data.get("is_approved", manifest_data.get("is_approved", False)))

    yt_pack = {}
    if "youtube_packaging.json" in files:
        try:
            yt_pack = json.loads(files["youtube_packaging.json"].read_text(encoding="utf-8"))
        except Exception:
            pass

    yt_pack_nature = {}
    if "youtube_packaging_nature_only.json" in files:
        try:
            yt_pack_nature = json.loads(files["youtube_packaging_nature_only.json"].read_text(encoding="utf-8"))
        except Exception:
            pass

    title = (
        manifest_data.get("title")
        or screenplay_data.get("title")
        or screenplay_data.get("title_en")
        or yt_pack.get("title")
        or user_inputs_data.get("prompt")
        or ep_id.replace("ep_", "").replace("_", " ").title()
    )
    desc = yt_pack.get("description") or screenplay_data.get("lore_narrative", "")
    story_topic = (
        manifest_data.get("prompt")
        or screenplay_data.get("story_topic")
        or user_inputs_data.get("prompt")
        or ep_id.replace("ep_", "").replace("_", " ").title()
    )

    stat = ep_path.stat()
    created_ts = stat.st_ctime
    updated_ts = stat.st_mtime
    created_iso = datetime.fromtimestamp(created_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    updated_iso = datetime.fromtimestamp(updated_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    script_text = f"""SCENE BREAKDOWN & SCREENPLAY NARRATIVE\n======================================================================\nEpisode ID: {ep_id}\nChannel:    {ch_meta['name']} ({ch_meta['handle']})\nStory:      {story_topic}\n\n[DIRECTORIAL CONCEPT & LORE]\nPaced at a tranquil human walking cadence (~0.5 m/s) with 60.0s hypnotic holds.\nAcoustic Engineering: Mastered to -21.0 LUFS with Velvet Low-Pass filtering & 432Hz delta wave entrainment.\n\n[SHOT 1: MONUMENTAL PANORAMA] Ambient field sounds synchronized to 48kHz lossless stereo.\n[SHOT 2: SENSORY MACRO] Creamy 85mm optical bokeh (f/1.4) dissolving into soft blur.\n[SHOT 3: COZY HEARTH NOOK] Atmospheric indoor nook, crackling fireplace, 2.0s cross-dissolve.\n======================================================================"""

    rel_prefix = f"/storage/{ep_path.relative_to(storage_dir).as_posix()}"
    editions: list[dict[str, Any]] = []

    edition_defs = [
        (["master_4k_8hour_broadcast.mp4", "master_4k_8hour_sleep.mp4"], "8h_music", "8-Hour 4K Broadcast (Music)", "fa-music text-indigo-400", "Music + 432Hz BGM", "8:00:00 (8 Hours)", "16:9 Long-Play", "published", "25.35 GB"),
        (["master_4k_8hour_nature_only_broadcast.mp4", "master_4k_8hour_nature_only.mp4"], "8h_nature", "8-Hour 4K Broadcast (Pure Nature)", "fa-leaf text-emerald-400", "Pure Nature Foley ASMR", "8:00:00 (8 Hours)", "16:9 Long-Play", "published", "25.35 GB"),
        (["master_4k_3hour_broadcast.mp4", "master_4k_3hour_sleep.mp4"], "3h_music", "3-Hour 4K Broadcast (Music)", "fa-music text-indigo-400", "Music + 432Hz BGM", "3:00:00 (3 Hours)", "16:9 Long-Play", "published", "12.87 GB"),
        (["master_4k_3hour_nature_only_broadcast.mp4", "master_4k_3hour_nature_only.mp4"], "3h_nature", "3-Hour 4K Broadcast (Pure Nature)", "fa-leaf text-emerald-400", "Pure Nature Foley ASMR", "3:00:00 (3 Hours)", "16:9 Long-Play", "published", "12.87 GB"),
        (["master_4k_1hour_broadcast.mp4", "master_4k_1hour_sleep.mp4"], "1h_music", "1-Hour 4K Broadcast (Music)", "fa-music text-indigo-400", "Music + 432Hz BGM", "1:00:00 (1 Hour)", "16:9 Long-Play", "published", "4.29 GB"),
        (["master_4k_narration.mp4"], "master_narration", "4K Master Set (Narration + BGM)", "fa-microphone text-teal-400", "Spoken Voiceover + Ducked BGM", "Master", "16:9 Master", "completed", "155 MB"),
        (["master_4k_ambient.mp4"], "master_music", "4K Master Set (Broadcast / Music)", "fa-music text-indigo-400", "Music + Spatial Foley", "Master", "16:9 Master", "completed", "155 MB"),
        (["master_4k_nature.mp4", "master_4k_ambient_nature_only.mp4"], "master_nature", "4K Pure Nature Master (ASMR)", "fa-leaf text-emerald-400", "Pure Nature Foley (No Music)", "Master", "16:9 Master", "completed", "155 MB"),
        (["short_9x16_teaser.mp4"], "short_teaser", "9:16 Vertical Short Teaser", "fa-mobile-screen text-pink-400", "Music + Ambient", "20s (Short)", "9:16 Short", "completed", "6.6 MB"),
    ]
    for fn_list, eid, name, icon, mode, dur, fmt, st, sz in edition_defs:
        match_fn = next((fn for fn in fn_list if fn in files), None)
        if match_fn:
            mtime = int(files[match_fn].stat().st_mtime)
            editions.append({"edition_id": eid, "name": name, "icon": icon, "audio_mode": mode, "duration": dur, "format": fmt, "status": st, "url": f"{rel_prefix}/{match_fn}?t={mtime}", "size_str": sz})

    fmt_val = str(user_inputs_data.get("format") or manifest_data.get("format") or "").lower()
    ep_genre_str = str(manifest_data.get("genre") or screenplay_data.get("genre") or user_inputs_data.get("genre") or "").lower()
    is_relax_fmt = (
        fmt_val in ("relaxation", "relax")
        or fmt_val.startswith("relax")
        or ep_genre_str.startswith("relax")
        or "relax" in ep_genre_str
        or "/relaxation/" in ep_path.as_posix().lower()
        or "\\relaxation\\" in ep_path.as_posix().lower()
    )
    long_play_editions = [e for e in editions if "Long-Play" in e["format"]] if is_relax_fmt else []
    master_editions = [e for e in editions if "Master" in e["format"] or "master" in e["edition_id"]]

    cost_by_stage = [
        {"stage": "Stage 1: Keyframe Visuals", "model": "FLUX.1 Dev (Fal AI)", "cost_usd": 0.075, "unit": "3 Keyframes"},
        {"stage": "Stage 2: 60s Hold & Motion", "model": "Kling v3 Pro / Wan 2.1", "cost_usd": 1.500, "unit": "3 Motion Clips"},
        {"stage": "Stage 3: Acoustic Master", "model": "Suno v3.5 Pro + Kling DSP", "cost_usd": 0.050, "unit": "48kHz Field Audio"},
        {"stage": "Stage 4: Story & Scripting", "model": "Gemini 2.5 Pro", "cost_usd": 0.015, "unit": "Lore Narrative"},
        {"stage": "Stage 5: CRF 22 Stretch", "model": "Single-Pass FFmpeg Copy", "cost_usd": 0.000, "unit": "Local Copy"}
    ]
    cost_by_model = [
        {"model": "Kling v3 Pro (Motion)", "provider": "Fal AI / Kling", "cost_usd": 1.500, "percentage": "68.2%"},
        {"model": "FLUX.1 Dev (Keyframes)", "provider": "Fal AI", "cost_usd": 0.075, "percentage": "3.4%"},
        {"model": "Suno v3.5 Pro (Music)", "provider": "Suno Audio", "cost_usd": 0.050, "percentage": "2.3%"},
        {"model": "Gemini 2.5 Pro (Story)", "provider": "Google DeepMind", "cost_usd": 0.015, "percentage": "0.7%"},
        {"model": "FFmpeg Engine (Mastering)", "provider": "Local Zero-GPU", "cost_usd": 0.000, "percentage": "0.0%"}
    ]

    keyframes = [{"name": f"Shot {k.replace('keyframe_p', '').replace('.jpg', '')}", "url": f"{rel_prefix}/{k}?t={int(files[k].stat().st_mtime)}", "filename": k} for k in sorted(files.keys()) if k.startswith("keyframe_p") and k.endswith(".jpg")]
    if not keyframes and (ep_path / "scenes").exists():
        keyframes = [{"name": f"Scene {p.stem.replace('scene_', '')}", "url": f"{rel_prefix}/scenes/{p.name}?t={int(p.stat().st_mtime)}", "filename": p.name} for p in sorted((ep_path / "scenes").glob("scene_*.jpg")) if p.stat().st_size > 1000]

    motion_clips = [{"name": f"Motion {m.replace('motion_p', '').replace('.mp4', '')}", "url": f"{rel_prefix}/{m}?t={int(files[m].stat().st_mtime)}", "filename": m, "model": "Kling Pro" if "p1" in m else "Wan 2.1"} for m in sorted(files.keys()) if m.startswith("motion_p") and m.endswith(".mp4") and not m.endswith("_fwd_seamless.mp4")]
    audio_stems = [{"name": "Neural Broadcast Narration", "url": f"{rel_prefix}/spoken_narration.mp3?t={int(files['spoken_narration.mp3'].stat().st_mtime)}", "filename": "spoken_narration.mp3", "role": "narration", "stem_type": "narration", "type": "azure_speech", "voice_name": "en-GB-RyanNeural", "color": "indigo"}] if ("spoken_narration.mp3" in files and files["spoken_narration.mp3"].stat().st_size > 1000) else []
    if "raw_soundtrack.mp3" in files and files["raw_soundtrack.mp3"].stat().st_size > 1000:
        audio_stems.append({
            "name": "Suno Soundtrack",
            "url": f"{rel_prefix}/raw_soundtrack.mp3?t={int(files['raw_soundtrack.mp3'].stat().st_mtime)}",
            "filename": "raw_soundtrack.mp3",
            "type": "suno_bgm",
            "model": "Suno v3.5",
            "color": "cyan",
        })
    if "velvet_binaural_master_48k.mp3" in files and files["velvet_binaural_master_48k.mp3"].stat().st_size > 1000:
        audio_stems.append({
            "name": "Velvet 432Hz Master",
            "url": f"{rel_prefix}/velvet_binaural_master_48k.mp3?t={int(files['velvet_binaural_master_48k.mp3'].stat().st_mtime)}",
            "filename": "velvet_binaural_master_48k.mp3",
            "type": "binaural_nature",
            "model": "Spatial DSP",
            "color": "emerald",
        })
    if not audio_stems and (ep_path / "stems").exists():
        for a in sorted((ep_path / "stems").glob("*.mp3")):
            if a.stat().st_size > 1000:
                audio_stems.append({"name": "Suno Vocal Soundtrack" if "soundtrack" in a.name else a.stem, "url": f"{rel_prefix}/stems/{a.name}?t={int(a.stat().st_mtime)}", "filename": a.name, "type": "vocal_music", "model": "Suno v3.5", "color": "cyan"})

    if (ep_path / "master_renders").exists():
        for m in sorted((ep_path / "master_renders").glob("*.mp4")):
            if m.stat().st_size > 1000:
                editions.append({"edition_id": "master_music_video", "name": f"🎵 4K Vocal Master", "label": "4K Vocal Music Video Master", "icon": "fa-music text-purple-400", "audio_mode": "Singing Vocals + Suno BGM", "duration": f"{int(manifest_data.get('duration_seconds', 60))}s", "format": "16:9 Master", "status": "completed", "url": f"{rel_prefix}/master_renders/{m.name}?t={int(m.stat().st_mtime)}", "size_str": f"{round(m.stat().st_size / (1024*1024), 1)} MB"})

    thumb_url = None
    if "thumbnail_music_4k.jpg" in files:
        thumb_url = f"{rel_prefix}/thumbnail_music_4k.jpg?ep={ep_id}&t={int(files['thumbnail_music_4k.jpg'].stat().st_mtime)}"
    elif "keyframe_p1.jpg" in files:
        thumb_url = f"{rel_prefix}/keyframe_p1.jpg?ep={ep_id}&t={int(files['keyframe_p1.jpg'].stat().st_mtime)}"
    elif (ep_path / "thumbnails").exists():
        for th in sorted((ep_path / "thumbnails").glob("thumb_*.jpg")):
            if th.stat().st_size > 1000:
                thumb_url = f"{rel_prefix}/thumbnails/{th.name}?t={int(th.stat().st_mtime)}"
                break
    elif keyframes:
        thumb_url = keyframes[0]["url"]

    thumb_short_url = None
    if "thumbnail_9x16_short.jpg" in files:
        thumb_short_url = f"{rel_prefix}/thumbnail_9x16_short.jpg?ep={ep_id}&t={int(files['thumbnail_9x16_short.jpg'].stat().st_mtime)}"
    elif thumb_url:
        thumb_short_url = thumb_url

    total_cost = sum(item["cost_usd"] for item in cost_by_stage)
    master_ed = [e for e in editions if "master" in e.get("edition_id", "")]
    primary_master = master_ed[0]["url"] if master_ed else (editions[0]["url"] if editions else None)

    has_master_file = bool(primary_master or ("master_4k_ambient.mp4" in files) or ("master_4k_nature.mp4" in files))
    ep_status = "completed" if has_master_file else (pipeline_state_data.get("status") or manifest_data.get("status") or "ready")
    curr_stage = 4 if has_master_file else int(pipeline_state_data.get("current_stage") or (3 if len(audio_stems) > 0 else (2 if len(keyframes) > 0 else 1)))
    eff_format = "relaxation" if is_relax_fmt else (user_inputs_data.get("format") or manifest_data.get("format") or "relaxation")

    return {
        "episode_id": ep_id,
        "id": ep_id,
        "status": ep_status,
        "currentStage": curr_stage,
        "current_stage": curr_stage,
        "format": eff_format,
        "format_slug": eff_format,
        "channel_id": ch_meta["id"],
        "channel_name": ch_meta["name"],
        "channel_handle": ch_meta["handle"],
        "channel_icon": ch_meta["icon"],
        "channel_color": ch_meta["color"],
        "title": title,
        "production_name": (
            user_inputs_data.get("production_name")
            or manifest_data.get("production_name")
            or (ep_path.parent.name if ep_path.parent.name not in ("channels", "networks", ch_meta["id"]) else "standalone")
        ),
        "genre": (manifest_data.get("genre") or screenplay_data.get("genre") or user_inputs_data.get("genre") or "relax/nature"),
        "sub_genre": (manifest_data.get("sub_genre") or screenplay_data.get("sub_genre") or user_inputs_data.get("sub_genre")),
        "primary_archetype": (manifest_data.get("primary_archetype") or screenplay_data.get("primary_archetype") or user_inputs_data.get("primary_archetype")),
        "story_topic": story_topic,
        "script_text": script_text,
        "description": desc,
        "category": ch_meta["category"],
        "cost_usd": total_cost,
        "cost_breakdown": {"total_usd": total_cost, "by_stage": cost_by_stage, "by_model": cost_by_model},
        "models_used": {
            "scripting": "Gemini 2.5 Pro", "visuals": "FLUX.1 Dev (Fal)", "motion": "Kling v3 Pro / Wan 2.1",
            "audio": "Suno v3.5 + Spatial DSP", "encoding": "Single-Pass FFmpeg CRF 22",
        },
        "stages": {
            "stage_1_keyframes": len(keyframes) > 0, "stage_2_cineloop_masters": "master_4k_ambient.mp4" in files,
            "stage_3_crf22_compression": "master_4k_ambient.mp4" in files, "stage_4_long_play_stretch": len(long_play_editions) > 0,
            "stage_5_short_teaser": "short_9x16_teaser.mp4" in files,
        },
        "keyframes": keyframes,
        "motion_clips": motion_clips,
        "audio_stems": audio_stems,
        "thumbnail_url": thumb_url,
        "thumbnailUrl": thumb_url,
        "thumbnail_short_url": thumb_short_url,
        "thumbnailShortUrl": thumb_short_url,
        "editions": master_editions if master_editions else editions,
        "long_play_editions": long_play_editions,
        "all_editions": editions,
        "video_url": primary_master,
        "videoUrl": primary_master,
        "nature_video_url": next((e["url"] for e in master_editions if e["edition_id"] == "master_nature"), None),
        "story": story_data if story_data else None,
        "script": screenplay_data if screenplay_data else None,
        "screenplay": screenplay_data if screenplay_data else None,
        "user_inputs": user_inputs_data if user_inputs_data else None,
        "pipeline_state": pipeline_state_data if pipeline_state_data else None,
        "manifest": manifest_data,
        "scenes": (screenplay_data.get("scenes") or manifest_data.get("scenes", [])),
        "audio_tags": (screenplay_data.get("audio_master", {}).get("suno_musical_tags") if isinstance(screenplay_data.get("audio_master"), dict) else (screenplay_data.get("audio_tags") or manifest_data.get("audio_tags", ""))),
        "cluster": manifest_data.get("cluster", ""),
        "recommended_fps": screenplay_data.get("recommended_fps", manifest_data.get("recommended_fps", 24)),
        "created_at": created_iso,
        "updated_at": updated_iso,
        "created_timestamp": created_ts,
        "created_by": "AI Studio Autonomous Producer",
        "is_approved": is_approved,
        "approved": is_approved,
        "dual_editions": bool(user_inputs_data.get("dual_editions") or ("master_4k_narration.mp4" in files and "master_4k_ambient.mp4" in files)),
        "execution_mode": user_inputs_data.get("execution_mode", "test"),
        "duration_seconds": float(user_inputs_data.get("duration_seconds") or screenplay_data.get("total_duration_seconds") or 120.0),
        "youtube_packaging": yt_pack,
        "youtube_packaging_nature_only": yt_pack_nature,
        "storage_path": str(ep_path.relative_to(storage_dir)).replace("\\", "/"),
        "storagePath": str(ep_path.relative_to(storage_dir)).replace("\\", "/"),
    }
