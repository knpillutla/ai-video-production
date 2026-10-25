"""Pipeline Factory and Dispatcher for Global Music & Dance Videos.

Routes genre selections to their specialized, dedicated pipeline implementation:
- music/static_vocal -> StaticVocalPipeline
- music/solo_singer -> SoloSingingPipeline
- music/concert_live -> ConcertPipeline
- music/duet_romance -> DuetRomancePipeline
- dance/folk -> DanceFolkPipeline
- music/mass_song -> MassSongPipeline
"""

from __future__ import annotations

from typing import Optional

from src.studios.music_video_studio.base_music_pipeline import BaseMusicVideoPipeline
from src.studios.music_video_studio.concert_pipeline import ConcertPipeline
from src.studios.music_video_studio.dance_folk_pipeline import DanceFolkPipeline
from src.studios.music_video_studio.duet_romance_pipeline import DuetRomancePipeline
from src.studios.music_video_studio.instrumental_pipeline import InstrumentalPipeline
from src.studios.music_video_studio.mass_song_pipeline import MassSongPipeline
from src.studios.music_video_studio.solo_singing_pipeline import SoloSingingPipeline
from src.studios.music_video_studio.static_vocal_pipeline import StaticVocalPipeline
from src.studios.music_video_studio.virtual_artist_pipeline import VirtualArtistPipeline


def get_music_video_pipeline(
    genre: Optional[str],
    user_id: str,
    channel_id: str,
    episode_id: str,
    production_name: str = "standalone",
) -> BaseMusicVideoPipeline:
    """Instantiate the specialized pipeline matching the music video genre."""
    g = (genre or "").lower().strip()
    if "virtual_artist" in g or "artist" in g or "lara_aredo" in g:
        return VirtualArtistPipeline(user_id=user_id, channel_id=channel_id, episode_id=episode_id, production_name=production_name)
    if "instrumental" in g:
        return InstrumentalPipeline(user_id=user_id, channel_id=channel_id, episode_id=episode_id, production_name=production_name)
    if "mass" in g:
        return MassSongPipeline(user_id=user_id, channel_id=channel_id, episode_id=episode_id, production_name=production_name)
    if "concert" in g or "live" in g:
        return ConcertPipeline(user_id=user_id, channel_id=channel_id, episode_id=episode_id, production_name=production_name)
    if "solo" in g or "singer" in g:
        return SoloSingingPipeline(user_id=user_id, channel_id=channel_id, episode_id=episode_id, production_name=production_name)
    if "duet" in g or "romance" in g:
        return DuetRomancePipeline(user_id=user_id, channel_id=channel_id, episode_id=episode_id, production_name=production_name)
    if "dance" in g or "folk" in g:
        return DanceFolkPipeline(user_id=user_id, channel_id=channel_id, episode_id=episode_id, production_name=production_name)
    return StaticVocalPipeline(user_id=user_id, channel_id=channel_id, episode_id=episode_id, production_name=production_name)


__all__ = [
    "get_music_video_pipeline",
    "StaticVocalPipeline",
    "SoloSingingPipeline",
    "ConcertPipeline",
    "DuetRomancePipeline",
    "DanceFolkPipeline",
    "MassSongPipeline",
    "InstrumentalPipeline",
    "VirtualArtistPipeline",
]
