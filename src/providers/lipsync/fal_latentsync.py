"""Fal.ai LatentSync beat-synchronized lipsync adapter.

Calls ``fal-ai/latentsync`` — beat-synchronized vocal lipsync matching
mouth motion to the Suno music track stem. Falls back to FalLivePortraitAdapter
when the Fal key is absent or LatentSync is unavailable.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import _fal_api_key, upload_to_fal
from src.services.video_4k_encoder import ensure_video_4k


_LATENTSYNC_ENDPOINT = "https://queue.fal.run/fal-ai/latentsync"
_POLL_INTERVAL_S = 3.0
_POLL_MAX_ATTEMPTS = 45   # 135 seconds max


def normalize_lipsync_model(model: str | None) -> str:
    """Normalize lipsync model name to standard slug or local CPU engine."""
    if not model or str(model).lower().strip() in ("local", "wav2lip", "cpu", "default"):
        return "local"
    m = str(model).strip()
    m_lower = m.lower()
    if "sadtalker" in m_lower or "sad-talker" in m_lower:
        if "fal" in m_lower:
            return "fal-ai/sadtalker"
        return "sadtalker"
    if "kling" in m_lower:
        return "fal-ai/kling-video/lipsync/audio-to-video"
    if m_lower in (
        "sync-lipsync/v2", "fal-ai/sync-lipsync/v2", "sync-lipsync-v2",
        "synclipsync-v2", "synclipsync/v2", "sync-v2", "sync2",
        "sync-lipsync", "synclipsync", "fal-ai/sync-lipsync",
    ):
        return "fal-ai/sync-lipsync/v2"
    if m_lower in ("latentsync", "latent-sync", "fal-ai/latentsync"):
        return "fal-ai/latentsync"
    if any(k in m_lower for k in ("bytedance", "omnihuman", "onepass_bytedance", "bytedance_1pass")):
        return "fal-ai/bytedance/omnihuman"
    if not m.startswith("fal-ai/"):
        return f"fal-ai/{m}"
    return m


class FalLatentSyncAdapter:
    """Unified Lip-sync Router supporting Local CPU Wav2Lip, SadTalker, Kling, and SyncLabs."""

    def __init__(self, api_key: str | None = None, default_model: str = "wav2lip") -> None:
        self.api_key = api_key or _fal_api_key()
        self.default_model = default_model

    async def sync_lips(
        self,
        video_path: Path | str,
        audio_path: Path | str,
        output_path: Path | str,
        force_live: bool = False,
        model: str | None = None,
    ) -> Path:
        """Alias for lipsync_video matching standard studio directorial calls."""
        return await self.lipsync_video(
            video_url=str(video_path),
            audio_path=Path(audio_path),
            output_path=output_path,
            force_live=force_live,
            model=model,
        )

    async def lipsync_video(
        self,
        video_url: str | Path,
        audio_path: Path,
        output_path: Path | str,
        force_live: bool = False,
        model: str | None = None,
    ) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        eff_model = normalize_lipsync_model(model or self.default_model)

        # Artifact caching guard (Directive 3)
        if out.exists() and out.stat().st_size > 50_000:
            ensure_video_4k(out)
            logger.info(f"lipsync_cache_hit [model={eff_model}]: {out.name} ({out.stat().st_size} B, 4K)")
            return out

        # 1. Local CPU SadTalker Engine (Default $0.00 spend, head tilt + eye blink + lip sync)
        if eff_model in ("sadtalker", "local_sadtalker"):
            from src.providers.lipsync.local_sadtalker import local_sadtalker_adapter
            return await local_sadtalker_adapter.sync_lips(video_url, audio_path, out, force_live=force_live)

        # 2. Local CPU Wav2Lip Engine ($0.00 spend)
        if eff_model in ("local", "wav2lip"):
            from src.providers.lipsync.local_wav2lip import local_wav2lip_adapter
            return await local_wav2lip_adapter.sync_lips(video_url, audio_path, out, force_live=force_live)

        # 3. Fal Kling LipSync Engine (High-fidelity production, $0.014/cut)
        if "kling" in eff_model:
            from src.providers.lipsync.fal_kling_lipsync import fal_kling_lipsync_adapter
            return await fal_kling_lipsync_adapter.sync_lips(video_url, audio_path, out, force_live=force_live)

        if is_mock_mode() and not force_live:
            return await self._fallback_liveportrait(video_url, audio_path, out)

        if not self.api_key:
            logger.warning("fal_lipsync: no FAL_KEY — falling back to Local CPU Wav2Lip")
            from src.providers.lipsync.local_wav2lip import local_wav2lip_adapter
            return await local_wav2lip_adapter.sync_lips(video_url, audio_path, out, force_live=force_live)

        endpoint = f"https://queue.fal.run/{eff_model}"
        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            try:
                audio_fal_url = str(audio_path) if str(audio_path).startswith("http") else await upload_to_fal(Path(audio_path), self.api_key)
                if "sadtalker" in eff_model:
                    img_src = Path(str(video_url))
                    import cv2
                    if img_src.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm") and img_src.is_file():
                        cap = cv2.VideoCapture(str(img_src))
                        ret, frame = cap.read()
                        cap.release()
                        frame_path = img_src.parent / f"{img_src.stem}_frame0.jpg"
                        if ret and frame is not None:
                            cv2.imwrite(str(frame_path), frame)
                            img_src = frame_path
                    if img_src.is_file():
                        raw_img = cv2.imread(str(img_src))
                        if raw_img is not None:
                            try:
                                from src.scripts.local_perspective_drone import detect_lead_face_center
                                center = detect_lead_face_center(raw_img)
                                if center is not None:
                                    cx, cy = center
                                    ih, iw = raw_img.shape[:2]
                                    box_sz = int(ih * 0.45)
                                    x1, y1 = max(0, cx - box_sz // 2), max(0, cy - int(box_sz * 0.4))
                                    x2, y2 = min(iw, x1 + box_sz), min(ih, y1 + box_sz)
                                    crop = raw_img[y1:y2, x1:x2]
                                    if crop.size > 0:
                                        crop_p = img_src.parent / f"{img_src.stem}_sadtalker_crop.jpg"
                                        cv2.imwrite(str(crop_p), crop)
                                        img_src = crop_p
                            except Exception: pass
                    img_fal_url = str(img_src) if str(img_src).startswith("http") else await upload_to_fal(img_src, self.api_key)
                    payload = {"source_image_url": img_fal_url, "driven_audio_url": audio_fal_url, "still": True, "enhancer": "gfpgan", "preprocess": "crop"}
                else:
                    vid_fal_url = str(video_url) if str(video_url).startswith("http") else await upload_to_fal(Path(video_url), self.api_key)
                    payload = {"video_url": vid_fal_url, "audio_url": audio_fal_url}
                    if "sync-lipsync" in eff_model:
                        payload["sync_mode"] = "cut_off"

                logger.info(f"fal_lipsync_submit: model={eff_model} video={out.name}")
                sub_resp = await client.post(endpoint, headers=headers, json=payload)
                if sub_resp.status_code not in (200, 201):
                    raise RuntimeError(f"Lipsync [{eff_model}] submit failed: {sub_resp.text[:200]}")
                sub_data = sub_resp.json()
                status_url: str = sub_data["status_url"]
                response_url: str = sub_data["response_url"]

                for attempt in range(_POLL_MAX_ATTEMPTS):
                    await asyncio.sleep(_POLL_INTERVAL_S)
                    s = (await client.get(status_url, headers=headers)).json()
                    status = s.get("status")
                    if status == "COMPLETED":
                        r = (await client.get(response_url, headers=headers)).json()
                        res_url: str = r.get("video", {}).get("url", "")
                        if not res_url:
                            if "face" in str(r).lower() and "sync-lipsync" not in eff_model:
                                logger.warning(f"fal_latentsync_face_error: falling back to fal-ai/sync-lipsync/v2 for {out.name}")
                                return await self.lipsync_video(video_url, audio_path, output_path, force_live=force_live, model="fal-ai/sync-lipsync/v2")
                            raise RuntimeError(f"Lipsync [{eff_model}] response missing video URL: {r}")
                        v_bytes = (await client.get(res_url, timeout=60.0)).content
                        out.write_bytes(v_bytes)
                        ensure_video_4k(out)
                        logger.info(f"fal_lipsync_ok [model={eff_model}]: {out.name} ({out.stat().st_size} B, 4K)")
                        return out
                    if status in ("FAILED", "CANCELLED"):
                        raise RuntimeError(f"Lipsync [{eff_model}] task failed: {s}")
                    if attempt % 3 == 0:
                        logger.info(f"fal_lipsync_poll [model={eff_model}]: status={status} ({attempt * _POLL_INTERVAL_S:.0f}s)")

            except Exception as ex:
                logger.error(f"fal_lipsync_error [model={eff_model}]: {ex}")
                raise

    async def _fallback_liveportrait(
        self,
        video_url: str | Path,
        audio_path: Path,
        out: Path,
    ) -> Path:
        """Fallback: local video passthrough in mock mode or raw Kling video download."""
        v_path = Path(str(video_url))
        if v_path.is_file() and v_path.stat().st_size > 1000:
            import shutil
            shutil.copy2(v_path, out)
            ensure_video_4k(out)
            logger.info(f"lipsync_mock_passthrough: {out.name} ({out.stat().st_size} B, 4K)")
            return out
        if str(video_url).startswith("http") and "fal" in str(video_url):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.get(str(video_url), timeout=60.0)
                    if resp.status_code == 200 and len(resp.content) > 10_000:
                        out.write_bytes(resp.content)
                        ensure_video_4k(out)
                        logger.info(f"latentsync_fallback_raw_kling: {out.name} (4K)")
                        return out
            except Exception as ex:
                logger.warning(f"latentsync_raw_download_failed: {ex}")
        from src.providers.lipsync.fal_liveportrait import FalLivePortraitAdapter
        adapter = FalLivePortraitAdapter()
        placeholder = out.parent / "lipsync_placeholder_frame.jpg"
        if not placeholder.exists():
            placeholder.write_bytes(b"")
        return await adapter.animate_avatar(placeholder, audio_path, out)


fal_latentsync_adapter = FalLatentSyncAdapter()

__all__ = ["FalLatentSyncAdapter", "fal_latentsync_adapter", "normalize_lipsync_model"]
