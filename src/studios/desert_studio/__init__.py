"""Desert Studio package for luxury desert glamping sanctuaries across all diurnal timings."""

from pathlib import Path
from typing import Any, Dict, Optional
from src.studios.desert_studio.desert_catalog import DESERT_ARCHETYPES
from src.studios.desert_studio.desert_director import (
    DesertScenePrompt,
    DesertStoryboard,
    desert_screenplay_to_storyboard,
    generate_desert_screenplay_gemini,
)
from src.studios.studio_producer import StudioProducer as DesertStudioProducer


async def handle_orchestrated_desert(
    storyboard: DesertStoryboard,
    output_base_dir: Optional[Path] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Universal entrypoint for orchestrating Desert Studio production pipelines."""
    producer = DesertStudioProducer(output_base_dir)
    return await producer.produce(sb=storyboard, **kwargs)


__all__ = [
    "DESERT_ARCHETYPES",
    "DesertScenePrompt",
    "DesertStoryboard",
    "desert_screenplay_to_storyboard",
    "generate_desert_screenplay_gemini",
    "DesertStudioProducer",
    "handle_orchestrated_desert",
]
