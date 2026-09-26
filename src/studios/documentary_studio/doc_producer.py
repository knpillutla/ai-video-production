"""Documentary Studio 4K Single-Pass Master Producer.

Orchestrates 4-Stage Progressive Quality Gate for blue-chip documentaries:
Topic Deduplication -> Keyframes Review -> Narration Voiceover -> Video Motion -> 4K Master Assembly.
"""

from __future__ import annotations

import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from src.core.telemetry import logger
from src.services.soundtrack_service import soundtrack_service
from src.services.topic_memory import topic_memory
from src.services.visual_batch_service import MotionClipTask, visual_batch_service
from src.studios.documentary_studio.doc_audio_mixer import generate_documentary_subtitles, mix_documentary_audio
from src.studios.documentary_studio.doc_export_service import assemble_documentary_4k_master, export_documentary_metadata_package
from src.studios.documentary_studio.doc_storyboard import DocStoryboard
from src.studios.documentary_studio.doc_voice_service import doc_voice_service


class DocumentaryProducer:
    """Produces broadcast-grade 4K 24fps documentaries with authoritative narration."""

    def __init__(self, output_base_dir: Optional[Path] = None):
        self.output_base = (output_base_dir or Path("storage/channels/documentary")).resolve()
        self.output_base.mkdir(parents=True, exist_ok=True)

    async def produce(
        self,
        sb: DocStoryboard,
        episode_id: Optional[str] = None,
        motion_model: str = "auto",
        female_voice: bool = False,
        include_bgm: bool = False,
        photos_only: bool = False,
        allow_fallback: bool = False,
    ) -> Dict[str, Any]:
        """Execute 4-Stage Progressive Quality Gate with 100% Artifact Idempotency."""
        t_start = time.time()
        ep_dir = (self.output_base / episode_id) if episode_id else (self.output_base / f"ep_doc_{sb.genre.value}_{int(time.time())}")
        ep_dir.mkdir(parents=True, exist_ok=True)

        # Stage 1: Topic Deduplication & Autonomous Creative Pivot
        if not episode_id:
            is_dup, conflict = await topic_memory.is_duplicate_topic(sb.title, genre=f"doc_{sb.genre.value}")
            if is_dup and conflict:
                logger.warning(f"documentary_duplicate_detected: '{sb.title}' matches {conflict.get('episode_id')}")
                print(f"[DECISION - TOPIC DEDUPLICATION] Topic '{sb.title}' exists in Topic Memory. Auto-pivoting angle...")
                sb.title = f"{sb.title} ~ The Untold Frontier"
            else:
                print(f"[DECISION - TOPIC DEDUPLICATION] Title '{sb.title}' is 100% novel. Proceeding.")

        # Stage 2: Keyframe Image Gate (Concurrent Idempotent Batch)
        kf_tasks = [
            (scene.visual_prompt, ep_dir / f"keyframe_p{scene.scene_index}.jpg", ep_dir / f"fal_req_p{scene.scene_index}.json", scene.scene_index)
            for scene in sb.scenes
        ]
        keyframe_paths = await visual_batch_service.render_keyframes_batch(kf_tasks)

        if photos_only:
            from src.services.notification import notification_service
            await notification_service.notify_keyframes_ready(
                channel_name=f"Documentary Studio ({sb.genre.value.upper()})",
                episode_id=ep_dir.name,
                title=sb.title,
                keyframe_paths=[str(p.resolve()) for p in keyframe_paths],
                pipeline_script="documentary_pipeline.py",
            )
            return {
                "episode_id": ep_dir.name, "title": sb.title, "status": "photos_ready_for_review",
                "keyframes": [str(p) for p in keyframe_paths], "storage_path": str(ep_dir),
            }

        # Stage 3: Timed Narration Voiceover Synthesis
        voice_path = ep_dir / f"voiceover_{'female' if female_voice else 'male'}_{sb.language}.wav"
        scenes_narr = [s.narration_text for s in sb.scenes]
        scenes_dur = [s.duration_seconds for s in sb.scenes]
        
        await doc_voice_service.synthesize_full_documentary_voiceover(
            scenes_narration=scenes_narr,
            output_full_wav=voice_path,
            scene_durations=scenes_dur,
            language=sb.language,
            female=female_voice,
        )

        # Stage 3B: Optional Subtle BGM Synthesis & Low Ducking (-26dB)
        bgm_path = None
        if include_bgm:
            raw_bgm = ep_dir / "raw_doc_bgm.mp3"
            if not raw_bgm.is_file() or raw_bgm.stat().st_size < 1000:
                await soundtrack_service.synthesize_ambient_soundtrack(sb.title, sb.audio_tags, raw_bgm, sb.total_duration)
            bgm_path = raw_bgm

        mixed_audio = ep_dir / "master_audio_48k.aac"
        mix_documentary_audio(voice_path, bgm_path, mixed_audio, target_lufs=-14.0)

        # Generate timestamped SRT subtitles
        srt_path = ep_dir / "subtitles.srt"
        generate_documentary_subtitles(scenes_narr, scenes_dur, srt_path)

        # Stage 4: AI Video Diffusion Motion Synthesis (Dynamic Model Routing per Scene)
        motion_tasks = []
        for scene, kf_path in zip(sb.scenes, keyframe_paths):
            eff_model = motion_model if motion_model != "auto" else scene.recommended_model
            motion_tasks.append(
                MotionClipTask(
                    image_path=kf_path,
                    motion_prompt=scene.motion_prompt,
                    visual_prompt=scene.visual_prompt,
                    output_path=ep_dir / f"motion_p{scene.scene_index}.mp4",
                    duration_seconds=scene.duration_seconds,
                    model=eff_model,
                    domain=scene.motion_domain,
                    req_file=ep_dir / f"fal_diff_req_p{scene.scene_index}.json",
                    allow_fallback=allow_fallback,
                )
            )
        video_clip_paths = await visual_batch_service.render_motion_batch(motion_tasks)

        # Stage 5: Master Assembly & Packaging
        master_path = ep_dir / "master_4k_documentary.mp4"
        assemble_documentary_4k_master(video_clip_paths, mixed_audio, master_path, srt_path)
        yt_pkg = export_documentary_metadata_package(sb, ep_dir)

        await topic_memory.remember_topic(
            topic=sb.title,
            genre=f"doc_{sb.genre.value}",
            tags=[sb.genre.value, "documentary", sb.language],
            story_synopsis=f"4K Documentary on {sb.title} ({len(sb.scenes)} scenes)",
            episode_id=ep_dir.name,
        )

        render_time = round(time.time() - t_start, 2)
        logger.info(f"documentary_production_ready: {ep_dir.name} in {render_time}s")

        return {
            "episode_id": ep_dir.name, "title": sb.title, "master_video_path": str(master_path),
            "voiceover_path": str(voice_path), "audio_track": str(mixed_audio), "subtitles_path": str(srt_path),
            "keyframes": [str(p) for p in keyframe_paths], "raw_videos": [str(p) for p in video_clip_paths],
            "youtube_package": yt_pkg, "render_time_seconds": render_time, "storage_path": str(ep_dir),
        }
