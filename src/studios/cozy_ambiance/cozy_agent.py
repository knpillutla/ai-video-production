"""Standalone CLI Agent for Cozy Ambiance & Biophilic Studio Productions."""

import argparse
import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

from src.core.telemetry import logger
from src.studios.cozy_ambiance.cozy_producer import CozyAmbianceProducer
from src.studios.cozy_ambiance.cozy_storyboard import generate_cozy_storyboard


async def main():
    parser = argparse.ArgumentParser(description="Produce 4K Cozy Ambiance Video")
    parser.add_argument("--theme", type=str, default="Cozy Oceanfront Terrace Fireplace & Ocean Waves", help="Ambiance theme")
    parser.add_argument("--duration", type=float, default=60.0, help="Total duration in seconds")
    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f"🎬 Cozy Ambiance Studio: Directing 4K Master Video")
    print(f"Theme: {args.theme}")
    print(f"Duration: {args.duration}s | Pacing: 2-Perspective Long-Play")
    print(f"=======================================================\n")

    sb = generate_cozy_storyboard(theme=args.theme, duration_seconds=args.duration)
    producer = CozyAmbianceProducer()
    result = await producer.produce(sb)

    print("\n=======================================================")
    print("✅ Cozy Ambiance 4K Production Completed Successfully!")
    print(f"Episode ID:  {result['episode_id']}")
    print(f"Master 4K:   {result['master_video_path']}")
    print(f"Keyframes:   {len(result['keyframes'])} images")
    print(f"Soundtrack:  {result['bgm_path']}")
    print(f"Render Time: {result['render_time_seconds']}s")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
