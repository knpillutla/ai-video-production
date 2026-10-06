"""Ocean Studio Package.

Provides dedicated 4K Living Wallpapers and single-pass productions for:
- Overwater Villas & Turquoise Lagoons (Daytime)
- Coastal Verandas & Sunrise Dawn
- Cliffside Sanctuaries & Golden Hour Sunset
- Starlit Beach Pavilions & Bioluminescent Waves (Night)
- Open-Air Beach Campfires & Shoreline Hearths
- Sheltered Balconies & Tropical Ocean Rain
"""

from pathlib import Path
from typing import Any, Dict, Optional
from src.studios.ocean_studio.ocean_catalog import OCEAN_ARCHETYPES
from src.studios.ocean_studio.ocean_director import (
    OceanStoryboard,
    generate_ocean_screenplay_gemini,
    ocean_screenplay_to_storyboard,
)
from src.studios.studio_producer import StudioProducer as OceanStudioProducer


async def handle_orchestrated_ocean(
    storyboard: OceanStoryboard,
    output_base_dir: Optional[Path] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Universal entrypoint for orchestrating Ocean Studio production pipelines."""
    producer = OceanStudioProducer(output_base_dir)
    return await producer.produce(sb=storyboard, **kwargs)


__all__ = [
    "OCEAN_ARCHETYPES",
    "OceanStoryboard",
    "generate_ocean_screenplay_gemini",
    "ocean_screenplay_to_storyboard",
    "OceanStudioProducer",
    "handle_orchestrated_ocean",
]
