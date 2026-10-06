"""Mountain Studio 4K Single-Pass Master Producer."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional
from src.studios.screenplay_models import AmbientScenePrompt, AmbientStoryboard
from src.studios.studio_producer import StudioProducer
from src.studios.mountain_studio.mountain_director import MountainStoryboard


class MountainStudioProducer:
    def __init__(self, output_base_dir: Optional[Path] = None):
        self.output_base = (output_base_dir or Path("storage/mountain_studio")).resolve()
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.producer = StudioProducer(self.output_base)

    async def produce(
        self,
        sb: MountainStoryboard,
        tier: str = "balanced",
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
        amb_sb = AmbientStoryboard(
            title=sb.title,
            story_topic=sb.story_topic,
            primary_archetype=sb.primary_archetype,
            secondary_archetype=sb.secondary_archetype,
            cluster="mountain",
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
                    motion_type=getattr(s, "motion_type", "ai_diffusion"),
                    camera_movement=getattr(s, "camera_movement", "slow_zoom_in"),
                    motion_rationale=getattr(s, "motion_rationale", None),
                )
                for s in sb.scenes
            ],
        )
        return await self.producer.produce(
            sb=amb_sb,
            tier=tier,
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
