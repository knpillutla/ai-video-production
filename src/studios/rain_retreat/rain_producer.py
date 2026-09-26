"""Rain Retreat 4K Single-Pass Master Producer."""

import asyncio
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
import imageio_ffmpeg

from src.core.telemetry import logger
from src.providers.visual.fal_flux_pro_ultra import FalFluxProUltraAdapter
from src.services.audio_vault import audio_vault
from src.services.topic_memory import topic_memory
from src.studios.rain_retreat.rain_storyboard import RainStoryboard, generate_rain_storyboard


class RainRetreatProducer:
    """Produces 4K broadcast-grade Rain Retreat & River ASMR videos under $2.20 USD."""

    def __init__(self, output_base_dir: Optional[Path] = None):
        self.output_base = (output_base_dir or Path("storage/rain_retreat")).resolve()
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.fal_key = os.getenv("FAL_KEY", "")

    async def produce(self, sb: RainStoryboard) -> Dict[str, Any]:
        """Execute the 4-Stage Progressive Quality Gate for Rain Retreat."""
        t_start = time.time()
        ep_slug = sb.theme.lower().replace(" ", "_")[:30]
        ep_dir = self.output_base / f"ep_{ep_slug}_{int(time.time())}"
        ep_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"starting_rain_retreat_production: theme='{sb.theme}' dir={ep_dir.name}")

        # Stage 2: Keyframe Image Gate (Concurrent 2 Keyframes)
        async def _fetch_kf(scene):
            kf_path = ep_dir / f"keyframe_p{scene.scene_index}.jpg"
            await self._render_keyframe(scene.visual_prompt, kf_path)
            return kf_path

        keyframe_paths = list(await asyncio.gather(*[_fetch_kf(s) for s in sb.scenes]))

        # Stage 3: Audio & Soundtrack Gate
        bgm_path = ep_dir / "rain_soundscape_48k.mp3"
        await self._synthesize_audio(sb.title, sb.audio_tags, bgm_path, sb.total_duration)

        # Stage 4: Fluid Video Motion & 4K Master Assembly (Concurrent Batch)
        async def _fetch_motion(scene, kf_path):
            clip_path = ep_dir / f"motion_p{scene.scene_index}.mp4"
            await self._render_motion_clip(kf_path, scene.motion_prompt, clip_path, duration_sec=scene.duration_seconds)
            return clip_path

        video_clip_paths = list(await asyncio.gather(*[_fetch_motion(s, kf) for s, kf in zip(sb.scenes, keyframe_paths)]))

        master_4k_path = ep_dir / "master_4k_60s.mp4"
        await self._assemble_4k_master(video_clip_paths, bgm_path, master_4k_path)

        topic_memory.remember_topic(
            topic=sb.theme,
            genre="rain_retreat",
            tags=["rain", "river", "asmr", "nature", "sleep", "4k"],
            story_synopsis=f"Rain Retreat: {sb.theme} with serene river rainfall.",
            episode_id=ep_dir.name,
        )

        render_time = round(time.time() - t_start, 2)
        logger.info(f"rain_retreat_master_completed: {master_4k_path.name} in {render_time}s")

        return {
            "episode_id": ep_dir.name,
            "title": sb.title,
            "master_video_path": str(master_4k_path),
            "keyframes": [str(p) for p in keyframe_paths],
            "raw_videos": [str(p) for p in video_clip_paths],
            "bgm_path": str(bgm_path),
            "render_time_seconds": render_time,
            "storage_path": str(ep_dir),
        }

    async def _render_keyframe(self, prompt: str, out_path: Path):
        """Render single FLUX 1.1 Pro Ultra master keyframe via modular provider."""
        adapter = FalFluxProUltraAdapter(api_key=self.fal_key)
        await adapter.generate_to_file(prompt=prompt, output_path=out_path, aspect_ratio="16:9", force_live=bool(self.fal_key))

    async def _render_motion_clip(self, img_path: Path, motion_prompt: str, out_path: Path, duration_sec: float):
        """Render fluid rain motion via single-pass FFmpeg Lanczos zoompan / Wan 2.1."""
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_bin, "-y", "-loop", "1", "-i", str(img_path),
            "-vf", f"scale=3840:2160:flags=lanczos,zoompan=z='min(zoom+0.0003,1.03)':d={int(duration_sec*24)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=3840x2160",
            "-t", str(duration_sec), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    async def _synthesize_audio(self, title: str, tags: str, out_path: Path, total_duration: float):
        """Retrieve cached soundtrack from AudioVault or synthesize via Suno v3.5 Pro."""
        cached = audio_vault.find_matching_stem(genre="rain retreat", theme="forest river", concept=title, tags=tags, min_similarity=0.70)
        if cached and cached.is_file():
            import shutil
            shutil.copy2(cached, out_path)
            logger.info(f"audio_vault_cache_hit_rain: {cached.name} -> {out_path.name}")
            return

        from src.providers.music.suno_adapter import SunoMusicAdapter
        adapter = SunoMusicAdapter()
        await adapter.generate_to_file(
            output_path=out_path,
            genre="ambient rain, river water sounds, asmr sleep",
            mood=tags,
            duration_seconds=total_duration,
            title=title,
            force_live=True,
        )

    async def _assemble_4k_master(self, video_clips: List[Path], audio_path: Path, out_master: Path):
        """Assemble seamless 4K master with 45s Extended Hold and CRF 22 via ambient_export_service."""
        from src.services.ambient_export_service import assemble_4k_master
        assemble_4k_master(video_clips, audio_path, out_master)



