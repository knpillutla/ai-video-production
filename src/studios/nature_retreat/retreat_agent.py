"""Autonomous Nature Retreat Director Agent & Scheduled Generator."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.telemetry import logger
from src.studios.nature_retreat.retreat_producer import produce_nature_retreat


DEFAULT_THEMES = [
    "Rainforest Waterfall Patio & Plunge Pool",
    "Japanese Kyoto Zen Garden & Koi Pond",
    "Swiss Alpine Glacier Stream Chalet",
    "Santorini Cliffside Ocean Sunset Pool",
    "Nordic Forest Mossy River Retreat",
]


async def run_nature_retreat_job(theme: str | None = None, duration: float = 20.0, scenes: int = 4):
    """Autonomous execution entrypoint for nature retreat production."""
    selected_theme = theme or DEFAULT_THEMES[0]
    logger.info(f"starting_nature_retreat_agent: theme='{selected_theme}', duration={duration}s, scenes={scenes}")
    print("=" * 80)
    print("AUTONOMOUS NATURE RETREAT STUDIO (4K BROADCAST PRODUCTION)")
    print(f"Theme: {selected_theme}")
    print(f"Duration: {duration}s ({scenes} scenes)")
    print("=" * 80)

    result = await produce_nature_retreat(theme=selected_theme, duration=duration, scenes=scenes)

    print("\n[SUCCESS] Production Complete!")
    print(f"Master Video: {result['master_video_path']}")
    print(f"Keyframes Generated: {len(result['keyframes'])}")
    print(f"Raw Video Clips: {len(result['raw_videos'])}")
    print(f"Soundtrack Stem: {result['bgm_path']}")
    print(f"Render Time: {result['render_time_seconds']}s")
    print("=" * 80)
    return result


def main():
    parser = argparse.ArgumentParser(description="Autonomous 4K Nature Retreat Generator")
    parser.add_argument("--theme", type=str, default=None, help="Retreat theme name")
    parser.add_argument("--duration", type=float, default=20.0, help="Target duration in seconds")
    parser.add_argument("--scenes", type=int, default=4, help="Number of distinct camera scenes")
    args = parser.parse_args()

    asyncio.run(run_nature_retreat_job(theme=args.theme, duration=args.duration, scenes=args.scenes))


if __name__ == "__main__":
    main()
