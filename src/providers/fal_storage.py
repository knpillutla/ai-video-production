"""Shared Fal.ai Storage Upload Utility.

Converts local media files (images, audio, video) to remote Fal CDN URLs
required by all Fal queue-based APIs (FLUX.1-dev, Kling, LatentSync).
"""

from pathlib import Path
import httpx

from src.core.config import settings
from src.core.telemetry import logger


def _fal_api_key() -> str:
    """Resolve Fal API key from settings or environment."""
    key = (
        getattr(settings.video, "fal_key", None)
        or getattr(settings.video, "fal_api_key", None)
        or ""
    )
    if not key:
        import os
        key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY") or ""
    return key


async def upload_to_fal(file_path: Path, api_key: str = "") -> str:
    """Upload a local media file to Fal CDN storage and return the remote URL.

    Args:
        file_path: Local path to the file (image, audio, or video).
        api_key:   Fal API key; resolved from settings if omitted.

    Returns:
        Remote Fal CDN URL string (``fal.media/files/...``).

    Raises:
        RuntimeError: If initiate or upload PUT step fails.
    """
    key = api_key or _fal_api_key()
    if not key:
        raise RuntimeError("FAL_KEY is not set — cannot upload to Fal storage.")

    # Universal Artifact Caching Guard (Directive 3): Check for existing .fal_url sidecar
    url_sidecar = file_path.with_suffix(file_path.suffix + ".fal_url")
    if url_sidecar.exists():
        cached_url = url_sidecar.read_text(encoding="utf-8").strip()
        if cached_url.startswith("http"):
            logger.info(f"fal_storage_cache_hit: {file_path.name} → {cached_url}")
            return cached_url

    suffix = file_path.suffix.lower()
    mime_map = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime = mime_map.get(suffix, "application/octet-stream")
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=15.0)) as client:
        # Step 1: Initiate upload — get signed PUT URL + file_url
        init_resp = await client.post(
            "https://rest.alpha.fal.ai/storage/upload/initiate",
            headers=headers,
            json={"file_name": file_path.name, "content_type": mime},
        )
        if init_resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Fal upload initiate failed ({init_resp.status_code}): {init_resp.text[:200]}"
            )
        data = init_resp.json()
        upload_url: str = data["upload_url"]
        file_url: str = data["file_url"]

        # Step 2: PUT file bytes to signed URL
        put_resp = await client.put(
            upload_url,
            headers={"Content-Type": mime},
            content=file_path.read_bytes(),
            timeout=120.0,
        )
        if put_resp.status_code not in (200, 201, 204):
            raise RuntimeError(
                f"Fal upload PUT failed ({put_resp.status_code}): {put_resp.text[:200]}"
            )

    try:
        url_sidecar.write_text(file_url, encoding="utf-8")
    except Exception:
        pass
    logger.info(f"fal_storage_upload_ok: {file_path.name} → {file_url}")
    return file_url


__all__ = ["upload_to_fal"]
