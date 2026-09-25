"""Niche Channel 1 Pipeline: Earth Serenade (4K Scenic Nature Sanctuaries).

Extends BaseChannelPipeline for automated 3-stage production (Photos -> Master -> 3h Long-Play).
"""

import asyncio
from pathlib import Path
import sys
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from src.services.base_channel_pipeline import (
    BaseChannelPipeline,
    ChannelPipelineConfig,
    create_base_channel_parser,
)
from src.studios.ambient_world.ambient_storyboard import generate_ambient_storyboard

NATURE_ARCHETYPES = ["swiss_alps", "himalayas", "ocean_world", "mountains", "lake", "forest", "autumn"]

CHANNEL_CONFIG = ChannelPipelineConfig(
    channel_name="Earth Serenade",
    channel_handle="@EarthSerenade4K",
    output_dir=Path("storage/channels/earth_serenade"),
    script_name="nature_sanctuary_pipeline.py",
    default_hours=3.0,
    strategy_description="High-CTR nature relaxation with immersive spatial foley, alpine acoustic depth, and native 4K living wallpaper diffusion.",
)

pipeline = BaseChannelPipeline(CHANNEL_CONFIG)


async def main():
    parser = create_base_channel_parser(
        description="Earth Serenade Niche Channel Producer",
        primary_choices=NATURE_ARCHETYPES,
        default_primary="swiss_alps",
        default_hours=3.0,
    )
    args = parser.parse_args()

    sb = generate_ambient_storyboard(
        primary=args.primary,
        custom_prompt=args.prompt,
        duration_seconds=args.master_duration,
        num_shots=args.shots,
    )

    await pipeline.execute(
        sb=sb,
        episode_id=args.id,
        motion_model=args.motion_model,
        long_play_hours=args.hours,
        generate_short=not args.no_short,
        photos_only=args.photos_only,
        auto_stretch=args.auto_stretch,
        allow_fallback=args.allow_fallback,
    )


if __name__ == "__main__":
    asyncio.run(main())
