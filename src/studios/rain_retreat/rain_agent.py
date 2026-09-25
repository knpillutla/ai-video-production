"""Standalone CLI Agent for Rain Retreat Studio Productions."""

import argparse
import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.studios.rain_retreat.rain_producer import RainRetreatProducer
from src.studios.rain_retreat.rain_storyboard import generate_rain_storyboard


async def main():
    parser = argparse.ArgumentParser(description="Produce 4K Rain Retreat Video")
    parser.add_argument("--theme", type=str, default="Lush Forest River in Gentle Rain", help="Rain theme")
    parser.add_argument("--duration", type=float, default=60.0, help="Total duration in seconds")
    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f"🌧️ Rain Retreat Studio: Directing 4K Master Video")
    print(f"Theme: {args.theme}")
    print(f"Duration: {args.duration}s | Pacing: 2-Perspective Long-Play")
    print(f"=======================================================\n")

    sb = generate_rain_storyboard(theme=args.theme, duration_seconds=args.duration)
    producer = RainRetreatProducer()
    result = await producer.produce(sb)

    print("\n=======================================================")
    print("✅ Rain Retreat 4K Production Completed Successfully!")
    print(f"Episode ID:  {result['episode_id']}")
    print(f"Master 4K:   {result['master_video_path']}")
    print(f"Keyframes:   {len(result['keyframes'])} images")
    print(f"Soundtrack:  {result['bgm_path']}")
    print(f"Render Time: {result['render_time_seconds']}s")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
