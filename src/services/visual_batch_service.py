"""Unified Visual Media Batch Rendering Service.

Encapsulates 100% of Keyframe Image and AI Video Diffusion batching, universal disk caching,
dynamic model routing, concurrent Fal.ai queue execution, and single-pass 4K Lanczos scaling.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
from typing import List, Optional, Tuple

import imageio_ffmpeg
from src.core.telemetry import logger
from src.providers.dance.fal_hunyuan import FalHunyuanAdapter
from src.providers.dance.fal_kling import FalKlingAdapter
from src.providers.fal_storage import _fal_api_key
from src.providers.visual.fal_flux_dev import FalFluxDevAdapter
from src.providers.visual.fal_flux_pro_ultra import FalFluxProUltraAdapter
from src.providers.visual.fal_kling_v3 import FalKlingV3Adapter
from src.providers.visual.fal_wan21 import FalWan21Adapter
from src.providers.visual.fal_zimage import FalZImageAdapter


@dataclass
class MotionClipTask:
    """Specification for an AI video diffusion motion clip task."""
    image_path: Path
    motion_prompt: str
    visual_prompt: str
    output_path: Path
    duration_seconds: float = 30.0
    model: str = "auto"
    domain: str = "water_fluid"
    req_file: Optional[Path] = None
    allow_fallback: bool = False
    force_rerun: bool = False
    negative_prompt: Optional[str] = None
    model_configs: Optional[dict[str, Any]] = None


def resolve_motion_model(model: str, prompt_context: str, total_shots: int = 4) -> tuple[str, str]:
    """Dynamically route to optimal AI video diffusion model with directorial rationale."""
    m_clean = (model or "").lower()
    if m_clean in ("wan_4k", "wan_super_res", "wan_upscale"):
        return "wan_4k", "Alibaba Wan 2.1 (1080p) + AI 4K Super-Resolution selected for true 4K high-fidelity living wallpaper"
    if m_clean in ("wan", "wan_2_1", "wan21"):
        return "wan", "Alibaba Wan 2.1 cost-effective motion diffusion selected for fluid landscapes"
    if m_clean in ("kling_pro", "kling_v1_6_pro", "kling_v1_5_pro", "kling_1_6", "kling_1_5", "kling"):
        return "kling_pro", "Kling 1.6 Pro selected for flagship high-coherence video diffusion"
    if m_clean in ("kling_v3", "kling_4k", "kling_v3_4k"):
        return "kling_v3", "Kling v3 4K Native selected for native 4K UHD video diffusion"
    if m_clean in ("hunyuan", "lanczos"):
        return m_clean, f"Direct configuration override ({model})"
    if total_shots <= 5:
        return "kling_v3", f"Kling v3 4K Native selected as default for <=5 shots ({total_shots} shots) for native 4K UHD OLED fidelity"
    p = prompt_context.lower()
    if any(k in p for k in ("fire", "flame", "ember", "hearth", "waterfall", "rapids", "cascade", "chimney")):
        return "kling_v3", "Kling v3 4K Native selected for high volumetric momentum, dynamic fire embers, and fluid splash plumes"
    return "wan_4k", "Alibaba Wan 2.1 + AI 4K Super-Resolution selected for fluid landscapes"


def _is_clip_4k(video_path: Path) -> bool:
    """Check if video file has 4K UHD dimensions (width >= 3840 and height >= 2160)."""
    try:
        import re
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_bin, "-i", str(video_path)], capture_output=True, text=True, errors="ignore")
        match = re.search(r"(\d{3,4})x(\d{3,4})", res.stderr)
        if match:
            w, h = int(match.group(1)), int(match.group(2))
            return w >= 3840 and h >= 2160
    except Exception:
        pass
    return False


class VisualBatchService:
    """Universal batch rendering utility for keyframes and AI video diffusion."""

    def __init__(self, fal_key: Optional[str] = None):
        self._fal_key = fal_key or ""

    @property
    def fal_key(self) -> str:
        return self._fal_key or _fal_api_key()

    @fal_key.setter
    def fal_key(self, value: Optional[str]) -> None:
        self._fal_key = value or ""

    async def render_keyframes_batch(
        self,
        tasks: List[Tuple[str, Path, Optional[Path], int]],
        aspect_ratio: str = "16:9",
        force_rerun: bool = False,
        image_model: str = "flux_dev",
    ) -> List[Path]:
        """Render batch of keyframes concurrently with disk caching and dynamic image model routing."""
        async def _process_single_keyframe(prompt: str, out_path: Path, req_file: Optional[Path], idx: int) -> Path:
            if not force_rerun and out_path.is_file() and out_path.stat().st_size > 1000:
                logger.info(f"decision_keyframe_cache_hit: Shot {idx} reusing {out_path.name} ($0.00 spend)")
                print(f"[DECISION - KEYFRAME CACHE HIT] Shot {idx} exists on disk ({out_path.name}). Reusing image ($0.00 spend).")
                return out_path

            if force_rerun:
                out_path.unlink(missing_ok=True)
                if req_file and req_file.exists():
                    req_file.unlink(missing_ok=True)

            model_str = (image_model or "flux_dev").lower()
            if "zimage" in model_str or "z_image" in model_str:
                adapter = FalZImageAdapter(api_key=self.fal_key)
                model_display = "Z-Image Turbo"
            elif "pro" in model_str or "ultra" in model_str:
                adapter = FalFluxProUltraAdapter(api_key=self.fal_key)
                model_display = "FLUX 1.1 Pro Ultra"
            else:
                adapter = FalFluxDevAdapter(api_key=self.fal_key)
                model_display = "FLUX.1-dev"

            logger.info(f"decision_keyframe_invoke: Shot {idx} cache miss (or force_rerun). Synthesizing via {model_display}...")
            print(f"[DECISION - KEYFRAME SYNTHESIS] Shot {idx} synthesizing via {model_display} concurrently...")
            await adapter.generate_to_file(prompt=prompt, output_path=out_path, aspect_ratio=aspect_ratio, force_live=bool(self.fal_key))
            return out_path

        return list(await asyncio.gather(*[_process_single_keyframe(p, out, req, idx) for p, out, req, idx in tasks]))

    async def render_thumbnails_batch(
        self,
        tasks: List[Tuple[str, Path, str]],
        force_rerun: bool = False,
        image_model: str = "flux_dev",
    ) -> List[Path]:
        """Render batch of YouTube SEO thumbnails (16:9 Long-Play and 9:16 Vertical Shorts) concurrently with disk caching."""
        async def _process_single_thumbnail(prompt: str, out_path: Path, aspect_ratio: str) -> Path:
            if not force_rerun and out_path.is_file() and out_path.stat().st_size > 1000:
                logger.info(f"decision_thumbnail_cache_hit: Reusing {out_path.name} ($0.00 spend)")
                print(f"[DECISION - THUMBNAIL CACHE HIT] Thumbnail {out_path.name} exists on disk. Reusing image ($0.00 spend).")
                return out_path

            if force_rerun:
                out_path.unlink(missing_ok=True)

            model_str = (image_model or "flux_dev").lower()
            if "zimage" in model_str or "z_image" in model_str:
                adapter = FalZImageAdapter(api_key=self.fal_key)
                model_display = "Z-Image Turbo"
            elif "pro" in model_str or "ultra" in model_str:
                adapter = FalFluxProUltraAdapter(api_key=self.fal_key)
                model_display = "FLUX 1.1 Pro Ultra"
            else:
                adapter = FalFluxDevAdapter(api_key=self.fal_key)
                model_display = "FLUX.1-dev"

            logger.info(f"decision_thumbnail_invoke: Synthesizing {out_path.name} ({aspect_ratio}) via {model_display}...")
            print(f"[DECISION - THUMBNAIL SYNTHESIS] Synthesizing SEO thumbnail {out_path.name} ({aspect_ratio}) via {model_display}...")
            await adapter.generate_to_file(prompt=prompt, output_path=out_path, aspect_ratio=aspect_ratio, force_live=bool(self.fal_key))
            return out_path

        return list(await asyncio.gather(*[_process_single_thumbnail(p, out, ar) for p, out, ar in tasks]))

    async def render_motion_batch(
        self,
        tasks: List[MotionClipTask],
    ) -> List[Path]:
        """Render batch of AI video diffusion clips concurrently with dynamic routing and 4K scaling."""
        total_shots = len(tasks)

        async def _process_single_motion(task: MotionClipTask) -> Path:
            if not task.force_rerun and task.output_path.is_file() and task.output_path.stat().st_size > 1000:
                logger.info(f"decision_motion_cache_hit: Reusing {task.output_path.name} ($0.00 spend)")
                print(f"[DECISION - MOTION CACHE HIT] Clip {task.output_path.name} exists on disk. Reusing asset ($0.00 spend).")
                return task.output_path

            if task.force_rerun:
                task.output_path.unlink(missing_ok=True)
                raw_diff = task.output_path.parent / f"raw_diff_{task.output_path.name}"
                raw_diff.unlink(missing_ok=True)
                if task.req_file and task.req_file.exists():
                    task.req_file.unlink(missing_ok=True)

            chosen_model, rationale = resolve_motion_model(task.model, f"{task.visual_prompt} {task.motion_prompt}", total_shots=total_shots)
            logger.info(f"decision_motion_routing: {task.output_path.name} -> {chosen_model.upper()} ({rationale})")
            print(f"[DECISION - MOTION ROUTING] {task.output_path.name} -> {chosen_model.upper()} ({rationale})")

            eff_prompt = task.motion_prompt
            eff_neg = task.negative_prompt
            eff_settings: dict[str, Any] = {}
            if task.model_configs and isinstance(task.model_configs, dict):
                m_key = "wan_2_1" if chosen_model == "wan" else ("kling_v1_6_pro" if chosen_model in ("kling", "kling_v3", "kling_4k") else chosen_model)
                m_cfg = task.model_configs.get(m_key) or task.model_configs.get(chosen_model)
                if m_cfg:
                    prompts = m_cfg.get("prompts") if isinstance(m_cfg, dict) else getattr(m_cfg, "prompts", None)
                    settings = m_cfg.get("settings") if isinstance(m_cfg, dict) else getattr(m_cfg, "settings", {})
                    if prompts:
                        p_pos = prompts.get("positive_prompt") if isinstance(prompts, dict) else getattr(prompts, "positive_prompt", None)
                        p_neg = prompts.get("negative_prompt") if isinstance(prompts, dict) else getattr(prompts, "negative_prompt", None)
                        if p_pos and p_pos.strip():
                            eff_prompt = p_pos.strip()
                        if p_neg and p_neg.strip():
                            eff_neg = p_neg.strip()
                    if settings and isinstance(settings, dict):
                        eff_settings = settings

            if chosen_model in ("hunyuan", "wan", "wan_4k", "kling", "kling_pro", "kling_v3", "kling_4k") and self.fal_key and task.image_path.is_file() and task.image_path.stat().st_size > 1000:
                try:
                    raw_diff = task.output_path.parent / f"raw_diff_{task.output_path.name}"
                    if chosen_model in ("wan", "wan_4k"):
                        adapter = FalWan21Adapter(api_key=self.fal_key)
                        await adapter.generate_video(image_url=str(task.image_path), motion_prompt=eff_prompt, output_path=raw_diff, force_live=True, negative_prompt=eff_neg, settings=eff_settings)
                    elif chosen_model in ("kling_v3", "kling_4k"):
                        adapter = FalKlingV3Adapter(api_key=self.fal_key)
                        await adapter.generate_video(image_url=str(task.image_path), motion_prompt=eff_prompt, output_path=raw_diff, force_live=True, negative_prompt=eff_neg, settings=eff_settings)
                    elif chosen_model in ("kling_pro", "kling"):
                        adapter = FalKlingAdapter(api_key=self.fal_key)
                        await adapter.generate_video(image_url=str(task.image_path), motion_prompt=eff_prompt, output_path=raw_diff, force_live=True, negative_prompt=eff_neg, mode="pro")
                    else:
                        adapter = FalHunyuanAdapter(api_key=self.fal_key)
                        await adapter.generate_video(image_url=str(task.image_path), motion_prompt=eff_prompt, output_path=raw_diff, force_live=True, req_file=task.req_file)

                    if raw_diff.is_file() and raw_diff.stat().st_size > 1000:
                        # Direct 4K Pass-Through: If already 4K native, move directly (0% CPU, 0s compute)
                        if _is_clip_4k(raw_diff):
                            logger.info(f"decision_4k_direct_pass: {task.output_path.name} is already 4K native. Skipping re-encoding.")
                            print(f"[DECISION - 4K DIRECT PASS] {task.output_path.name} is native 4K UHD. Preserved directly without CPU re-encoding.")
                            if task.output_path.exists():
                                task.output_path.unlink()
                            raw_diff.rename(task.output_path)
                            return task.output_path

                        # Only scale/encode if clip is not 4K (e.g. 1080p fallback) with thread capping
                        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
                        cmd_scale = [
                            ffmpeg_bin, "-y", "-i", str(raw_diff),
                            "-vf", "scale=3840:2160:flags=lanczos",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4",
                            "-an",
                            str(task.output_path)
                        ]
                        res = subprocess.run(cmd_scale, capture_output=True, text=True)
                        if res.returncode != 0:
                            logger.warning(f"ffmpeg_scale_warn: {res.stderr[:200]}. Using direct copy.")
                            import shutil
                            shutil.copy(str(raw_diff), str(task.output_path))
                        try:
                            raw_diff.unlink(missing_ok=True)
                        except Exception:
                            pass
                        logger.info(f"ai_diffusion_motion_rendered: model={chosen_model} {task.output_path.name}")
                        return task.output_path
                except Exception as e:
                    logger.error(f"ai_diffusion_error: {e}")
                    if not task.allow_fallback:
                        raise RuntimeError(f"AI Video Diffusion failed on live production clip {task.output_path.name}: {e}. (Use --allow-fallback to allow fallback).") from e

            # Fallback only when explicitly permitted
            if task.allow_fallback:
                return await self._render_local_fallback(task.image_path, task.output_path, task.duration_seconds)
            raise RuntimeError(f"Cannot generate motion clip {task.output_path.name}: Image missing or diffusion unavailable without --allow-fallback.")

        return list(await asyncio.gather(*[_process_single_motion(t) for t in tasks]))

    async def _render_local_fallback(self, img_path: Path, out_path: Path, duration_sec: float) -> Path:
        """Deterministic 4K slow steadycam zoom-pan fallback (used only when --allow-fallback is active)."""
        logger.warning(f"decision_motion_fallback: Using high-quality 4K zoom-pan for {out_path.name}")
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        total_frames = int(duration_sec * 24)
        cmd = [
            ffmpeg_bin, "-y", "-loop", "1", "-i", str(img_path),
            "-vf", f"zoompan=z='min(zoom+0.0003,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:fps=24,scale=3840:2160:flags=bicubic",
            "-t", str(duration_sec), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-r", "24", str(out_path),
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except Exception as e:
            logger.error(f"zoompan_primary_failed: {e}. Falling back to safe 4K loop.")
            cmd_safe = [
                ffmpeg_bin, "-y", "-loop", "1", "-i", str(img_path),
                "-vf", "scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160",
                "-t", str(duration_sec), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-r", "24", str(out_path),
            ]
            subprocess.run(cmd_safe, capture_output=True, text=True, check=True)
        return out_path


visual_batch_service = VisualBatchService()

__all__ = ["VisualBatchService", "visual_batch_service", "MotionClipTask", "resolve_motion_model"]
