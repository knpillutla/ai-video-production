"""Niche Channel 3 Pipeline: Rain & Quill (3-Hour Deep Study & Focus Lounge).

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

FOCUS_ARCHETYPES = ["beach_house", "rain", "forest", "lake", "autumn", "camp_fire"]

CHANNEL_CONFIG = ChannelPipelineConfig(
    channel_name="Rain & Quill",
    channel_handle="@RainAndQuill",
    output_dir=Path("storage/channels/rain_and_quill"),
    script_name="study_focus_cafe_pipeline.py",
    default_hours=3.0,
    strategy_description="Deep flow-state audio, warm library/cafe aesthetics, and soothing rain backdrop.",
)

pipeline = BaseChannelPipeline(CHANNEL_CONFIG)


async def main():
    parser = create_base_channel_parser(
        description="Rain & Quill Niche Channel Producer",
        primary_choices=FOCUS_ARCHETYPES,
        default_primary="beach_house",
        default_hours=3.0,
        supports_secondary=True,
        secondary_default="rain",
    )
    args = parser.parse_args()

    sb = generate_ambient_storyboard(
        primary=args.primary,
        secondary=args.secondary,
        custom_title=f"Cozy {args.primary.replace('_', ' ').title()} Rain ~ {int(args.hours)} Hours Deep Study & Focus [4K]",
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
