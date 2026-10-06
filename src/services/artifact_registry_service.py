"""Universal Artifact Registry Service.

Maintains canonical artifact records (model, owner, status, local/remote URLs,
and content hashes) within pipeline_state.json to enforce 100% idempotency
and enable instant re-download of missing/deleted files.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from src.core.telemetry import logger


class UniversalArtifactRecord(BaseModel):
    """Canonical tracking record for an individual production artifact."""
    artifact_id: str
    category: str
    scene_index: Optional[int] = None
    model: str
    owner: str
    status: str = "synthesized"
    local_path: str
    local_url: Optional[str] = None
    remote_url: Optional[str] = None
    file_size_bytes: int = 0
    duration_seconds: Optional[float] = None
    resolution: Optional[str] = None
    content_hash: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _load_pipeline_state(ep_dir: Path) -> dict[str, Any]:
    pipe_file = ep_dir / "pipeline_state.json"
    if pipe_file.is_file():
        try:
            return json.loads(pipe_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"artifact_registry_state_read_error: {e}")
    return {}


def _save_pipeline_state(ep_dir: Path, state: dict[str, Any]) -> None:
    pipe_file = ep_dir / "pipeline_state.json"
    try:
        pipe_file.parent.mkdir(parents=True, exist_ok=True)
        pipe_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.warning(f"artifact_registry_state_write_error: {e}")


def register_artifact(ep_dir: Path, record: UniversalArtifactRecord) -> UniversalArtifactRecord:
    """Record an artifact in pipeline_state.json with model, owner, and URLs."""
    state = _load_pipeline_state(ep_dir)
    artifacts = state.setdefault("artifact_registry", {})
    artifacts[record.artifact_id] = record.model_dump()
    state["artifacts"] = list(artifacts.values())
    _save_pipeline_state(ep_dir, state)
    logger.info(f"artifact_registered: id={record.artifact_id} model={record.model} owner={record.owner} status={record.status}")
    return record


def get_artifact(ep_dir: Path, artifact_id: str) -> Optional[UniversalArtifactRecord]:
    """Retrieve an artifact record by ID from pipeline_state.json."""
    state = _load_pipeline_state(ep_dir)
    data = state.get("artifact_registry", {}).get(artifact_id)
    if data:
        try:
            return UniversalArtifactRecord(**data)
        except Exception:
            pass
    return None


def list_artifacts(ep_dir: Path, category: Optional[str] = None) -> List[UniversalArtifactRecord]:
    """List all registered artifacts, optionally filtered by category."""
    state = _load_pipeline_state(ep_dir)
    res = []
    for d in state.get("artifact_registry", {}).values():
        try:
            rec = UniversalArtifactRecord(**d)
            if not category or rec.category == category:
                res.append(rec)
        except Exception:
            continue
    return res


async def resolve_or_download_artifact(
    ep_dir: Path,
    artifact_id: str,
    local_file: Path,
    expected_min_bytes: int = 1000,
) -> Optional[Path]:
    """Universal 4-tier idempotency resolver.

    1. Local Disk: if local_file exists and is valid -> reuse ($0.00).
    2. Remote URL: if local_file is missing but remote_url is recorded in registry -> download ($0.00).
    3. Return None if fresh synthesis is required.
    """
    if local_file.is_file() and local_file.stat().st_size >= expected_min_bytes:
        logger.info(f"artifact_cache_hit_disk: {local_file.name} ({local_file.stat().st_size} B) ($0.00 spend)")
        return local_file

    rec = get_artifact(ep_dir, artifact_id)
    remote_url = rec.remote_url if rec else None

    # Fallback sidecar check (.fal_meta.json) if registry didn't have remote_url
    if not remote_url:
        for cand in (ep_dir / f"{local_file.name}.fal_meta.json", ep_dir / f"raw_diff_{local_file.name}.fal_meta.json"):
            if cand.is_file():
                try:
                    meta_d = json.loads(cand.read_text("utf-8"))
                    remote_url = meta_d.get("video_url") or meta_d.get("remote_url")
                    if remote_url:
                        break
                except Exception:
                    pass

    if remote_url and (remote_url.startswith("http://") or remote_url.startswith("https://")):
        logger.info(f"artifact_cache_hit_remote: re-downloading {local_file.name} from {remote_url} ($0.00 spend)...")
        print(f"[IDEMPOTENCY - REMOTE CDN HIT] Re-downloading {local_file.name} from {remote_url} ($0.00 spend)...")
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0, read=180.0)) as client:
                resp = await client.get(remote_url)
                if resp.status_code == 200 and len(resp.content) >= expected_min_bytes:
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    local_file.write_bytes(resp.content)
                    logger.info(f"artifact_redownload_success: {local_file.name} ({len(resp.content)} B) ($0.00 spend)")
                    if rec:
                        rec.file_size_bytes = len(resp.content)
                        rec.status = "synthesized"
                        register_artifact(ep_dir, rec)
                    return local_file
        except Exception as e:
            logger.warning(f"artifact_redownload_failed: {local_file.name} from {remote_url} error={e}")

    return None
