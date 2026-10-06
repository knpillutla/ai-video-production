"""Mountain Peak & High Alpine Studio."""
from src.studios.mountain_studio.mountain_catalog import MOUNTAIN_ARCHETYPES
from src.studios.mountain_studio.mountain_director import (
    MountainStoryboard,
    generate_mountain_screenplay_gemini,
)
from src.studios.studio_producer import StudioProducer as MountainStudioProducer

__all__ = [
    "MOUNTAIN_ARCHETYPES",
    "MountainStoryboard",
    "generate_mountain_screenplay_gemini",
    "MountainStudioProducer",
]
