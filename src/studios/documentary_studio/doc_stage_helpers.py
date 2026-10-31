"""Helper utilities for documentary stage directory resolution, state persistence, and shot mapping."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.storage import sanitize_container_name, storage_service


def resolve_doc_episode_dir(
    user_id: str,
    channel_id: str,
    episode_id: str,
    production_name: Optional[str] = None,
    req: Any = None,
) -> Path:
    """Locate existing documentary episode directory or derive one under the destination slug."""
    ep_dir = storage_service.find_episode_path(
        user_id=user_id,
        channel_id=channel_id,
        episode_id=episode_id,
        format_slug="documentary",
        production_name=production_name,
    )
    if ep_dir and ep_dir.exists() and any((ep_dir / f).is_file() for f in ("raw_gemini_story.json", "raw_gemini_screenplay.json", "spoken_narration.mp3")):
        sf, ex_dest = ep_dir / "raw_gemini_story.json", None
        if sf.is_file():
            try:
                ex_dest = json.loads(sf.read_text(encoding="utf-8")).get("destination_entity")
            except Exception:
                pass
        if not ex_dest and ep_dir.parent.name not in ("documentary", "networks", "channels", "destination"):
            ex_dest = ep_dir.parent.name.replace("_", " ").title()
        if ex_dest and req is not None:
            setattr(req, "production_name", ex_dest)
            setattr(req, "country", ex_dest)
        return ep_dir

    c_name = sanitize_container_name(user_id) if "@" in user_id else user_id
    dest = (production_name or getattr(req, "country", None) or "").strip()
    if not dest or dest.lower() in ("standalone", "destination") or re.match(r"^ep[-_]?\d+$", dest.lower()):
        from src.studios.documentary_studio.doc_geo_rotation import resolve_autonomous_geo_details
        eff_sub = getattr(req, "sub_genre", None) or "europe_nations"
        eff_arch = getattr(req, "primary_archetype", None) or "countries"
        _, _, _, picked = resolve_autonomous_geo_details(
            eff_sub, eff_arch, user_id=user_id, channel_id=channel_id, custom_prompt=getattr(req, "prompt", None) or dest
        )
        dest = picked or "Norway"
    if req is not None:
        setattr(req, "production_name", dest)
        setattr(req, "country", dest)
    safe_dest = re.sub(r"[^a-zA-Z0-9_-]+", "_", dest.lower()).strip("_") or "destination"
    return storage_service.root_dir / c_name / "networks" / channel_id / "documentary" / safe_dest / episode_id.lower()


def update_doc_pipeline_state(ep_dir: Path, stage_num: int, stage_key: str, status_val: str = "ready") -> None:
    """Persist documentary pipeline_state.json stage completion."""
    state_file = ep_dir / "pipeline_state.json"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.is_file() else {}
    except Exception:
        state = {}
    state["current_stage"] = max(int(state.get("current_stage") or 1), stage_num)
    state["stage_status"] = status_val
    comp = state.setdefault("stages_completed", {})
    app = state.setdefault("stage_approvals", {})
    comp[stage_key] = app[stage_key] = True
    for k, a in (("screenplay", "script"), ("keyframes", "photos"), ("bgm", "audio")):
        if stage_key == k:
            comp[a] = True
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def write_doc_user_inputs(ep_dir: Path, req: Any, dest: str, title: Optional[str] = None) -> Path:
    """Persist user_inputs.json for auditability and parameter traceability."""
    ep_dir.mkdir(parents=True, exist_ok=True)
    ui_path = ep_dir / "user_inputs.json"
    data = {
        "prompt": getattr(req, "prompt", "") or title or f"Documentary: {dest}",
        "production_name": dest,
        "destination": dest,
        "destination_entity": dest,
        "format": "documentary",
        "format_slug": "documentary",
        "title": title or getattr(req, "title", None) or f"{dest}: Sovereign Realm",
        "genre": getattr(req, "genre", "doc/nations"),
        "sub_genre": getattr(req, "sub_genre", "europe_nations"),
        "primary_archetype": getattr(req, "primary_archetype", "countries"),
        "channel_id": getattr(req, "channel_id", "euro_discovery"),
        "episode_id": getattr(req, "episode_id", ep_dir.name),
        "user_id": getattr(req, "user_id", "knpillutla@gmail.com"),
        "duration_seconds": getattr(req, "duration_seconds", 120),
        "tier": getattr(req, "tier", "balanced"),
        "execution_mode": getattr(req, "execution_mode", "test"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ui_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return ui_path


def load_screenplay_or_raise(ep_dir: Path) -> Dict[str, Any]:
    """Load raw_gemini_screenplay.json from episode directory or raise RuntimeError."""
    sp = ep_dir / "raw_gemini_screenplay.json"
    if not sp.is_file():
        raise RuntimeError(f"Screenplay raw_gemini_screenplay.json not found in {ep_dir.name}. Run Stage 3 first.")
    return json.loads(sp.read_text(encoding="utf-8"))


def select_shots_within_user_duration(
    sp_data: Dict[str, Any], ep_dir: Path, req: Any = None
) -> List[Tuple[int, Dict[str, Any], Dict[str, Any]]]:
    """Read (seq_num, chapter, shot) tuples from chapters[].shots fitting requested duration."""
    req_d = getattr(req, "duration_seconds", None)
    max_dur = float(req_d) if (req_d is not None and float(req_d) > 0) else None
    ui_f = ep_dir / "user_inputs.json"
    if ui_f.is_file():
        try:
            ui = json.loads(ui_f.read_text(encoding="utf-8"))
            raw_d = ui.get("duration_seconds") if ui.get("duration_seconds") is not None else (ui.get("requested_duration_seconds") or ui.get("duration_secs"))
            if raw_d is not None and float(raw_d) > 0:
                max_dur = float(raw_d)
        except Exception:
            pass
    selected, elapsed, seq_num = [], 0.0, 1
    for ch in sp_data.get("chapters") or []:
        for shot in ch.get("shots") or []:
            dur = float(shot.get("duration_seconds") or 6.0)
            if max_dur and max_dur > 0 and selected and (elapsed + dur) > max_dur:
                return selected
            selected.append((seq_num, ch, shot))
            elapsed += dur
            seq_num += 1
    return selected

