"""Unified Visual Media Batch Rendering Service."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
from typing import Any, List, Optional, Tuple

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
from src.providers.visual.google_imagen3 import GoogleImagen3Adapter
from src.providers.visual.fal_aura_sr import FalAuraSRAdapter


@dataclass
class MotionClipTask:
    """Specification for an AI video diffusion motion clip task."""
    image_path: Path; motion_prompt: str; visual_prompt: str; output_path: Path
    duration_seconds: float = 30.0; model: str = "auto"; domain: str = "water_fluid"
    req_file: Optional[Path] = None; allow_fallback: bool = False; force_rerun: bool = False
    negative_prompt: Optional[str] = None; model_configs: Optional[dict[str, Any]] = None
    camera_waypoints: Optional[list] = None; kinetic_micro_zones: Optional[dict] = None
    camera_movement: Optional[Any] = None; interpolation: str = "cubic"
    is_relaxation: bool = False


from src.core.step_logger import log_pipeline_step


def resolve_motion_model(model: str, prompt_context: str, total_shots: int = 4) -> tuple[str, str]:
    """Dynamically route to optimal AI video diffusion model with directorial rationale."""
    m_clean = (model or "").lower()
    if m_clean in ("local_drone", "locked_tripod", "local", "offline", "drone"):
        return "local_drone", "Local Perspective Drone ($0.00 compute)"
    if m_clean in ("wan_4k", "wan_super_res", "wan_upscale"):
        return "wan_4k", "Alibaba Wan 2.1 (1080p) + AI 4K Super-Resolution"
    if m_clean in ("wan", "wan_2_1", "wan21"):
        return "wan", "Alibaba Wan 2.1 motion diffusion"
    if m_clean in ("kling_pro", "kling_v1_6_pro", "kling_v1_5_pro", "kling_1_6", "kling_1_5", "kling"):
        return "kling_pro", "Kling 1.6 Pro high-coherence video diffusion"
    if m_clean in ("kling_v3", "kling_4k", "kling_v3_4k"):
        return "kling_v3", "Kling v3 4K Native video diffusion"
    if m_clean in ("hunyuan", "lanczos", "local_zoompan", "ken_burns", "zoompan"):
        return m_clean, f"Configuration override ({model})"
    if total_shots <= 5:
        return "kling_v3", f"Kling v3 4K Native default ({total_shots} shots)"
    p = prompt_context.lower()
    if any(k in p for k in ("fire", "flame", "ember", "hearth", "waterfall", "rapids", "cascade", "chimney")):
        return "kling_v3", "Kling v3 4K Native for fluid dynamics"
    return "wan_4k", "Alibaba Wan 2.1 + AI 4K Super-Resolution"


from src.services.video_4k_encoder import is_clip_4k as _is_clip_4k, ensure_video_4k



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
        enable_4k_upscale: bool = True,
    ) -> List[Path]:
        """Render batch of keyframes concurrently with disk caching and dynamic image model routing."""
        async def _process_single_keyframe(prompt: str, out_path: Path, req_file: Optional[Path], idx: int) -> Path:
            log_pipeline_step("checking keyframes", f"Shot {idx} Keyframe", "started", metadata={"file": out_path.name})
            if not force_rerun and out_path.is_file() and out_path.stat().st_size > 80_000:
                logger.info(f"decision_keyframe_cache_hit: Shot {idx} reusing {out_path.name} ($0.00 spend)")
                log_pipeline_step("checking keyframes", f"Shot {idx} Keyframe", "completed", "keyframe exists, keyframe not recreated", {"file": out_path.name, "size_bytes": out_path.stat().st_size, "cost": "$0.00"})
                return out_path

            if force_rerun:
                out_path.unlink(missing_ok=True)
                if req_file and req_file.exists():
                    req_file.unlink(missing_ok=True)

            model_str = (image_model or ("flux_dev" if self.fal_key else "gemini")).lower()
            if "imagen" in model_str or "gemini" in model_str:
                adapter = GoogleImagen3Adapter()
                model_display = "Gemini 2.5 Flash Image"
            elif "zimage" in model_str or "z_image" in model_str:
                adapter = FalZImageAdapter(api_key=self.fal_key)
                model_display = "Z-Image Turbo"
            elif "pro" in model_str or "ultra" in model_str:
                adapter = FalFluxProUltraAdapter(api_key=self.fal_key)
                model_display = "FLUX 1.1 Pro Ultra"
            else:
                adapter = FalFluxDevAdapter(api_key=self.fal_key)
                model_display = "FLUX.1-dev"

            log_pipeline_step("checking keyframes", f"Shot {idx} Keyframe", "started", f"keyframe missing, synthesizing via {model_display}", {"file": out_path.name})
            logger.info(f"generating_keyframe [model={model_display}]: Shot {idx} {out_path.name} prompt={prompt[:70]}...")
            await adapter.generate_to_file(prompt=prompt, output_path=out_path, aspect_ratio=aspect_ratio, force_live=bool(self.fal_key))
            if enable_4k_upscale and out_path.is_file():
                await FalAuraSRAdapter(api_key=self.fal_key).upscale_image(out_path, out_path, force_live=bool(self.fal_key))
            log_pipeline_step("checking keyframes", f"Shot {idx} Keyframe", "completed", "keyframe created", {"file": out_path.name, "size_bytes": out_path.stat().st_size if out_path.is_file() else 0})
            return out_path

        return list(await asyncio.gather(*[_process_single_keyframe(p, out, req, idx) for p, out, req, idx in tasks]))

    async def render_motion_batch(
        self,
        tasks: List[MotionClipTask],
    ) -> List[Path]:
        """Render batch of AI video diffusion clips concurrently with dynamic routing and 4K scaling."""
        total_shots = len(tasks)

        async def _process_single_motion(task: MotionClipTask) -> Path:
            log_pipeline_step("checking motion", f"Motion Clip ({task.output_path.name})", "started", metadata={"file": task.output_path.name, "target_duration": task.duration_seconds})
            if not task.force_rerun and task.output_path.is_file() and task.output_path.stat().st_size > 1000:
                from src.services.ambient_export_service import get_media_duration
                c_dur = get_media_duration(task.output_path) or 0.0
                logger.info(f"decision_motion_cache_hit: Reusing {task.output_path.name} ($0.00 spend)")
                log_pipeline_step("checking motion", f"Motion Clip ({task.output_path.name})", "completed", "motion clip exists, motion clip not recreated", {"file": task.output_path.name, "duration": c_dur, "cost": "$0.00"})
                return task.output_path

            if task.force_rerun:
                task.output_path.unlink(missing_ok=True)
                raw_diff = task.output_path.parent / f"raw_diff_{task.output_path.name}"
                raw_diff.unlink(missing_ok=True)

            chosen_model, rationale = resolve_motion_model(task.model, f"{task.visual_prompt} {task.motion_prompt}", total_shots=total_shots)
            logger.info(f"decision_motion_routing: {task.output_path.name} -> {chosen_model.upper()} ({rationale})")
            log_pipeline_step("checking motion", f"Motion Clip ({task.output_path.name})", "started", f"motion clip missing, synthesizing via {chosen_model.upper()}", {"file": task.output_path.name, "rationale": rationale})
            if chosen_model in ("lanczos", "local_zoompan", "ken_burns", "zoompan", "local_drone", "locked_tripod", "local"):
                raw_cfg = task.model_configs if isinstance(task.model_configs, dict) else {}
                local_cfg = raw_cfg.get("local_drone") or raw_cfg.get("ken_burns") or {}
                mov = local_cfg.get("movement") or task.camera_movement or task.camera_waypoints or "stay"
                res_f = await self._render_local_fallback(
                    task.image_path, task.output_path, task.duration_seconds, movement=mov,
                    waypoints=task.camera_waypoints, kinetic_micro_zones=task.kinetic_micro_zones,
                    interpolation=task.interpolation, start_pan=local_cfg.get("start_pan", "center"),
                    start_zoom=local_cfg.get("start_zoom", "normal"), start_tilt=local_cfg.get("start_tilt", "center"),
                    curve=local_cfg.get("curve", "cosine"),
                )
                log_pipeline_step("checking motion", f"Motion Clip ({task.output_path.name})", "completed", "motion clip created via local perspective drone", {"file": task.output_path.name, "cost": "$0.00"})
                return res_f

            eff_prompt = task.motion_prompt
            eff_neg = task.negative_prompt
            eff_settings: dict[str, Any] = {}
            if task.model_configs and isinstance(task.model_configs, dict):
                if chosen_model in ("kling_v3", "kling_4k", "kling_v3_4k"):
                    m_cfg = task.model_configs.get("kling_v3_4k") or task.model_configs.get("kling_v3") or task.model_configs.get("kling_4k")
                elif chosen_model in ("kling_pro", "kling"):
                    m_cfg = task.model_configs.get("kling_v1_6_pro") or task.model_configs.get("kling_pro") or task.model_configs.get("kling")
                elif chosen_model in ("wan", "wan_2_1", "wan_4k"):
                    m_cfg = task.model_configs.get("wan_2_1") or task.model_configs.get("wan")
                else:
                    m_cfg = task.model_configs.get(chosen_model)
                if not m_cfg:
                    raise RuntimeError(f"Mandatory motion config for '{chosen_model}' missing from screenplay model_configs. No fallbacks allowed.")
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

            # Anti-Motion-Fatigue Clear Sky Standard & Realistic Fluid Physics Guard
            p_lower = f"{eff_prompt} {task.visual_prompt}".lower()
            if any(k in p_lower for k in ("rain", "storm", "downpour", "cyclone", "monsoon")):
                eff_neg = f"{eff_neg}, snow, snowfall, snowflakes, blizzard, ice, frost, frozen ground, winter, sleet, hail" if eff_neg else "snow, snowfall, snowflakes, blizzard, ice, frost, frozen ground, winter, sleet, hail"
            elif any(k in p_lower for k in ("snow", "blizzard", "winter")):
                eff_neg = f"{eff_neg}, rain, rainfall, rain droplets, torrential rain, downpour, puddle reflections, wet water drops, monsoon" if eff_neg else "rain, rainfall, rain droplets, torrential rain, downpour, puddle reflections, wet water drops, monsoon"
            elif any(k in p_lower for k in ("sky", "mountain", "valley", "alpine", "nature", "meadow", "landscape", "fjord", "lake", "forest")):
                if "cloudless" not in eff_prompt.lower():
                    eff_prompt = f"{eff_prompt}, crystal-clear static cloudless azure sky, zero clouds, tranquil motionless atmosphere"
                cloud_negs = "clouds, cloudy, overcast sky, overcast, cumulus, stratus, cirrus, storm clouds, dark clouds, moving clouds, timelapse clouds, rapid clouds, rolling clouds, cloud morphing, rapid cloud shadows, sky flickering"
                eff_neg = f"{eff_neg}, {cloud_negs}" if eff_neg else cloud_negs

            # Relaxation Format Strict Locked Tripod Guard (Zero Camera Movements or Angles)
            is_relax_clip = (
                getattr(task, "is_relaxation", False)
                or "/relaxation/" in str(task.output_path).lower()
                or "\\relaxation\\" in str(task.output_path).lower()
                or any(k in f"{eff_prompt} {task.motion_prompt}".lower() for k in ("living wallpaper", "cinemagraph", "locked_stationary", "locked_tripod"))
            )
            if is_relax_clip:
                tripod_lead = "Cinemagraph living wallpaper. Strictly locked stationary camera on a heavy fixed tripod with zero camera movement, zero camera angles, zero pan, zero tilt, zero zoom, zero camera drift. The camera never moves. The entire frame, topography, and architecture remain 100% frozen, solid, and motionless. Only subtle organic living motion in the scene: "
                if "zero camera movement" not in eff_prompt.lower():
                    eff_prompt = f"{tripod_lead}{eff_prompt}"
                cam_negs = "camera movement, camera motion, camera angles, camera pan, panning, camera tilt, tilting, camera zoom, zooming, camera rotation, dolly, drone, tracking shot, flythrough, handheld camera, camera drift, jitter, shaky camera, moving perspective, perspective shift, morphing architecture, changing furniture"
                eff_neg = f"{eff_neg}, {cam_negs}" if eff_neg else cam_negs

            if chosen_model in ("hunyuan", "wan", "wan_4k", "kling", "kling_pro", "kling_v3", "kling_4k") and self.fal_key and task.image_path.is_file() and task.image_path.stat().st_size > 1000:
                try:
                    raw_diff = task.output_path.parent / f"raw_diff_{task.output_path.name}"
                    if chosen_model in ("wan", "wan_4k"):
                        adapter = FalWan21Adapter(api_key=self.fal_key)
                        await adapter.generate_video(image_url=str(task.image_path), motion_prompt=eff_prompt, output_path=raw_diff, force_live=True, negative_prompt=eff_neg, settings=eff_settings, req_file=task.req_file)
                    elif chosen_model in ("kling_v3", "kling_4k"):
                        adapter = FalKlingV3Adapter(api_key=self.fal_key)
                        await adapter.generate_video(image_url=str(task.image_path), motion_prompt=eff_prompt, output_path=raw_diff, force_live=True, negative_prompt=eff_neg, settings=eff_settings, req_file=task.req_file)
                    elif chosen_model in ("kling_pro", "kling"):
                        adapter = FalKlingAdapter(api_key=self.fal_key)
                        await adapter.generate_video(image_url=str(task.image_path), motion_prompt=eff_prompt, output_path=raw_diff, force_live=True, negative_prompt=eff_neg, mode="pro", req_file=task.req_file)
                    else:
                        adapter = FalHunyuanAdapter(api_key=self.fal_key)
                        await adapter.generate_video(image_url=str(task.image_path), motion_prompt=eff_prompt, output_path=raw_diff, force_live=True, req_file=task.req_file)

                    if raw_diff.is_file() and raw_diff.stat().st_size > 1000:
                        ensure_video_4k(raw_diff)
                        if task.output_path.exists():
                            task.output_path.unlink()
                        raw_diff.rename(task.output_path)
                        logger.info(f"ai_diffusion_motion_rendered: model={chosen_model} {task.output_path.name}")
                        log_pipeline_step("checking motion", f"Motion Clip ({task.output_path.name})", "completed", "motion clip created", {"file": task.output_path.name, "cost": "$0.00"})
                        return task.output_path
                except Exception as e:
                    logger.error(f"ai_diffusion_error: {e}")
                    if not task.allow_fallback:
                        raise RuntimeError(f"AI Video Diffusion failed on live production clip {task.output_path.name}: {e}. (Use --allow-fallback to allow fallback).") from e

            # Fallback only when explicitly permitted
            if task.allow_fallback:
                p_text = f"{task.visual_prompt} {task.motion_prompt}".lower()
                mov = "crane_ascend" if any(k in p_text for k in ("crane", "tilt_up", "ascend", "vertical")) else (
                    "drone_sweep_left" if any(k in p_text for k in ("left", "sweep_left", "pan_left")) else (
                        "drone_sweep_right" if any(k in p_text for k in ("right", "sweep_right", "pan_right")) else (
                            "dolly_pullback" if any(k in p_text for k in ("pull_back", "reveal", "zoom_out")) else "slow_drone_forward"
                        )
                    )
                )
                res_fb = await self._render_local_fallback(task.image_path, task.output_path, task.duration_seconds, mov, task.camera_waypoints, task.kinetic_micro_zones)
                log_pipeline_step("checking motion", f"Motion Clip ({task.output_path.name})", "completed", "motion clip created via local perspective drone", {"file": task.output_path.name, "cost": "$0.00"})
                return res_fb
            raise RuntimeError(f"Cannot generate motion clip {task.output_path.name}: Image missing or diffusion unavailable without --allow-fallback.")

        return list(await asyncio.gather(*[_process_single_motion(t) for t in tasks]))

    async def _render_local_fallback(self, img_path: Path, out_path: Path, duration_sec: float, movement: Any = "stay", waypoints: Optional[list] = None, kinetic_micro_zones: Optional[dict] = None, interpolation: str = "cubic", start_pan: str = "center", start_zoom: str = "normal", start_tilt: str = "center", curve: str = "cosine") -> Path:
        """Deterministic 4K CPU motion engine ($0.00 spend): pure locked default, calm drone on demand."""
        m_str = str(movement) if isinstance(movement, (list, dict)) else (movement or "")
        m_lower = m_str.lower()
        if any(k in m_lower for k in ("multi_angle", "skyline", "mission", "fpv_drone", "dynamic_drone")):
            logger.info(f"decision_motion_fallback: 4K CPU multi-angle skyline drone for {out_path.name}")
            from src.scripts.local_perspective_multiangle_drone import render_multiangle_drone_clip
            return await render_multiangle_drone_clip(image_path=img_path, output_path=out_path, duration_seconds=duration_sec, fps=30, target_res=(3840, 2160), force_rerun=True, kinetic_micro_zones=kinetic_micro_zones)
        choreo = "stay" if any(w in m_lower for w in ("stay", "locked", "tripod", "static", "fixed", "hold")) else movement
        logger.info(f"decision_motion_fallback: 4K CPU perspective drone for {out_path.name} (choreo: {choreo}, inter: {interpolation})")
        from src.scripts.local_perspective_drone import render_perspective_drone_clip
        return await render_perspective_drone_clip(
            image_path=img_path, output_path=out_path, duration_seconds=duration_sec,
            fps=24, target_res=(3840, 2160), camera_movement=movement, choreography=choreo, speed_factor=1.0,
            force_rerun=True, camera_waypoints=waypoints, kinetic_micro_zones=kinetic_micro_zones,
            interpolation=interpolation, start_pan=start_pan, start_zoom=start_zoom, start_tilt=start_tilt, curve=curve,
        )

visual_batch_service = VisualBatchService()

__all__ = ["VisualBatchService", "visual_batch_service", "MotionClipTask", "resolve_motion_model"]
