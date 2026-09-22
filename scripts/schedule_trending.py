"""CLI Runner for Trending Topics Discovery & Autonomous Video Production."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.telemetry import logger
from src.services.trending_planner import TrendingPlanner
from scripts.produce_video import run_production


async def main():
    parser = argparse.ArgumentParser(description="Trending Video Production & Topic Planner")
    parser.add_argument("--categories", "-c", type=str, default="travel,nature,ocean", help="Comma-separated trending categories (travel, nature, ocean)")
    parser.add_argument("--duration", "-d", type=str, default="1m", help="Target video duration (e.g. 1m, 60s, 15s)")
    parser.add_argument("--tier", "-t", type=str, default="balanced", choices=["draft", "balanced", "cinematic_4k"], help="Quality tier")
    parser.add_argument("--language", "-l", type=str, default="en", help="Narration audio language (default: en)")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of trending videos to produce (default: 1)")
    parser.add_argument("--list-only", action="store_true", help="Discover and display ranked trending topics without producing")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm preflight generation without prompt")
    parser.add_argument("--dry-run", action="store_true", help="Dry run simulation")
    args = parser.parse_args()

    cats = [c.strip() for c in args.categories.split(",") if c.strip()]
    print(f"\n=======================================================")
    print(f" 🔥 TRENDING TOPIC PLANNER: {', '.join(cats).upper()}")
    print(f"=======================================================")
    print(f"[*] Discovering viral, high-CTR topics with zero-repetition and YPP monetization checks...\n")

    planner = TrendingPlanner(language=args.language)
    candidates = await planner.fetch_trending_candidates(categories=cats, max_results=max(args.count * 2, 5))

    if not candidates:
        print("[!] No eligible non-duplicate trending topics found. Try adding more categories.")
        return

    print(f"Found {len(candidates)} monetization-cleared trending topics:\n")
    for idx, cand in enumerate(candidates, 1):
        status_icon = "✅" if cand.monetization_ready else "⚠️"
        print(f"  {idx}. [{cand.category.upper()}] {cand.title}")
        print(f"     - Idea: {cand.idea}")
        print(f"     - Est CTR: {cand.estimated_ctr} | Monetization: {status_icon} Cleared | Sim: {cand.similarity_score:.2f}\n")

    if args.list_only:
        print("[i] List-only mode active. Exiting without generating videos.")
        return

    to_produce = candidates[:args.count]
    print(f"=======================================================")
    print(f" 🎬 STARTING PRODUCTION ({len(to_produce)} EPISODES)")
    print(f"=======================================================")

    for i, item in enumerate(to_produce, 1):
        print(f"\n[Episode {i}/{len(to_produce)}] Producing: {item.title}")
        print(f"Tier: {args.tier.upper()} | Duration: {args.duration} | Language: {args.language.upper()}\n")

        await run_production(
            title=item.title,
            idea=item.idea,
            genre=item.category,
            duration=args.duration,
            language=args.language,
            tier=args.tier,
            auto_confirm=args.yes,
            dry_run=args.dry_run,
        )

    print("\n=======================================================")
    print(" 🎉 ALL TRENDING PRODUCTIONS COMPLETE")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
