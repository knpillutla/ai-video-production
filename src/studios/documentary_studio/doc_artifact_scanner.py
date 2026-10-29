"""Documentary Artifact Scanner.

Discovers and compiles synthesized documentary artifacts (stories, screenplays,
user_inputs, audio stems, keyframes, motion clips, masters, and pipeline state)
from disk into standardized inspection dictionaries.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.storage import storage_service


def scan_documentary_artifacts(
    channel_id: str,
    episode_id: str,
    format_slug: Optional[str] = "documentary",
    production_name: Optional[str] = None,
    user_id: str = "knpillutla@gmail.com",
    format: Optional[str] = None,
) -> Dict[str, Any]:
    """Scans and returns all synthesized documentary artifacts for an episode."""
    eff_fmt = format or format_slug or "documentary"
    c_dir = storage_service.find_episode_path(
        user_id=user_id,
        channel_id=channel_id,
        episode_id=episode_id,
        format_slug=eff_fmt,
        production_name=production_name,
    )
    if not c_dir or not c_dir.exists():
        return {
            "keyframes": [], "motion_clips": [], "audio_stems": [], "video_url": None,
            "stage": 1, "format": "documentary", "status": "ready",
        }

    files = {f.name: f for f in c_dir.iterdir() if f.is_file()}

    def _file_url(f: Path) -> str:
        mtime = int(f.stat().st_mtime) if f.exists() else int(time.time())
        try:
            rel = f.resolve().relative_to(storage_service.root_dir.resolve())
            return f"/storage/{str(rel).replace('\\', '/')}?t={mtime}"
        except Exception:
            return f"/storage/{f.name}?t={mtime}"

    story_data = None
    story_p = c_dir / "raw_gemini_story.json"
    if story_p.exists() and story_p.stat().st_size > 50:
        try:
            story_data = json.loads(story_p.read_text("utf-8"))
        except Exception:
            pass

    sp_data = None
    sp_p = c_dir / "raw_gemini_screenplay.json"
    if sp_p.exists() and sp_p.stat().st_size > 50:
        try:
            sp_data = json.loads(sp_p.read_text("utf-8"))
        except Exception:
            pass

    user_inputs_file = c_dir / "user_inputs.json"
    u_data = json.loads(user_inputs_file.read_text("utf-8")) if user_inputs_file.exists() else None

    gemini_story_inputs_file = c_dir / "gemini_story_inputs.json"
    g_story_inputs = json.loads(gemini_story_inputs_file.read_text("utf-8")) if gemini_story_inputs_file.exists() else None

    gemini_sp_inputs_file = c_dir / "gemini_screenplay_inputs.json"
    g_sp_inputs = json.loads(gemini_sp_inputs_file.read_text("utf-8")) if gemini_sp_inputs_file.exists() else None

    pipe_file = c_dir / "pipeline_state.json"
    pipe_data = json.loads(pipe_file.read_text("utf-8")) if pipe_file.exists() else None

    manifest_file = c_dir / "episode_manifest.json"
    m_data = json.loads(manifest_file.read_text("utf-8")) if manifest_file.exists() else {}

    stems = []
    narr_file = files.get("active_spoken_narration.mp3") or files.get("spoken_narration.mp3")
    if narr_file and narr_file.stat().st_size > 1000:
        stems.append({
            "name": "Neural Broadcast Narration", "filename": narr_file.name,
            "url": _file_url(narr_file), "role": "narration", "stem_type": "narration",
            "type": "azure_speech", "voice_name": "en-GB-RyanNeural", "color": "indigo",
        })
    if "raw_soundtrack.mp3" in files and files["raw_soundtrack.mp3"].stat().st_size > 1000:
        stems.append({
            "name": "Suno Soundtrack", "filename": "raw_soundtrack.mp3",
            "url": _file_url(files["raw_soundtrack.mp3"]), "role": "bgm", "stem_type": "bgm", "color": "cyan",
        })

    kfs = [
        {"name": f"Shot {k.replace('keyframe_p','').replace('.jpg','')}", "url": _file_url(files[k]), "filename": k}
        for k in sorted(files) if k.startswith("keyframe_p") and k.endswith(".jpg") and files[k].stat().st_size > 1000
    ]
    vids = [
        {"name": f"Motion {m.replace('motion_p','').replace('.mp4','')}", "url": _file_url(files[m]), "filename": m}
        for m in sorted(files) if m.startswith("motion_p") and m.endswith(".mp4") and files[m].stat().st_size > 1000
    ]
    master_file = files.get("master_4k_narration.mp4") or files.get("master_4k_documentary.mp4") or files.get("master_4k_final.mp4")
    master_url = _file_url(master_file) if master_file and master_file.stat().st_size > 1000 else None

    eff_stage = pipe_data.get("current_stage", 1) if pipe_data else (
        7 if master_url else (6 if vids else (4 if kfs else (3 if sp_data else (2 if stems else 1))))
    )
    prod_name = (
        (u_data.get("production_name") if u_data else None)
        or (m_data.get("production_name") if m_data else None)
        or (story_data.get("destination_entity") if story_data else None)
        or c_dir.parent.name
    )

    has_story = bool(story_data and (story_data.get("chapters") or story_data.get("title")))
    has_narr = "spoken_narration.mp3" in files and files["spoken_narration.mp3"].stat().st_size > 1000
    has_sp = bool(sp_data and (sp_data.get("scenes") or sp_data.get("chapters")))
    has_kfs = len(kfs) > 0
    has_bgm = "raw_soundtrack.mp3" in files and files["raw_soundtrack.mp3"].stat().st_size > 1000
    has_motion = len(vids) > 0
    has_master = bool(master_url)
    has_short = "short_9x16_teaser.mp4" in files and files["short_9x16_teaser.mp4"].stat().st_size > 1000
    has_pkg = "youtube_packaging.json" in files and files["youtube_packaging.json"].stat().st_size > 100

    if pipe_data:
        stages_comp = pipe_data.setdefault("stages_completed", {})
        stages_comp["story"] = has_story
        stages_comp["narration"] = has_narr
        stages_comp["screenplay"] = has_sp
        stages_comp["keyframes"] = has_kfs
        stages_comp["bgm"] = has_bgm
        stages_comp["motion"] = has_motion
        stages_comp["master"] = has_master
        stages_comp["short"] = has_short
        stages_comp["packaging"] = has_pkg
        stages_comp["script"] = has_sp or has_story
        stages_comp["photos"] = has_kfs
        stages_comp["audio"] = has_narr or has_bgm

        approvals = pipe_data.setdefault("stage_approvals", {})
        for k in ("story", "narration", "screenplay", "keyframes", "bgm", "motion", "master", "short", "packaging"):
            if k not in approvals:
                approvals[k] = stages_comp.get(k, False)

        pipe_data["artifacts"] = sorted(list(files.keys()))
        try:
            pipe_file.write_text(json.dumps(pipe_data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    return {
        "format": "documentary", "format_slug": "documentary", "channel_id": channel_id, "episode_id": episode_id,
        "story": story_data, "screenplay": sp_data, "script": sp_data, "audio_stems": stems, "keyframes": kfs,
        "motion_clips": vids, "video_url": master_url, "current_stage": eff_stage, "currentStage": eff_stage,
        "stage": eff_stage, "status": "completed" if master_url else (pipe_data.get("stage_status") if pipe_data else "ready"),
        "pipeline_state": pipe_data, "manifest": m_data, "user_inputs": u_data,
        "gemini_story_inputs": g_story_inputs, "gemini_screenplay_inputs": g_sp_inputs,
        "gemini_inputs": g_story_inputs, "production_name": prod_name,
    }


__all__ = ["scan_documentary_artifacts"]
