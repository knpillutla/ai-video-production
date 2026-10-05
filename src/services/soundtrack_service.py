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
from src.services.cultural_acoustic_service import resolve_cultural_acoustic_profile


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
        archetype: Optional[str] = None,
        force_rerun: bool = False,
        prompt: Optional[str] = None,
    ) -> Path:
        """Fetch matching acoustic stem from AudioVault (respecting cultural keys & 10-video cooldown) or synthesize via Suno."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if not force_rerun and out_path.is_file() and out_path.stat().st_size > 1000:
            logger.info(f"decision_soundtrack_disk_cache_hit: Reusing {out_path.name} ($0.00 spend)")
            print(f"[DECISION - SOUNDTRACK CACHE HIT] Soundscape exists on disk ({out_path.name}). Reusing asset ($0.00 spend).")
            return out_path

        profile = resolve_cultural_acoustic_profile(
            archetype=archetype or "",
            sub_genre=genre,
            title=title,
            tags=tags,
        )

        eff_prompt = prompt.strip() if prompt and prompt.strip() else profile.suno_prompt
        clean_tags = tags.strip() if tags and tags.strip() and "guitar" not in tags.lower() else profile.suno_tags

        # Rule 3 Tier 1 & 3: AudioVault Local Stem Cache Check with Cultural Key Isolation ($0.00 spend)
        if not force_rerun:
            cached = audio_vault.find_matching_stem(
                genre=f"{genre} {profile.culture_key}",
                theme=title,
                concept=profile.lead_instrument,
                tags=f"{clean_tags} {profile.culture_key}",
                min_similarity=0.70,
                current_episode_id=episode_id,
                min_cooldown=min_cooldown,
            )
            if cached and cached.is_file() and cached.stat().st_size > 1000:
                shutil.copy2(cached, out_path)
                logger.info(f"decision_audiovault_cache_hit: Matched stem '{cached.name}' ({profile.culture_key}: {profile.lead_instrument}) ($0.00 spend)")
                print(f"[DECISION - AUDIOVAULT CACHE HIT] Reusing vault stem '{cached.name}' ({profile.lead_instrument}) ($0.00 spend).")
                return out_path

        logger.info(f"decision_audio_invoke_suno: Synthesizing fresh cultural anti-fatigue soundscape [{profile.culture_key.upper()} - {profile.lead_instrument}] via Suno v3.5 Pro...")
        print(f"[DECISION - SUNO CULTURAL SYNTHESIS] Synthesizing {profile.culture_key.upper()} soundscape: {profile.lead_instrument} ({profile.scale_and_tuning}, {profile.rhythm_and_tempo})...")
        adapter = SunoMusicAdapter()

        await adapter.generate_to_file(
            output_path=out_path,
            genre=f"{genre}, {profile.culture_key}, {profile.scale_and_tuning}, {profile.lead_instrument}",
            mood=clean_tags[:120],
            duration_seconds=total_duration,
            lyrics=eff_prompt,
            vocal_gender="none",
            title=title,
            episode_id=episode_id,
            force_live=force_rerun,
        )

        if out_path.is_file() and out_path.stat().st_size > 1000:
            audio_vault.register_stem(
                source_path=out_path,
                genre=f"{genre} {profile.culture_key}",
                theme=title,
                concept=profile.lead_instrument,
                tags=f"{tags}, {profile.culture_key}, {profile.lead_instrument}",
                vocal_gender="none",
                episode_id=episode_id,
            )
        return out_path


soundtrack_service = SoundtrackService()

__all__ = ["SoundtrackService", "soundtrack_service"]
