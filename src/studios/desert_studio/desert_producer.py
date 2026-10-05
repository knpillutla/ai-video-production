"""Desert Studio 4K Single-Pass Master Producer.

Enforces Universal Artifact Caching, Resilient Idempotency, FAL Request State Persistence,
Velvet 432Hz Anti-Fatigue Acoustic Mastering, AI Video Diffusion (Wan/Kling), and 4K UHD rendering.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from src.studios.screenplay_models import AmbientScenePrompt, AmbientStoryboard
from src.studios.studio_producer import StudioProducer
from src.studios.desert_studio.desert_director import DesertStoryboard


class DesertStudioProducer:
    """Produces 4K broadcast-grade Desert meditation videos under $2.20 USD."""

    def __init__(self, output_base_dir: Optional[Path] = None):
        self.output_base = (output_base_dir or Path("storage/desert_studio")).resolve()
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.producer = StudioProducer(self.output_base)

    async def produce(
        self,
        sb: DesertStoryboard,
        motion_model: str = "wan",
        motion_only: bool = False,
        keyframes_only: bool = False,
        audio_only: bool = False,
        no_bgm: bool = False,
        force_rerun: bool = False,
        episode_dir: Optional[Path] = None,
        long_play_hours: float = 0.0,
        generate_short: bool = False,
    ) -> Dict[str, Any]:
        """Execute the 4-Stage Progressive Quality Gate for Desert productions."""
        amb_sb = AmbientStoryboard(
            title=sb.title,
            story_topic=sb.story_topic,
            primary_archetype=sb.primary_archetype,
            secondary_archetype=sb.secondary_archetype,
            cluster=sb.cluster or "desert",
            total_duration=sb.total_duration,
            recommended_fps=sb.recommended_fps,
            audio_tags=sb.audio_tags,
            scenes=[
                AmbientScenePrompt(
                    scene_index=s.scene_index,
                    perspective_type=s.perspective_type,
                    visual_prompt=s.visual_prompt,
                    motion_prompt=s.motion_prompt,
                    duration_seconds=s.duration_seconds,
                    domain=s.domain,
                    location_hub=s.location_hub,
                )
                for s in sb.scenes
            ],
        )

        return await self.producer.produce(
            sb=amb_sb,
            motion_model=motion_model,
            motion_only=motion_only,
            keyframes_only=keyframes_only,
            audio_only=audio_only,
            no_bgm=no_bgm,
            force_rerun=force_rerun,
            episode_dir=episode_dir,
            long_play_hours=long_play_hours,
            generate_short=generate_short,
        )


async def handle_orchestrated_desert(
    storyboard: DesertStoryboard,
    output_base_dir: Optional[Path] = None,
    motion_model: str = "wan",
    motion_only: bool = False,
    keyframes_only: bool = False,
    audio_only: bool = False,
    no_bgm: bool = False,
    force_rerun: bool = False,
    episode_dir: Optional[Path] = None,
    long_play_hours: float = 0.0,
    generate_short: bool = False,
) -> Dict[str, Any]:
    """Universal entrypoint for orchestrating Desert Studio production pipelines."""
    producer = DesertStudioProducer(output_base_dir)
    return await producer.produce(
        sb=storyboard,
        motion_model=motion_model,
        motion_only=motion_only,
        keyframes_only=keyframes_only,
        audio_only=audio_only,
        no_bgm=no_bgm,
        force_rerun=force_rerun,
        episode_dir=episode_dir,
        long_play_hours=long_play_hours,
        generate_short=generate_short,
    )
