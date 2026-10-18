"""Base Abstract Pipeline for Broadcast 4K Music & Dance Videos.

Provides universal artifact caching, retry backoffs, directory structures,
and state persistence for all specialized music video pipelines.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional

from src.core.storage import storage_service
from src.core.telemetry import logger


class BaseMusicVideoPipeline:
    """Foundational pipeline providing shared caching, persistence, and retry facilities."""

    pipeline_type: str = "base_music"

    def __init__(
        self,
        user_id: str,
        channel_id: str,
        episode_id: str,
        production_name: str = "standalone",
    ):
        self.user_id = user_id or "user_krishna_01"
        self.channel_id = channel_id or "default_channel"
        self.episode_id = episode_id or "EP-001"
        self.production_name = production_name or "standalone"
        self.ep_dir = storage_service.get_channel_format_production_episode_path(
            self.user_id, self.channel_id, "music_video", self.production_name, self.episode_id
        )
        self.ep_dir.mkdir(parents=True, exist_ok=True)
        self.scenes_dir = self.ep_dir / "scenes"
        self.stems_dir = self.ep_dir / "stems"
        self.renders_dir = self.ep_dir / "master_renders"
        self.sub_dir = self.ep_dir / "subtitles"
        self.thumb_dir = self.ep_dir / "thumbnails"
        for d in (self.scenes_dir, self.stems_dir, self.renders_dir, self.sub_dir, self.thumb_dir):
            d.mkdir(parents=True, exist_ok=True)

    def _file_url(self, file_path: Path) -> str:
        """Construct client-accessible static URL with bust timestamp."""
        try:
            mtime = int(file_path.stat().st_mtime) if file_path.exists() else int(time.time())
            rel = file_path.resolve().relative_to(storage_service.root_dir.resolve())
            return f"/storage/{str(rel).replace('\\', '/')}?t={mtime}"
        except Exception:
            p_str = str(file_path.resolve()).replace("\\", "/")
            mtime = int(file_path.stat().st_mtime) if file_path.exists() else int(time.time())
            return f"/storage/{p_str.split('/storage/', 1)[1]}?t={mtime}" if "/storage/" in p_str else f"/storage/{file_path.name}?t={mtime}"

    # Universal Artifact Caching (Rule 3)
    def is_script_cached(self) -> bool:
        sb = self.ep_dir / "storyboard.json"
        return sb.is_file() and sb.stat().st_size > 100

    def is_keyframes_cached(self, min_count: int = 1) -> bool:
        imgs = [p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000]
        return len(imgs) >= max(1, min_count)

    def is_audio_cached(self) -> bool:
        a = self.stems_dir / "raw_soundtrack.mp3"
        return a.is_file() and a.stat().st_size > 1000

    def is_master_cached(self) -> bool:
        vids = [p for p in self.renders_dir.glob("master_*.mp4") if p.stat().st_size > 1000]
        return len(vids) > 0

    # Safe Retries with Exponential Backoff
    async def with_retries(self, action_name: str, coro_fn: Callable[[], Coroutine[Any, Any, Any]], max_retries: int = 3, delay: float = 1.0) -> Any:
        last_exc: Optional[Exception] = None
        for attempt in range(1, max_retries + 1):
            try:
                return await coro_fn()
            except Exception as exc:
                last_exc = exc
                logger.warning(f"music_pipeline_retry: action='{action_name}' attempt={attempt}/{max_retries} err='{exc}'")
                if attempt < max_retries:
                    await asyncio.sleep(delay * (2 ** (attempt - 1)))
        raise RuntimeError(f"Action '{action_name}' failed after {max_retries} attempts: {last_exc}") from last_exc

    # Disk Metadata Persistence
    def _save_user_inputs(self, inputs: dict[str, Any]) -> None:
        payload = {**inputs, "pipeline_type": self.pipeline_type, "timestamp": time.time()}
        (self.ep_dir / "user_inputs.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _save_manifest(self, sb_data: dict[str, Any], dur: float, lang: str, country: str, genre: str) -> None:
        manifest = {
            "episode_id": self.episode_id, "channel_id": self.channel_id, "format": "music_video",
            "pipeline_type": self.pipeline_type, "genre": genre,
            "title": sb_data.get("title_en") or "Music Video",
            "title_localized": sb_data.get("title_localized") or "",
            "prompt": sb_data.get("hook_thesis") or sb_data.get("title_en") or "",
            "duration_seconds": dur, "language": lang, "country": country,
        }
        (self.ep_dir / "episode_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _save_pipeline_state(self, stage: int, status: str = "ready") -> None:
        state = {
            "episode_id": self.episode_id, "channel_id": self.channel_id, "format": "music_video",
            "pipeline_type": self.pipeline_type, "current_stage": stage, "stage_status": status,
            "is_approved": False,
            "stage_approvals": {
                "script": stage >= 1, "keyframes": stage >= 2, "audio": stage >= 3, "motion": stage >= 4, "master": stage >= 5,
            },
        }
        (self.ep_dir / "pipeline_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _make_response(
        self, sb_data: dict[str, Any], stage: int, kfs: list[dict[str, Any]], stems: list[dict[str, Any]],
        v_url: Optional[str], t0: float, dur: float, artifacts: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        self._save_pipeline_state(stage, "completed" if stage >= 5 else "ready")
        title = sb_data.get("title_en") or "Music Video"
        arts = artifacts or ([{"name": Path(v_url).name, "url": v_url}] if v_url else [])
        return {
            "success": True, "job_id": f"job_{self.episode_id.lower()}", "episode_id": self.episode_id,
            "title": title, "script": sb_data, "video_url": v_url, "storage_path": str(self.ep_dir),
            "duration_seconds": dur, "render_time_seconds": round(time.time() - t0, 2),
            "keyframes": kfs, "audio_stems": stems, "motion_clips": [], "current_stage": stage, "stage": stage,
            "artifacts": arts, "pipeline_type": self.pipeline_type,
        }
