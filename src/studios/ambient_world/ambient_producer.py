"""Ambient World & Relaxation 4K Single-Pass Master Producer.

Enforces Universal Artifact Caching, Resilient Idempotency, FAL Request State Persistence,
Velvet Anti-Fatigue Acoustic Mastering, AI Video Diffusion (Wan/Kling/Hunyuan), and 4K UHD rendering.
"""

import asyncio
import base64
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List, Optional
import httpx
import imageio_ffmpeg

from src.core.telemetry import logger
from src.providers.dance.fal_hunyuan import FalHunyuanAdapter
from src.providers.dance.fal_kling import FalKlingAdapter
from src.providers.visual.fal_flux_pro_ultra import FalFluxProUltraAdapter
from src.providers.visual.fal_wan21 import FalWan21Adapter
from src.services.ambient_export_service import export_metadata_packages, handle_long_play_export, handle_short_export
from src.services.audio_vault import audio_vault
from src.services.binaural_spatial_audio import apply_binaural_spatial_mastering
from src.services.topic_memory import topic_memory
from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


def resolve_diffusion_model(model: str, prompt: str) -> tuple[str, str]:
    """Dynamically route to optimal AI video diffusion model with explicit directorial rationale."""
    if model in ("hunyuan", "wan", "kling", "lanczos"):
        return model, f"Direct configuration override ({model})"
    p = prompt.lower()
    if any(k in p for k in ("fire", "flame", "ember", "hearth", "waterfall", "rapids", "cascade", "chimney")):
        return "kling", "Kling 1.6 Pro selected for high volumetric momentum, dynamic fire embers, and fluid splash plumes"
    if any(k in p for k in ("water", "river", "rain", "ocean", "stream", "lake", "snow", "blizzard", "wave", "droplet")):
        return "wan", "Alibaba Wan 2.1 selected for natural 3D liquid displacement, surface ripples, and falling snow dynamics"
    return "hunyuan", "Tencent Hunyuan Video selected for temporal stability, needle-sharp mountain landscapes, and tree reflections"


