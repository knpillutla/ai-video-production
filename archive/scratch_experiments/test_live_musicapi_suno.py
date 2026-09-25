"""Single live test for MusicAPI.ai / Suno v3.5 Pro integration (Directive 8 - Max 10s test)."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.providers.music.suno_adapter import SunoMusicAdapter


async def test_live_musicapi():
    print("=" * 80)
    print("MUSICAPI.AI / SUNO v3.5 PRO LIVE VALIDATION (SINGLE 10s TEST)")
    print("=" * 80)

    out_file = Path("storage/audio_vault/test_live_suno_10s.wav")
    adapter = SunoMusicAdapter()

    print(f"API Key present: {bool(adapter.api_key)}")
    print(f"Endpoint: {adapter.endpoint}")
    print("Submitting ambient nature request to MusicAPI.ai...")

    try:
        res = await adapter.generate_to_file(
            output_path=out_file,
            genre="ambient nature, meditation, waterfall",
            mood="crystal clear water trickle, soothing flute, peaceful zen",
            duration_seconds=10.0,
            title="Waterfall Pure Zen",
            force_live=True,
        )
        print(f"\n[SUCCESS] Track Generated & Downloaded: {res}")
        print(f"File Size: {res.stat().st_size} bytes")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] MusicAPI test failed: {e}")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_live_musicapi())
