"""Unified Soundtrack & BGM Audio Synthesis Service.

Encapsulates AudioVault acoustic stem caching, dynamic Suno v3.5 Pro synthesis,
and automatic stem registration for zero redundant music spend.
"""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import Optional

from src.core.telemetry import logger
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.services.audio_vault import audio_vault


class SoundtrackService:
    """Universal soundtrack generator with AudioVault caching and Suno v3.5 Pro synthesis."""

    async def synthesize_ambient_soundtrack(
        self,
        title: str,
        tags: str,
        out_path: Path,
        total_duration: float = 60.0,
        genre: str = "ambient relaxation",
        episode_id: Optional[str] = None,
        min_cooldown: int = 10,
    ) -> Path:
        """Fetch matching acoustic stem from AudioVault (respecting 10-video cooldown) or synthesize via Suno."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.is_file() and out_path.stat().st_size > 1000:
            logger.info(f"decision_soundtrack_disk_cache_hit: Reusing {out_path.name} ($0.00 spend)")
            print(f"[DECISION - SOUNDTRACK CACHE HIT] Soundscape exists on disk ({out_path.name}). Reusing asset ($0.00 spend).")
            return out_path

        # Rule 3 Tier 1 & 3: AudioVault Local Stem Cache Check ($0.00 spend)
        cached = audio_vault.find_matching_stem(
            genre=genre, theme=title, concept=title, tags=tags, min_similarity=0.70,
            current_episode_id=episode_id, min_cooldown=min_cooldown,
        )
        if cached and cached.is_file() and cached.stat().st_size > 1000:
            shutil.copy2(cached, out_path)
            logger.info(f"decision_audiovault_cache_hit: Matched stem '{cached.name}' ($0.00 spend)")
            print(f"[DECISION - AUDIOVAULT CACHE HIT] Reusing existing vault stem '{cached.name}' ($0.00 spend).")
            return out_path

        logger.info(f"decision_audio_invoke_suno: Synthesizing fresh anti-fatigue soundscape via Suno v3.5 Pro...")
        print(f"[DECISION - SUNO SYNTHESIS] Synthesizing broadcast-grade anti-fatigue soundscape via Suno v3.5 Pro...")
        adapter = SunoMusicAdapter()
        meditative_prompt = (
            "[Instrumental Ambient Meditation]\n"
            "[432Hz Solfeggio Velvet Resonance]\n"
            "[Joyful Uplifting Handpan & Singing Bowls]\n"
            "[Warm Velvet Ambient Pads & Celtic Harp]\n"
            "[Airy Nay Flute & Serene Soundbath]\n"
            "[Deep De-stressing & Restful Sleep Drone]\n"
            "[Outro: Infinite Peaceful Fade]"
        )
        ambient_tags = (
            f"432hz meditation, joyful handpan, singing bowls, velvet synth pads, "
            f"celtic harp, {tags}, deep stress relief, sleep drone, zero solo guitar, -21 LUFS"
        )
        await adapter.generate_to_file(
            output_path=out_path,
            genre=f"{genre}, 432hz harmonic resonance, soothing joyful velvet pads, zero solo guitar, zero harshness",
            mood=ambient_tags[:120],
            duration_seconds=total_duration,
            lyrics=meditative_prompt,
            vocal_gender="none",
            title=title,
            episode_id=episode_id,
            force_live=False,
        )

        if out_path.is_file() and out_path.stat().st_size > 1000:
            audio_vault.register_stem(
                source_path=out_path,
                genre=genre,
                theme=title,
                concept="ambient soundscape",
                tags=tags,
                vocal_gender="none",
                episode_id=episode_id,
            )
        return out_path


soundtrack_service = SoundtrackService()

__all__ = ["SoundtrackService", "soundtrack_service"]
