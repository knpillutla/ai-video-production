"""Music Video Studio package for global country-aware music and dance production."""

from src.studios.music_video_studio.country_music_catalog import (
    COUNTRY_CATALOG,
    SCENERY_ARCHETYPES,
    MUSIC_PERFORMANCE_TYPES,
    SONG_MOODS,
    resolve_network_language_and_country,
    build_music_video_prompt_package,
)

from src.studios.music_video_studio.music_video_director import generate_music_video_screenplay
from src.studios.music_video_studio.pipeline_factory import (
    get_music_video_pipeline,
    StaticVocalPipeline,
    SoloSingingPipeline,
    ConcertPipeline,
    DuetRomancePipeline,
    DanceFolkPipeline,
)
from src.studios.music_video_studio.music_pipeline import MusicVideoPipeline

__all__ = [
    "COUNTRY_CATALOG",
    "SCENERY_ARCHETYPES",
    "MUSIC_PERFORMANCE_TYPES",
    "SONG_MOODS",
    "resolve_network_language_and_country",
    "build_music_video_prompt_package",
    "generate_music_video_screenplay",
    "MusicVideoPipeline",
    "get_music_video_pipeline",
    "StaticVocalPipeline",
    "SoloSingingPipeline",
    "ConcertPipeline",
    "DuetRomancePipeline",
    "DanceFolkPipeline",
]

