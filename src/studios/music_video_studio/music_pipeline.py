"""Unified Entrypoint and Facade for Music & Dance Video Pipelines.

Dispatches requests directly to dedicated, specialized pipelines:
- StaticVocalPipeline: Solo singer locked tripod portrait with particle VFX
- SoloSingingPipeline: Multi-angle performance with dynamic camera transitions
- ConcertPipeline: Live stadium / arena stage performance with lighting trusses
- DuetRomancePipeline: Male & female duet harmony and alternating perspectives
- DanceFolkPipeline: High-energy cultural mass folk choreography & beat drops
"""

from __future__ import annotations

from typing import Any, Optional

from src.studios.music_video_studio.base_music_pipeline import BaseMusicVideoPipeline
from src.studios.music_video_studio.pipeline_factory import (
    ConcertPipeline,
    DanceFolkPipeline,
    DuetRomancePipeline,
    SoloSingingPipeline,
    StaticVocalPipeline,
    get_music_video_pipeline,
)


class MusicVideoPipeline:
    """Facade delegating dynamically to the specialized music video pipeline."""

    def __init__(
        self,
        user_id: str,
        channel_id: str,
        episode_id: str,
        production_name: str = "standalone",
    ):
        self.user_id = user_id
        self.channel_id = channel_id
        self.episode_id = episode_id
        self.production_name = production_name

    def _get_pipeline(self, genre: Optional[str]) -> BaseMusicVideoPipeline:
        return get_music_video_pipeline(
            genre=genre,
            user_id=self.user_id,
            channel_id=self.channel_id,
            episode_id=self.episode_id,
            production_name=self.production_name,
        )

    @property
    def ep_dir(self):
        return self._get_pipeline("music/static_vocal").ep_dir

    async def stage_1_script(self, **kwargs) -> dict[str, Any]:
        pipe = self._get_pipeline(kwargs.get("genre"))
        return await pipe.stage_1_script(**kwargs)

    async def stage_2_keyframes(self, **kwargs) -> list[dict[str, Any]]:
        pipe = self._get_pipeline(kwargs.get("genre"))
        return await pipe.stage_2_keyframes(**kwargs)

    async def stage_3_audio(self, **kwargs) -> list[dict[str, Any]]:
        pipe = self._get_pipeline(kwargs.get("genre"))
        return await pipe.stage_3_audio(**kwargs)

    async def stage_4_master_assembly(self, **kwargs):
        pipe = self._get_pipeline(kwargs.get("genre"))
        return await pipe.stage_4_master_assembly(**kwargs)

    async def produce(self, **kwargs) -> dict[str, Any]:
        pipe = self._get_pipeline(kwargs.get("genre"))
        return await pipe.produce(**kwargs)


__all__ = [
    "MusicVideoPipeline",
    "get_music_video_pipeline",
    "StaticVocalPipeline",
    "SoloSingingPipeline",
    "ConcertPipeline",
    "DuetRomancePipeline",
    "DanceFolkPipeline",
]
