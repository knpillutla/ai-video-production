"""Travel & Scenic Wonders Studio Package."""
from src.studios.travel_studio.travel_catalog import (
    TRAVEL_ARCHETYPES,
    get_all_travel_archetypes,
    get_travel_archetype,
)
from src.studios.travel_studio.travel_director import (
    TravelScenePrompt,
    TravelStoryboard,
    generate_travel_screenplay_gemini,
)
from src.studios.studio_producer import StudioProducer as TravelStudioProducer

__all__ = [
    "TRAVEL_ARCHETYPES",
    "get_all_travel_archetypes",
    "get_travel_archetype",
    "TravelScenePrompt",
    "TravelStoryboard",
    "generate_travel_screenplay_gemini",
    "TravelStudioProducer",
]
