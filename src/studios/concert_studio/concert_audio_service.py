"""Standalone Concert Audio Synthesis Service.

Synthesizes 48kHz broadcast master audio with Suno v3.5 Pro using Gemini lyrics.
Features:
- Rule 3 Universal Artifact Caching: reuses existing audio ($0.00 spend).
- Fail-Fast Enforcement: If Suno fails (e.g. HTTP 403 insufficient credits),
  immediately raises RuntimeError and halts pipeline to prevent wasting downstream video credits.
- Zero procedural foley fallback for live concerts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.compliance.rights_ledger import AssetType, CommercialLicenseType, rights_ledger
from src.core.telemetry import logger
from src.providers.music.suno_adapter import SunoMusicAdapter


async def synthesize_concert_audio(
    storyboard_data: dict[str, Any],
    stems_dir: Path,
    duration_seconds: float = 60.0,
    title: str = "Concert Anthem",
    episode_id: Any = None,
    force_live: bool = False,
    language: str = "te",
    is_soft: bool = False,
) -> Path:
    """Synthesize concert audio with fail-fast guarantee and zero foley degradation."""
    stems_dir.mkdir(parents=True, exist_ok=True)
    audio_path = stems_dir / "music_master.mp3"

    # Rule 3 Tier 1: Check existing cached audio
    if audio_path.is_file() and audio_path.stat().st_size > 50_000:
        logger.info(f"concert_audio_reused: {audio_path.name} ({audio_path.stat().st_size} bytes, $0.00 spend)")
        print(f"[+] Stage 2: Reusing existing concert audio: {audio_path.name} ($0.00 spend)")
        return audio_path

    print(f"[~] Stage 2: Synthesizing concert music with Suno v3.5...")
    vocal_gender = str(storyboard_data.get("vocal_gender") or "female").lower()
    if "male" in vocal_gender and "fe" not in vocal_gender:
        vocal_tag = "male vocals, deep energetic hero vocals"
        eff_vocal_gender = "male"
    else:
        vocal_tag = "female vocals, sweet melodic vocal delivery"
        eff_vocal_gender = "female"

    suno_base = storyboard_data.get("suno_tags", "live concert strings")
    suno_base = suno_base.replace("female vocals", "").replace("male vocals", "").strip(", ")

    instrument = str(storyboard_data.get("instrument") or "").lower()
    has_custom_inst = instrument not in ("", "mic", "none", "vocal", "vocals")
    inst_name = instrument.replace("_", " ")
    inst_prefix = f"virtuosic {inst_name} solos, expressive {inst_name} leads, " if (has_custom_inst and inst_name not in suno_base.lower()) else ""

    if is_soft:
        tags = f"{vocal_tag}, {inst_prefix}{suno_base}, soulful melody, warm concert atmosphere, 48khz broadcast master"
    else:
        tags = f"{vocal_tag}, {inst_prefix}{suno_base}, high-energy concert anthem, 128 bpm, 48khz broadcast master"

    lyrics = storyboard_data.get("lyrics", "")
    song_title = storyboard_data.get("title_en", title)

    try:
        await SunoMusicAdapter().generate_to_file(
            output_path=audio_path,
            genre=tags,
            duration_seconds=int(duration_seconds),
            lyrics=lyrics,
            vocal_gender=eff_vocal_gender,
            title=song_title,
            episode_id=episode_id,
            force_live=force_live,
        )
    except Exception as suno_err:
        logger.error(f"suno_concert_generation_failed: {suno_err}")
        # Fail-fast: Stop execution immediately so user can recharge credits
        raise RuntimeError(
            f"❌ Suno Music Generation failed: {suno_err}\n"
            f"Halting concert production immediately to prevent wasting downstream Fal/Wan video generation credits. "
            f"Please check your Suno account credits and resume with '--id <episode_id>'."
        ) from suno_err

    if not (audio_path.is_file() and audio_path.stat().st_size > 1000):
        raise RuntimeError(f"Suno failed to produce valid audio file at: {audio_path}")

    if episode_id:
        rights_ledger.record_asset(
            episode_id, AssetType.MUSIC, str(audio_path), "Suno", "v3.5-pro",
            CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP, f"CONCERT-AUDIO-{episode_id}", True,
        )

    logger.info(f"concert_audio_synthesized: {audio_path.name} ({audio_path.stat().st_size} bytes)")
    return audio_path


__all__ = ["synthesize_concert_audio"]