class AmbientWorldProducer:
    """Produces 4K broadcast-grade relaxing ambient videos with Velvet audio & AI video diffusion."""

    def __init__(self, output_base_dir: Optional[Path] = None):
        self.output_base = (output_base_dir or Path("storage/ambient_world")).resolve()
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.fal_key = os.getenv("FAL_KEY", "")

    async def produce(
        self,
        sb: AmbientStoryboard,
        episode_id: Optional[str] = None,
        motion_model: str = "auto",
        long_play_hours: Optional[float] = None,
        fade_to_black_hours: Optional[float] = None,
        generate_short: bool = False,
    ) -> Dict[str, Any]:
        """Execute 4-Stage Progressive Quality Gate with 100% Artifact Idempotency."""
        t_start = time.time()
        ep_dir = (self.output_base / episode_id) if episode_id else (self.output_base / f"ep_{sb.primary_archetype[:20]}_{int(time.time())}")
        ep_dir.mkdir(parents=True, exist_ok=True)

        # Stage 1: Pre-Flight Deduplication & Autonomous Creative Auto-Pivot Gate
        if not episode_id:
            is_dup, conflict = await topic_memory.is_duplicate_topic(sb.title, genre=f"ambient_{sb.cluster}")
            if is_dup and conflict:
                logger.warning(f"decision_duplicate_detected: '{sb.title}' matches {conflict.get('episode_id')}. Auto-pivoting to unique sunset theme...")
                print(f"[DECISION - TOPIC DEDUPLICATION] Duplicate topic detected (matches {conflict.get('episode_id')}). Auto-pivoting to unique Twilight variation to protect channel CTR.")
                sb.title = f"{sb.title} ~ Golden Twilight Serenade"
                for s in sb.scenes:
                    s.visual_prompt = f"{s.visual_prompt} Bathed in warm golden twilight and evening mountain stillness."
            else:
                logger.info(f"decision_deduplication_clean: '{sb.title}' is unique. Proceeding without conflict.")
                print(f"[DECISION - TOPIC DEDUPLICATION] Title '{sb.title}' is 100% novel in Topic Memory. Proceeding without conflict.")

        # Stage 2: Keyframe Image Gate (Idempotent per scene)
        keyframe_paths: List[Path] = []
        for scene in sb.scenes:
            kf_path = ep_dir / f"keyframe_p{scene.scene_index}.jpg"
            req_file = ep_dir / f"fal_req_p{scene.scene_index}.json"
            await self._render_keyframe_idempotent(scene.visual_prompt, kf_path, req_file, scene.scene_index)
            keyframe_paths.append(kf_path)

        # Stage 3: Audio Synthesis & Binaural 3D Velvet Mastering (Idempotent)
        raw_bgm_path, master_bgm_path = ep_dir / "raw_soundtrack.mp3", ep_dir / "velvet_binaural_master_48k.mp3"
        if not master_bgm_path.is_file() or master_bgm_path.stat().st_size < 1000:
            await self._synthesize_soundtrack(sb.title, sb.audio_tags, raw_bgm_path, sb.total_duration)
            apply_binaural_spatial_mastering(input_audio=raw_bgm_path, output_audio=master_bgm_path, target_lufs=-21.0, duration_seconds=sb.total_duration)
        else:
            logger.info(f"decision_audio_master_cache_hit: Reusing {master_bgm_path.name} ($0.00 spend)")
            print(f"[DECISION - AUDIO MASTER CACHE HIT] Master audio already exists on disk ({master_bgm_path.name}). Reusing asset ($0.00 spend).")

        # Stage 4: AI Video Diffusion Motion Synthesis & 4K Master Assembly (Idempotent)
        video_clip_paths: List[Path] = []
        for scene, kf_path in zip(sb.scenes, keyframe_paths):
            clip_path = ep_dir / f"motion_p{scene.scene_index}.mp4"
            diff_req_file = ep_dir / f"fal_diff_req_p{scene.scene_index}.json"
            chosen_model, routing_rationale = resolve_diffusion_model(motion_model, f"{scene.visual_prompt} {scene.motion_prompt}")
            if not clip_path.is_file() or clip_path.stat().st_size < 1000:
                logger.info(f"decision_motion_routing: Shot {scene.scene_index} -> Model={chosen_model.upper()} ({routing_rationale})")
                print(f"[DECISION - MOTION ROUTING] Shot {scene.scene_index} -> {chosen_model.upper()} ({routing_rationale})")
                await self._render_motion_clip(kf_path, scene.motion_prompt, clip_path, duration_sec=scene.duration_seconds, model=chosen_model, req_file=diff_req_file)
            else:
                logger.info(f"decision_motion_cache_hit: Reusing {clip_path.name} ($0.00 spend)")
                print(f"[DECISION - MOTION CACHE HIT] Shot {scene.scene_index} clip already exists ({clip_path.name}). Reusing asset ($0.00 spend).")
            video_clip_paths.append(clip_path)

        master_4k_path = ep_dir / "master_4k_ambient.mp4"
        if not master_4k_path.is_file() or master_4k_path.stat().st_size < 1000:
            print(f"[DECISION - MASTER ASSEMBLY] Assembling {len(video_clip_paths)} clips into seamless 4K master with 1.5s cross-dissolve transitions.")
            await self._assemble_4k_master(video_clip_paths, master_bgm_path, master_4k_path)
        else:
            logger.info(f"decision_master_video_cache_hit: Reusing {master_4k_path.name} ($0.00 spend)")
            print(f"[DECISION - MASTER VIDEO CACHE HIT] Master 4K video already exists ({master_4k_path.name}). Reusing asset ($0.00 spend).")

        long_play_path = handle_long_play_export(master_4k_path, ep_dir, long_play_hours, fade_to_black_hours)
        short_video_path = handle_short_export(master_4k_path, ep_dir, generate_short)
        yt_package, ab_thumbnails, localized = export_metadata_packages(sb, ep_dir, long_play_hours, fade_to_black_hours)

        render_time = round(time.time() - t_start, 2)
        logger.info(f"ambient_production_ready: {ep_dir.name} in {render_time}s")
        return {
            "episode_id": ep_dir.name, "title": sb.title, "master_video_path": str(master_4k_path),
            "long_play_video_path": str(long_play_path) if long_play_path else None,
            "short_video_path": str(short_video_path) if short_video_path else None,
            "keyframes": [str(p) for p in keyframe_paths], "raw_videos": [str(p) for p in video_clip_paths],
            "bgm_path": str(master_bgm_path), "youtube_package": yt_package.model_dump(),
            "thumbnail_variants": ab_thumbnails.model_dump(),
            "localized_metadata": {k: v.model_dump() for k, v in localized.items()},
            "render_time_seconds": render_time, "storage_path": str(ep_dir),
        }

    async def _render_keyframe_idempotent(self, prompt: str, out_path: Path, req_file: Path, idx: int = 1):
        """Render FLUX keyframe via modular FalFluxProUltraAdapter with disk caching."""
        if out_path.is_file() and out_path.stat().st_size > 1000:
            logger.info(f"decision_keyframe_cache_hit: Shot {idx} reusing {out_path.name} ($0.00 spend)")
            print(f"[DECISION - KEYFRAME CACHE HIT] Shot {idx} keyframe exists on disk ({out_path.name}). Reusing image ($0.00 spend).")
            return

        logger.info(f"decision_keyframe_invoke_flux: Shot {idx} cache miss. Synthesizing via FLUX 1.1 Pro Ultra...")
        print(f"[DECISION - KEYFRAME CACHE MISS] Shot {idx} not found on disk. Invoking FLUX 1.1 Pro Ultra for 4K needle-sharp photographic visual.")
        adapter = FalFluxProUltraAdapter(api_key=self.fal_key)
        await adapter.generate_to_file(prompt=prompt, output_path=out_path, aspect_ratio="16:9", force_live=bool(self.fal_key))

    async def _render_motion_clip(
        self, img_path: Path, motion_prompt: str, out_path: Path,
        duration_sec: float, model: str = "wan", req_file: Optional[Path] = None
    ):
        """Render motion clip via modular AI video diffusion adapters with FFmpeg Lanczos fallback."""
        if out_path.is_file() and out_path.stat().st_size > 1000:
            logger.info(f"decision_motion_cache_hit: Reusing {out_path.name} ($0.00 spend)")
            print(f"[DECISION - MOTION CACHE HIT] Clip {out_path.name} exists on disk. Reusing asset ($0.00 spend).")
            return

        if model in ("hunyuan", "wan", "kling") and self.fal_key and img_path.is_file() and img_path.stat().st_size > 1000:
            try:
                raw_diff = out_path.parent / f"raw_diff_{out_path.name}"
                if model == "wan":
                    adapter = FalWan21Adapter(api_key=self.fal_key)
                    await adapter.generate_video(image_url=str(img_path), motion_prompt=motion_prompt, output_path=raw_diff, force_live=True)
                elif model == "kling":
                    adapter = FalKlingAdapter(api_key=self.fal_key)
                    await adapter.generate_video(image_url=str(img_path), motion_prompt=motion_prompt, output_path=raw_diff, force_live=True)
                else:
                    adapter = FalHunyuanAdapter(api_key=self.fal_key)
                    await adapter.generate_video(image_url=str(img_path), motion_prompt=motion_prompt, output_path=raw_diff, force_live=True)

                if raw_diff.is_file() and raw_diff.stat().st_size > 1000:
                    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
                    cmd_scale = [
                        ffmpeg_bin, "-y", "-stream_loop", "-1", "-i", str(raw_diff),
                        "-t", str(duration_sec), "-vf", "scale=3840:2160:flags=lanczos",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
                    ]
                    subprocess.run(cmd_scale, capture_output=True, check=True)
                    raw_diff.unlink(missing_ok=True)
                    logger.info(f"ai_diffusion_motion_rendered: model={model} {out_path.name}")
                    return
            except Exception as err:
                logger.warning(f"ai_diffusion_fallback_to_lanczos: {err}")

        # Deterministic 4K Native Lanczos Zoom-Pan Kinematics fallback
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_bin, "-y", "-loop", "1", "-i", str(img_path),
            "-vf", f"scale=3840:2160:flags=lanczos,zoompan=z='min(zoom+0.0002,1.025)':d={int(duration_sec*24)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=3840x2160",
            "-t", str(duration_sec), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    async def _synthesize_soundtrack(self, title: str, tags: str, out_path: Path, total_duration: float):
        """Retrieve cached soundtrack from AudioVault or synthesize via Suno v3.5 Pro."""
        cached = audio_vault.find_matching_stem(genre="ambient relaxation", theme=title, concept=title, tags=tags, min_similarity=0.70)
        if cached and cached.is_file():
            import shutil
            shutil.copy2(cached, out_path)
            logger.info(f"decision_audio_cache_hit: Matched AudioVault stem '{cached.name}'. ($0.00 spend)")
            return

        logger.info(f"decision_audio_invoke_suno: AudioVault cache miss (no stem >= 0.70 similarity). Synthesizing fresh soundscape via Suno v3.5 Pro...")
        from src.providers.music.suno_adapter import SunoMusicAdapter
        adapter = SunoMusicAdapter()
        await adapter.generate_to_file(
            output_path=out_path, genre="ambient sleep, 432hz acoustic music, tranquil foley, soft pads",
            mood=tags, duration_seconds=total_duration, title=title, force_live=True,
        )
        if out_path.is_file() and out_path.stat().st_size > 1000:
            audio_vault.register_stem(
                source_path=out_path, genre="ambient relaxation", theme=title,
                concept="ambient soundscape", tags=tags, vocal_gender="none",
            )

    async def _assemble_4k_master(self, video_clips: List[Path], audio_path: Path, out_master: Path):
        """Assemble seamless 4K master video with smooth cross-dissolve transitions."""
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        n = len(video_clips)
        if n == 1:
            cmd = [ffmpeg_bin, "-y", "-i", str(video_clips[0]), "-i", str(audio_path), "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_master)]
        elif n == 2:
            cmd = [ffmpeg_bin, "-y", "-i", str(video_clips[0]), "-i", str(video_clips[1]), "-i", str(audio_path), "-filter_complex", "[0:v][1:v]xfade=transition=fade:duration=1.5:offset=28.5[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_master)]
        else:
            inputs = []
            for c in video_clips:
                inputs.extend(["-i", str(c)])
            inputs.extend(["-i", str(audio_path)])
            filter_parts, prev_tag, curr_offset = [], "0:v", 28.5
            for i in range(1, n):
                out_tag = f"v{i}" if i < n - 1 else "v"
                filter_parts.append(f"[{prev_tag}][{i}:v]xfade=transition=fade:duration=1.5:offset={curr_offset:.1f}[{out_tag}]")
                prev_tag = out_tag
                curr_offset += 28.5
            cmd = [ffmpeg_bin, "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[v]", "-map", f"{n}:a", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_master)]
        subprocess.run(cmd, capture_output=True, check=True)
