"""Desert Studio package for luxury desert glamping sanctuaries across all diurnal timings."""

from src.studios.desert_studio.desert_catalog import DESERT_ARCHETYPES
from src.studios.desert_studio.desert_director import (
    DesertScenePrompt,
    DesertStoryboard,
    desert_screenplay_to_storyboard,
    generate_desert_screenplay_gemini,
)
from src.studios.desert_studio.desert_producer import (
    DesertStudioProducer,
    handle_orchestrated_desert,
)

__all__ = [
    "DESERT_ARCHETYPES",
    "DesertScenePrompt",
    "DesertStoryboard",
    "desert_screenplay_to_storyboard",
    "generate_desert_screenplay_gemini",
    "DesertStudioProducer",
    "handle_orchestrated_desert",
]
