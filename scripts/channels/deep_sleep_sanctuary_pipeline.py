"""Niche Channel 2 Pipeline: Silent Hearth (8-Hour Deep Sleep & Insomnia Sanctuary).

Extends BaseChannelPipeline for automated 3-stage production (Photos -> Master -> 8h Long-Play with 2h black screen).
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

SLEEP_ARCHETYPES = ["blizzard", "camp_fire", "rain", "ocean_world", "lake", "forest"]

CHANNEL_CONFIG = ChannelPipelineConfig(
    channel_name="Silent Hearth",
    channel_handle="@SilentHearthSleep",
    output_dir=Path("storage/channels/silent_hearth"),
    script_name="deep_sleep_sanctuary_pipeline.py",
    default_hours=8.0,
    default_fade_black_hours=None,
    strategy_description="Hypnotic delta-wave entrainment, cozy hearth warmth, and ultra-fast direct-copy broadcast stretching.",
)

pipeline = BaseChannelPipeline(CHANNEL_CONFIG)


async def main():
    parser = create_base_channel_parser(
        description="Silent Hearth Niche Channel Producer",
        primary_choices=SLEEP_ARCHETYPES,
        default_primary="blizzard",
        default_hours=8.0,
        default_fade_black=None,
        supports_secondary=True,
        secondary_default="camp_fire",
    )
    args = parser.parse_args()

    sb = generate_ambient_storyboard(
        primary=args.primary,
        secondary=args.secondary,
        custom_prompt=args.prompt,
        duration_seconds=args.master_duration,
        num_shots=args.shots,
    )

    fade_hours = args.fade_black or (2.0 if getattr(args, "sleep", False) else None)

    await pipeline.execute(
        sb=sb,
        episode_id=args.id,
        motion_model=args.motion_model,
        long_play_hours=args.hours,
        fade_to_black_hours=fade_hours,
        generate_short=not args.no_short,
        photos_only=args.photos_only,
        no_bgm=args.no_bgm,
        auto_stretch=args.auto_stretch,
        allow_fallback=args.allow_fallback,
    )


if __name__ == "__main__":
    asyncio.run(main())
