"""Concert Workspace Resolution & Lifecycle Management.

Finds existing concert episode workspaces or initializes a new organized directory hierarchy:
networks/{network}/music_video/{song_title_slug}/ep-001/
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Optional, Tuple
from uuid import UUID, uuid4

from src.core.config import settings
from src.domain.creative import Episode, Show
from src.domain.repo import repo
from src.domain.user import User


def resolve_concert_workspace(
    episode_id_or_code: str | None,
    network: str,
    user: User,
    title: str | None,
) -> tuple[Path, Episode]:
    """Find existing concert episode workspace or initialize a new one.

    user_inputs.json is the primary deciding factor and contract record for episode identity.
    """
    root = Path(settings.storage.local_storage_root)
    shows = repo.list_shows(user.id)
    show = shows[0] if shows else repo.save_show(Show(user_id=user.id, title=network.replace("_", " ").title(), slug=network))

    if episode_id_or_code:
        target = str(episode_id_or_code).strip()
        # 1. Direct folder path check
        target_path = Path(target)
        if target_path.is_dir() and (target_path / "user_inputs.json").is_file():
            return _load_workspace_episode(target_path, target, show, user, title)

        # 2. Check repo for episode metadata if UUID
        target_uuid = None
        try:
            if len(target) == 36:
                target_uuid = UUID(target)
        except Exception:
            target_uuid = None
        repo_ep = repo.get_episode(user.id, target_uuid) if target_uuid else None

        search_roots = [root / user.storage_container_name, root]
        matches = []
        for s_root in [r for r in search_roots if r.exists()]:
            # Step A: Check folder path matching target directly
            candidates = [
                m for m in (
                    list(s_root.glob(f"**/{target}/user_inputs.json"))
                    + list(s_root.glob(f"**/{target}/**/user_inputs.json"))
                ) if "-old" not in str(m) and "-bak" not in str(m)
            ]

            # Step B: Primary Deciding Factor - Scan user_inputs.json files for episode_id
            if not candidates:
                for u_cand in s_root.glob("**/user_inputs.json"):
                    if "-old" in str(u_cand) or "-bak" in str(u_cand):
                        continue
                    try:
                        u_data = json.loads(u_cand.read_text(encoding="utf-8"))
                        ep_id_in_u = str(u_data.get("episode_id") or u_data.get("id") or "").strip().lower()
                        if ep_id_in_u and ep_id_in_u == target.lower():
                            candidates.append(u_cand)
                    except Exception:
                        pass

            # Step C: Fallback to storyboards / screenplays if not yet matched
            if not candidates:
                for cand in (
                    list(s_root.glob(f"**/{target}/storyboard.json"))
                    + list(s_root.glob("**/music_video/**/storyboard.json"))
                    + list(s_root.glob("**/music_video/**/song_screenplay.json"))
                ):
                    if "-old" in str(cand) or "-bak" in str(cand):
                        continue
                    try:
                        text = cand.read_text(encoding="utf-8", errors="ignore")
                        if target.lower() in text.lower():
                            candidates.append(cand)
                    except Exception:
                        pass

            if candidates:
                if title:
                    t_clean = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower()).strip("_")
                    candidates = [m for m in candidates if t_clean in str(m).lower()] or candidates
                candidates.sort(key=lambda m: m.stat().st_mtime if m.exists() else 0, reverse=True)
                matches = candidates
                break

        if matches:
            ep_dir = matches[0].parent
            return _load_workspace_episode(ep_dir, target, show, user, title, repo_ep=repo_ep)
        raise FileNotFoundError(f"Episode '{target}' not found in storage for user '{user.storage_container_name}'.")

    clean_prod = re.sub(r"[^a-zA-Z0-9]+", "_", (title or "new_concert").lower()).strip("_") or "new_concert"
    prod_dir = root / user.storage_container_name / "networks" / network / "music_video" / clean_prod
    prod_dir.mkdir(parents=True, exist_ok=True)
    existing_eps = [d for d in prod_dir.glob("ep-*") if d.is_dir()]
    ep_num = len(existing_eps) + 1
    ep_ws = prod_dir / f"ep-{ep_num:03d}"
    ep_ws.mkdir(parents=True, exist_ok=True)
    ep = Episode(id=uuid4(), user_id=user.id, show_id=show.id, title=title or "Concert", episode_number=ep_num, duration_seconds=60)
    repo.save_episode(ep)
    return ep_ws, ep


def _load_workspace_episode(
    ep_dir: Path, target: str, show: Show, user: User, title: str | None, repo_ep: Episode | None = None
) -> tuple[Path, Episode]:
    """Helper to load or synthesize Episode object from user_inputs.json and workspace files."""
    u_file = ep_dir / "user_inputs.json"
    s_file = ep_dir / "storyboard.json"
    sc_file = ep_dir / "song_screenplay.json"
    c_file = ep_dir / "concert_directorial_screenplay.json"

    u_data = json.loads(u_file.read_text(encoding="utf-8")) if u_file.is_file() else {}
    s_data = json.loads(s_file.read_text(encoding="utf-8")) if s_file.is_file() else {}
    sc_data = json.loads(sc_file.read_text(encoding="utf-8")) if sc_file.is_file() else {}
    c_data = json.loads(c_file.read_text(encoding="utf-8")) if c_file.is_file() else {}

    ep_id_str = (
        u_data.get("episode_id")
        or u_data.get("id")
        or s_data.get("episode_id")
        or s_data.get("id")
        or sc_data.get("episode_id")
        or sc_data.get("id")
        or (str(repo_ep.id) if repo_ep else target)
    )
    ep_uuid = UUID(ep_id_str) if len(ep_id_str) == 36 else (repo_ep.id if repo_ep else uuid4())
    t_en = (
        u_data.get("title")
        or s_data.get("title_en")
        or sc_data.get("title_en")
        or c_data.get("title_en")
        or (repo_ep.title if repo_ep else None)
        or title
        or "Concert"
    )
    dur = int(u_data.get("duration_seconds") or sc_data.get("duration_seconds") or 60)
    ep = repo.get_episode(user.id, ep_uuid) or repo_ep or Episode(
        id=ep_uuid, user_id=user.id, show_id=show.id, title=t_en, duration_seconds=dur,
    )
    return ep_dir, ep


def restore_concert_workspace_inputs(ep_ws: Path, current_params: dict[str, Any]) -> dict[str, Any]:
    """Restore saved parameters from user_inputs.json, storyboard.json, or screenplay on resumption."""
    u_file = ep_ws / "user_inputs.json"
    sb_file = ep_ws / "storyboard.json"
    sc_file = ep_ws / "song_screenplay.json"
    c_file = ep_ws / "concert_directorial_screenplay.json"
    out = dict(current_params)
    saved: dict[str, Any] = {}
    if u_file.is_file():
        try:
            saved.update(json.loads(u_file.read_text(encoding="utf-8")))
        except Exception:
            pass

    for extra_file in (c_file, sc_file, sb_file):
        if extra_file.is_file():
            try:
                extra_data = json.loads(extra_file.read_text(encoding="utf-8"))
                if not saved.get("title") and extra_data.get("title_en"):
                    saved["title"] = extra_data["title_en"]
                if not saved.get("duration_seconds") and extra_data.get("duration_seconds"):
                    saved["duration_seconds"] = extra_data["duration_seconds"]
                if extra_file == c_file and extra_data.get("broadcast_timeline"):
                    cuts_max = max(float(c.get("end_time", 0.0)) for c in extra_data["broadcast_timeline"])
                    if cuts_max > 0:
                        saved["timeline_duration"] = cuts_max
            except Exception:
                pass

    for k in ("title", "chars", "language", "prompt", "theme", "style", "setting", "venue_type",
              "time_of_day", "stage_setting", "background", "weather", "instrument", "position", "lipsync_model",
              "spatial_3d_engine", "motion_model", "llm_provider", "llm_model"):
        if saved.get(k) and (not out.get(k) or out.get(k) in ("Radha", "te", "mic", "standing", "indoor_stadium", "wav2lip")):
            out[k] = saved[k]
    if saved.get("is_prod"):
        out["is_prod"] = bool(saved["is_prod"])
    if saved.get("is_dj"):
        out["is_dj"] = bool(saved["is_dj"])
    if saved.get("onepass_bytedance") is not None:
        out["onepass_bytedance"] = bool(saved["onepass_bytedance"])
    if saved.get("timeline_duration"):
        out["timeline_duration"] = saved["timeline_duration"]
    if not out.get("duration") and not out.get("duration_seconds"):
        if saved.get("timeline_duration"):
            out["duration_seconds"] = saved["timeline_duration"]
        elif saved.get("duration_seconds") and float(saved["duration_seconds"]) > 10.0:
            out["duration_seconds"] = float(saved["duration_seconds"])
    return out


__all__ = ["resolve_concert_workspace", "restore_concert_workspace_inputs"]
