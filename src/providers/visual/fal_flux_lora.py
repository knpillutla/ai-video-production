"""Fal.ai FLUX LoRA Trainer and Inference Adapter.

Supports:
1. Training custom portrait LoRAs via fal-ai/flux-lora-portrait-trainer ($1.50-$2.00)
2. Generating consistent character scenes via fal-ai/flux-lora ($0.035/image)
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
import httpx

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import upload_to_fal, _fal_api_key

_TRAIN_ENDPOINT = "https://queue.fal.run/fal-ai/flux-lora-portrait-trainer"
_INFER_ENDPOINT = "https://queue.fal.run/fal-ai/flux-lora"
_POLL_INTERVAL_S = 5.0
_MAX_TRAIN_POLLS = 250  # 1250 seconds max for training (20 minutes)
_MAX_INFER_POLLS = 60   # 300 seconds max for inference


class FalFluxLoraAdapter:
    """Specialized adapter for training and generating with custom FLUX LoRAs."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()

    async def train_portrait_lora(
        self,
        images_zip_path: Path | str,
        trigger_word: str,
        output_meta_path: Path | str,
        steps: int = 500,
    ) -> str:
        """Upload dataset zip and train a character portrait LoRA.
        
        Returns:
            The remote safetensors URL of the trained LoRA.
        """
        out_meta = Path(output_meta_path)
        out_meta.parent.mkdir(parents=True, exist_ok=True)

        if out_meta.exists():
            data = json.loads(out_meta.read_text(encoding="utf-8"))
            lora_url = data.get("diffusers_lora_file", {}).get("url") or data.get("lora_url")
            if lora_url and not (data.get("mock") and not is_mock_mode()):
                logger.info(f"lora_train_cache_hit: reusing existing LoRA {lora_url}")
                return lora_url

        if is_mock_mode() or not self.api_key:
            mock_url = f"https://fal.media/files/mock_lora_{trigger_word}.safetensors"
            out_meta.write_text(json.dumps({"lora_url": mock_url, "mock": True}), encoding="utf-8")
            return mock_url

        zip_path = Path(images_zip_path)
        dataset_url = await upload_to_fal(zip_path, self.api_key)

        job_sidecar = out_meta.with_suffix(".job.json")
        status_url, response_url = None, None
        if job_sidecar.exists():
            try:
                jdata = json.loads(job_sidecar.read_text(encoding="utf-8"))
                status_url, response_url = jdata.get("status_url"), jdata.get("response_url")
                if status_url and response_url:
                    logger.info(f"lora_train_resume: found in-flight training job, resuming polling...")
            except Exception:
                status_url, response_url = None, None

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "images_data_url": dataset_url,
            "trigger_word": trigger_word,
            "steps": steps,
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=20.0)) as client:
            if not status_url or not response_url:
                resp = await client.post(_TRAIN_ENDPOINT, headers=headers, json=payload)
                if resp.status_code not in (200, 201):
                    raise RuntimeError(f"LoRA training submit failed ({resp.status_code}): {resp.text[:300]}")
                job = resp.json()
                status_url, response_url = job.get("status_url"), job.get("response_url")
                job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")

            logger.info(f"lora_training_queued: trigger={trigger_word}, polling...")
            for attempt in range(_MAX_TRAIN_POLLS):
                await asyncio.sleep(_POLL_INTERVAL_S)
                st_resp = (await client.get(status_url, headers=headers)).json()
                status = st_resp.get("status")
                if status == "COMPLETED":
                    res = (await client.get(response_url, headers=headers)).json()
                    lora_url = res.get("diffusers_lora_file", {}).get("url")
                    out_meta.write_text(json.dumps(res, indent=2), encoding="utf-8")
                    if job_sidecar.exists():
                        job_sidecar.unlink(missing_ok=True)
                    logger.info(f"lora_training_success: {lora_url}")
                    return lora_url
                if status in ("FAILED", "CANCELLED"):
                    if job_sidecar.exists():
                        job_sidecar.unlink(missing_ok=True)
                    raise RuntimeError(f"LoRA training failed: {st_resp}")
                if attempt % 5 == 0:
                    logger.info(f"lora_train_progress: {status} ({attempt * _POLL_INTERVAL_S:.0f}s)")

            raise TimeoutError("LoRA training timed out.")

    async def generate_with_lora(
        self,
        prompt: str,
        lora_url: str,
        output_path: Path | str,
        lora_scale: float = 1.0,
        aspect_ratio: str = "16:9",
        seed: int | None = None,
    ) -> tuple[str, Path]:
        """Generate a consistent character scene using FLUX with the trained LoRA."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 50_000:
            logger.info(f"flux_lora_cache_hit: {out.name}")
            fal_url = await upload_to_fal(out, self.api_key)
            return fal_url, out

        if is_mock_mode() or not self.api_key:
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (1920, 1080), (20, 30, 45))
            draw = ImageDraw.Draw(img)
            draw.text((100, 500), f"[LoRA Scene: {prompt[:70]}]", fill=(255, 255, 255))
            img.save(out, format="JPEG", quality=90)
            return f"file://{out}", out

        job_sidecar = out.with_suffix(out.suffix + ".fal_job.json")
        status_url, response_url = None, None
        if job_sidecar.exists():
            try:
                jdata = json.loads(job_sidecar.read_text(encoding="utf-8"))
                status_url, response_url = jdata.get("status_url"), jdata.get("response_url")
                if status_url and response_url:
                    logger.info(f"flux_lora_resume: found in-flight scene job for {out.name}, resuming polling...")
            except Exception:
                status_url, response_url = None, None

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        image_size = {"width": 1920, "height": 1080} if aspect_ratio == "16:9" else {"width": 1080, "height": 1920}
        payload: dict[str, Any] = {
            "prompt": prompt.strip(),
            "image_size": image_size,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "loras": [{"path": lora_url, "scale": lora_scale}],
            "enable_safety_checker": True,
        }
        if seed is not None:
            payload["seed"] = seed

        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=15.0)) as client:
            if not status_url or not response_url:
                resp = await client.post(_INFER_ENDPOINT, headers=headers, json=payload)
                if resp.status_code not in (200, 201):
                    raise RuntimeError(f"Fal FLUX LoRA submit failed: {resp.text[:300]}")
                job = resp.json()
                status_url, response_url = job["status_url"], job["response_url"]
                job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")

            for attempt in range(_MAX_INFER_POLLS):
                await asyncio.sleep(2.0)
                st_resp = (await client.get(status_url, headers=headers)).json()
                if st_resp.get("status") == "COMPLETED":
                    res = (await client.get(response_url, headers=headers)).json()
                    img_url = res["images"][0]["url"]
                    img_bytes = (await client.get(img_url, timeout=60.0)).content
                    out.write_bytes(img_bytes)
                    if job_sidecar.exists():
                        job_sidecar.unlink(missing_ok=True)
                    logger.info(f"flux_lora_ok: {out.name}")
                    return img_url, out
                if st_resp.get("status") in ("FAILED", "CANCELLED"):
                    if job_sidecar.exists():
                        job_sidecar.unlink(missing_ok=True)
                    raise RuntimeError(f"Fal FLUX LoRA failed: {st_resp}")

            raise TimeoutError("Fal FLUX LoRA inference timed out.")


fal_flux_lora_adapter = FalFluxLoraAdapter()
