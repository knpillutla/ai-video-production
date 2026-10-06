"""Standalone CLI agent for Zen Studio productions."""

import argparse
import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.studios.studio_producer import StudioProducer as ZenStudioProducer
from src.studios.zen_studio.zen_director import generate_zen_storyboard


async def main():
    parser = argparse.ArgumentParser(description="Produce a 4K Zen Studio video")
    parser.add_argument("--theme", type=str, default="Tranquil Zen Garden & Sacred Lotus Pond at Dawn", help="Zen theme")
    parser.add_argument("--duration", type=float, default=60.0, help="Total duration in seconds")
    parser.add_argument("--shots", type=int, default=1, help="Number of scenes/keyframes (default: 1)")
    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f"🧘 Zen Studio: Directing 4K Master Video")
    print(f"Theme: {args.theme}")
    print(f"Duration: {args.duration}s | Scenes: {args.shots}")
    print(f"=======================================================\n")

    sb = generate_zen_storyboard(theme=args.theme, duration_seconds=args.duration, num_shots=args.shots)
    producer = ZenStudioProducer()
    result = await producer.produce(sb)

    print("\n=======================================================")
    print("✅ Zen Studio 4K Production Completed Successfully!")
    print(f"Episode ID:  {result['episode_id']}")
    print(f"Master 4K:   {result['master_video_path']}")
    print(f"Keyframes:   {len(result['keyframes'])} images")
    print(f"Soundtrack:  {result['bgm_path']}")
    print(f"Render Time: {result['render_time_seconds']}s")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
