"""Standalone CLI Agent for Healing Meditation & Relaxing Music Productions."""

import argparse
import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.studios.healing_relaxation.healing_producer import HealingRelaxationProducer
from src.studios.healing_relaxation.healing_storyboard import generate_healing_storyboard


async def main():
    parser = argparse.ArgumentParser(description="Produce 4K Healing Meditation Video")
    parser.add_argument("--theme", type=str, default="Tranquil Zen Garden & Sacred Lotus Pond at Dawn", help="Healing theme")
    parser.add_argument("--duration", type=float, default=60.0, help="Total duration in seconds")
    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f"🧘 Healing Relaxation Studio: Directing 4K Master Video")
    print(f"Theme: {args.theme}")
    print(f"Duration: {args.duration}s | Pacing: 2-Perspective Long-Play")
    print(f"=======================================================\n")

    sb = generate_healing_storyboard(theme=args.theme, duration_seconds=args.duration)
    producer = HealingRelaxationProducer()
    result = await producer.produce(sb)

    print("\n=======================================================")
    print("✅ Healing Relaxation 4K Production Completed Successfully!")
    print(f"Episode ID:  {result['episode_id']}")
    print(f"Master 4K:   {result['master_video_path']}")
    print(f"Keyframes:   {len(result['keyframes'])} images")
    print(f"Soundtrack:  {result['bgm_path']}")
    print(f"Render Time: {result['render_time_seconds']}s")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