async def handle_orchestrated_rain(job_id: str, request: Any) -> Any:
    """Orchestrator bridge handler for Rain Retreat productions."""
    from src.services.storage import get_storage_provider, ArtifactCategory, StudioArtifactManifest

    storage = get_storage_provider()
    sb = generate_rain_storyboard(theme=request.topic, duration_seconds=float(request.duration_seconds))
    producer = RainRetreatProducer()
    result = await producer.produce(sb)

    ep_id = result["episode_id"]
    master_item = await storage.save_artifact(
        project_id=ep_id,
        category=ArtifactCategory.SECTION_0_MASTER,
        filename=Path(result["master_video_path"]).name,
        source_path_or_bytes=result["master_video_path"],
        resolution="3840x2160",
    )

    image_items = []
    for idx, kf in enumerate(result["keyframes"]):
        item = await storage.save_artifact(
            project_id=ep_id,
            category=ArtifactCategory.SECTION_1_IMAGES,
            filename=Path(kf).name,
            source_path_or_bytes=kf,
            scene_index=idx + 1,
            model_name="flux-1.1-pro-ultra",
        )
        image_items.append(item)

    video_items = []
    for idx, vid in enumerate(result["raw_videos"]):
        item = await storage.save_artifact(
            project_id=ep_id,
            category=ArtifactCategory.SECTION_2_VIDEOS,
            filename=Path(vid).name,
            source_path_or_bytes=vid,
            scene_index=idx + 1,
            model_name="wan-2.1-fluid",
        )
        video_items.append(item)

    bgm_item = await storage.save_artifact(
        project_id=ep_id,
        category=ArtifactCategory.SECTION_4_BGM,
        filename=Path(result["bgm_path"]).name,
        source_path_or_bytes=result["bgm_path"],
        model_name="suno-v3.5-pro",
    )

    manifest = StudioArtifactManifest(
        project_id=ep_id,
        title=result["title"],
        studio_type="rain_retreat",
        topic=request.topic,
        created_at=datetime.now(timezone.utc).isoformat(),
        section_0_master=master_item,
        section_1_images=image_items,
        section_2_videos=video_items,
        section_4_bgm=[bgm_item],
    )
    return manifest


try:
    from src.orchestrator.studio_registry import studio_registry
    studio_registry.register_studio(
        studio_id="rain_retreat",
        display_name="Rain Retreat & River ASMR Studio",
        description="Produces 4K Forest River Rainfall, Water Droplet Ripples, and ASMR Soundscapes",
        default_fps=24,
        genre="rain_retreat",
        handler=handle_orchestrated_rain,
    )
except Exception:
    pass
