"""Documentary Studio Multi-Genre Production Pipeline CLI.

Supports 6 Blue-Chip Genres: Wildlife, Ocean, Nature, Mountains, Art, Ancient Structures.
Enforces Western Male voice default, --female-voice, multilingual (--lang te/hi),
fatigue-free audio ducking, dynamic scene-based AI model routing, and 4-Stage review gates.
"""

import argparse
import asyncio
from pathlib import Path
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.telemetry import logger
from src.studios.documentary_studio.doc_producer import DocumentaryProducer
from src.studios.documentary_studio.doc_storyboard import DocGenre, generate_documentary_storyboard


async def run_documentary_production(
    genre: str = "wildlife",
    custom_prompt: str | None = None,
    episode_id: str | None = None,
    female_voice: bool = False,
    language: str = "en",
    include_bgm: bool = False,
    photos_only: bool = False,
    motion_model: str = "auto",
    duration: float = 60.0,
    allow_fallback: bool = False,
):
    """Run full documentary production workflow."""
    doc_genre = DocGenre(genre)
    sb = generate_documentary_storyboard(
        genre=doc_genre,
        custom_prompt=custom_prompt,
        duration_seconds=duration,
        language=language,
    )

    producer = DocumentaryProducer()
    print("\n" + "=" * 70)
    print(f"[DOCUMENTARY PRODUCTION INITIALIZED]")
    print(f"   * Genre:       {genre.upper()}")
    print(f"   * Title:       {sb.title}")
    print(f"   * Narrator:    {'Female' if female_voice else 'Male (Default Western)'} [{language.upper()}]")
    print(f"   * Audio Mode:  {'Narration + Subtle BGM (-26dB)' if include_bgm else 'Pure Narration (Zero Ear Fatigue)'}")
    print(f"   * Target Dur:  {duration}s ({len(sb.scenes)} Scenes)")
    print("=" * 70)

    result = await producer.produce(
        sb=sb,
        episode_id=episode_id,
        motion_model=motion_model,
        female_voice=female_voice,
        include_bgm=include_bgm,
        photos_only=photos_only,
        allow_fallback=allow_fallback,
    )

    ep_id = result["episode_id"]
    if photos_only:
        print("\n" + "=" * 70)
        print(f"[STAGE 1 COMPLETE] 4K KEYFRAME PHOTOS READY ({len(result['keyframes'])} Images)!")
        print(f"Episode ID:  {ep_id}")
        for idx, kf in enumerate(result["keyframes"], 1):
            print(f"Scene {idx} Photo: {kf}")
        print(f"\n[NEXT STEPS] To synthesize motion & voiceover from these photos, run:")
        print(f"   python scripts/channels/documentary_pipeline.py --id {ep_id}")
        print("=" * 70 + "\n")
        return result

    master_path = Path(result["master_video_path"])
    print("\n" + "=" * 70)
    print(f"[STAGE 2 COMPLETE] 4K DOCUMENTARY MASTER READY!")
    print(f"Episode ID:     {ep_id}")
    print(f"Master Video:   {master_path.resolve()}")
    print(f"Voiceover WAV:  {result.get('voiceover_path')}")
    print(f"Subtitles SRT:  {result.get('subtitles_path')}")
    print("=" * 70 + "\n")
    return result


async def main():
    parser = argparse.ArgumentParser(description="Documentary Studio Production Pipeline")
    parser.add_argument("--genre", type=str, default="wildlife", choices=["wildlife", "ocean", "nature", "mountains", "art", "ancient_structures"], help="Documentary archetype")
    parser.add_argument("--id", type=str, default=None, help="Episode ID to resume or reuse cached artifacts")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="Custom documentary subject/location (e.g. 'Galapagos Marine Iguanas', 'Gothic Cathedrals')")
    parser.add_argument("--female-voice", action="store_true", help="Use female natural history narrator (defaults to Western male)")
    parser.add_argument("--lang", type=str, default="en", help="Narration language code (en=English, te=Telugu, hi=Hindi, es=Spanish)")
    parser.add_argument("--bgm", action="store_true", help="Include subtle, low-ducked orchestral BGM (-26dB)")
    parser.add_argument("--photos-only", action="store_true", help="Stage 1: Generate keyframe photos only for review")
    parser.add_argument("--motion-model", type=str, default="auto", choices=["auto", "kling_v3", "wan", "hunyuan", "kling"], help="Motion model override (default: auto -> best scene routing)")
    parser.add_argument("--duration", type=float, default=60.0, choices=[60.0, 90.0, 120.0], help="Master documentary duration in seconds")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow zoom-pan fallback if live diffusion fails")
    args = parser.parse_args()

    await run_documentary_production(
        genre=args.genre,
        custom_prompt=args.prompt,
        episode_id=args.id,
        female_voice=args.female_voice,
        language=args.lang,
        include_bgm=args.bgm,
        photos_only=args.photos_only,
        motion_model=args.motion_model,
        duration=args.duration,
        allow_fallback=args.allow_fallback,
    )


if __name__ == "__main__":
    asyncio.run(main())
