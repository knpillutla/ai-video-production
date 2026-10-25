"""Fal.ai Z-Image Turbo LoRA Trainer and Inference Adapter.

Supports:
1. Training custom character LoRAs on Z-Image Turbo via fal-ai/z-image-trainer (~$0.80-$1.20)
2. Ultra-fast sub-second scene generation via fal-ai/z-image/turbo/lora ($0.005/image)
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
import httpx

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import upload_to_fal, _fal_api_key
from src.services.image_4k_encoder import ensure_image_4k

_TRAIN_ENDPOINT = "https://queue.fal.run/fal-ai/z-image-trainer"
_INFER_ENDPOINT = "https://fal.run/fal-ai/z-image/turbo/lora"
_QUEUE_INFER_ENDPOINT = "https://queue.fal.run/fal-ai/z-image/turbo/lora"
_POLL_INTERVAL_S = 5.0
_MAX_TRAIN_POLLS = 600  # ~3000 seconds max (50 minutes)
_MAX_INFER_POLLS = 40


class FalZImageLoraAdapter:
    """Specialized adapter for training and generating with custom Z-Image LoRAs."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()

    async def train_portrait_lora(
        self,
        images_zip_path: Path | str,
        trigger_word: str,
        output_meta_path: Path | str,
        steps: int = 1500,
    ) -> str:
        """Upload dataset zip and train a character LoRA for Z-Image Turbo."""
        out_meta = Path(output_meta_path)
        out_meta.parent.mkdir(parents=True, exist_ok=True)

        if out_meta.exists():
            data = json.loads(out_meta.read_text(encoding="utf-8"))
            lora_url = data.get("diffusers_lora_file", {}).get("url") or data.get("lora_url")
            if lora_url and not (data.get("mock") and not is_mock_mode()):
                logger.info(f"zimage_lora_train_cache_hit: reusing existing LoRA {lora_url}")
                return lora_url

        if is_mock_mode() or not self.api_key:
            mock_url = f"https://fal.media/files/mock_zimage_lora_{trigger_word}.safetensors"
            out_meta.write_text(json.dumps({"lora_url": mock_url, "base_model": "z-image", "mock": True}), encoding="utf-8")
            return mock_url

        zip_path = Path(images_zip_path)
        dataset_url = await upload_to_fal(zip_path, self.api_key)

        job_sidecar = out_meta.with_suffix(".job.json")
        status_url, response_url = None, None
        if job_sidecar.exists():
            try:
                jdata = json.loads(job_sidecar.read_text(encoding="utf-8"))
                status_url, response_url = jdata.get("status_url"), jdata.get("response_url")
            except Exception:
                status_url, response_url = None, None

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "image_data_url": dataset_url,
            "trigger_word": trigger_word,
            "steps": steps,
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=20.0)) as client:
            if not status_url or not response_url:
                resp = await client.post(_TRAIN_ENDPOINT, headers=headers, json=payload)
                if resp.status_code not in (200, 201):
                    raise RuntimeError(f"Z-Image LoRA training submit failed ({resp.status_code}): {resp.text[:300]}")
                job = resp.json()
                status_url, response_url = job.get("status_url"), job.get("response_url")
                job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")

            t_poll_start = asyncio.get_event_loop().time()
            logger.info(f"zimage_lora_training_queued: trigger={trigger_word}, polling...")
            print(f"\n[~] Z-Image LoRA training queued: trigger={trigger_word}. Monitoring remote training job on Fal.ai...")
            for attempt in range(1, _MAX_TRAIN_POLLS + 1):
                await asyncio.sleep(_POLL_INTERVAL_S)
                try:
                    st_http = await client.get(status_url, headers=headers)
                    if st_http.status_code != 200:
                        logger.warning(f"zimage_lora_poll_warning: HTTP {st_http.status_code}, retrying...")
                        continue
                    st_resp = st_http.json()
                except Exception as ex:
                    logger.warning(f"zimage_lora_poll_network_glitch: {ex}, retrying...")
                    continue

                status = st_resp.get("status")
                elapsed_s = asyncio.get_event_loop().time() - t_poll_start
                queue_pos = st_resp.get("queue_position")
                pos_str = f" (queue pos: {queue_pos})" if queue_pos is not None else ""

                if attempt % 3 == 0 or status in ("COMPLETED", "FAILED", "CANCELLED"):
                    mins, secs = divmod(int(elapsed_s), 60)
                    print(f"    -> [Fal.ai Z-Image Trainer] Status: {status}{pos_str} | Elapsed: {mins}m {secs:02d}s (polling...)")
                    logger.info(f"zimage_lora_training_poll: trigger={trigger_word}, status={status}, elapsed={mins}m{secs:02d}s{pos_str}")

                if status == "COMPLETED":
                    res = (await client.get(response_url, headers=headers)).json()
                    lora_url = (
                        res.get("diffusers_lora_file", {}).get("url")
                        or res.get("output", {}).get("url")
                        or res.get("lora_file", {}).get("url")
                        or res.get("url")
                    )
                    res["base_model"] = "z-image"
                    out_meta.write_text(json.dumps(res, indent=2), encoding="utf-8")
                    if job_sidecar.exists():
                        job_sidecar.unlink(missing_ok=True)
                    mins, secs = divmod(int(elapsed_s), 60)
                    print(f"[+] Z-Image LoRA training SUCCESS in {mins}m {secs:02d}s: {lora_url}\n")
                    logger.info(f"zimage_lora_training_success: {lora_url}")
                    return lora_url
                if status in ("FAILED", "CANCELLED"):
                    if job_sidecar.exists():
                        job_sidecar.unlink(missing_ok=True)
                    raise RuntimeError(f"Z-Image LoRA training failed: {st_resp}")

            raise TimeoutError("Z-Image LoRA training timed out.")

    async def generate_with_lora(
        self,
        prompt: str,
        lora_url: str,
        output_path: Path | str,
        lora_scale: float = 0.82,
        aspect_ratio: str = "16:9",
        seed: int | None = None,
        upscale_4k: bool = True,
        force_live: bool = False,
    ) -> tuple[str, Path]:
        """Generate keyframe using Z-Image Turbo with trained LoRA."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 50_000:
            if upscale_4k:
                await ensure_image_4k(out, aspect_ratio=aspect_ratio, api_key=self.api_key)
            logger.info(f"zimage_lora_cache_hit [model=fal-ai/z-image/turbo/lora]: {out.name}")
            fal_url = await upload_to_fal(out, self.api_key)
            return fal_url, out

        if is_mock_mode() or not self.api_key:
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (1920, 1080), (25, 35, 45))
            draw = ImageDraw.Draw(img)
            draw.text((100, 500), f"[Z-Image LoRA Scene: {prompt[:70]}]", fill=(255, 255, 255))
            img.save(out, format="JPEG", quality=90)
            if upscale_4k:
                await ensure_image_4k(out, aspect_ratio=aspect_ratio, force_live=False, api_key=self.api_key)
            return f"file://{out}", out

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        image_size = {"width": 1080, "height": 1920} if aspect_ratio == "9:16" else {"width": 1920, "height": 1080}
        payload: dict[str, Any] = {
            "prompt": prompt.strip(),
            "image_size": image_size,
            "num_inference_steps": 8,
            "loras": [{"path": lora_url, "scale": lora_scale}],
            "enable_safety_checker": True,
        }
        if seed is not None:
            payload["seed"] = seed

        logger.info(f"generating_image [model=fal-ai/z-image/turbo/lora]: {out.name} (scale={lora_scale})")
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            resp = await client.post(_INFER_ENDPOINT, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                images = data.get("images") or []
                if images and images[0].get("url"):
                    img_bytes = (await client.get(images[0]["url"], timeout=60.0)).content
                    out.write_bytes(img_bytes)
                    if upscale_4k:
                        await ensure_image_4k(out, aspect_ratio=aspect_ratio, force_live=force_live, api_key=self.api_key)
                    return images[0]["url"], out

            # Fallback to queue endpoint if direct timed out
            sub_resp = await client.post(_QUEUE_INFER_ENDPOINT, headers=headers, json=payload)
            if sub_resp.status_code not in (200, 201):
                raise RuntimeError(f"Z-Image LoRA inference failed: {sub_resp.text[:200]}")
            sub_data = sub_resp.json()
            status_url, response_url = sub_data["status_url"], sub_data["response_url"]

            for attempt in range(_MAX_INFER_POLLS):
                await asyncio.sleep(_POLL_INTERVAL_S)
                st = (await client.get(status_url, headers=headers)).json()
                if st.get("status") == "COMPLETED":
                    res = (await client.get(response_url, headers=headers)).json()
                    img_bytes = (await client.get(res["images"][0]["url"], timeout=60.0)).content
                    out.write_bytes(img_bytes)
                    if upscale_4k:
                        await ensure_image_4k(out, aspect_ratio=aspect_ratio, force_live=force_live, api_key=self.api_key)
                    return res["images"][0]["url"], out
                if st.get("status") in ("FAILED", "CANCELLED"):
                    raise RuntimeError(f"Z-Image LoRA generation failed: {st}")

            raise TimeoutError("Z-Image LoRA generation timed out.")


fal_zimage_lora_adapter = FalZImageLoraAdapter()

__all__ = ["FalZImageLoraAdapter", "fal_zimage_lora_adapter"]
