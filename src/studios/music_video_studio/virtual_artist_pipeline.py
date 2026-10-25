"""Dedicated Pipeline for Photorealistic Virtual Artist Music Videos (Lara Aredo Style).

Features:
- Solo male, solo female, or duet performances with character LoRA consistency.
- Two master modes:
  * Scenic: wildflower meadows, mountain peaks, valleys, sand dunes, or landmarks.
  * Concert: live stage, mic, instruments, backing orchestra, audience, and 1-2 orchestra cutaways.
- Autonomous Gemini direction of backgrounds, outfits (Rule 12), and natural performance kinematics.
- Natural performance motion synthesis (Wan 2.1 / Kling 1.6 Pro) and beat-synchronized LatentSync lipsync.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

from src.compositor.virtual_artist_service import synthesize_virtual_artist_motion
from src.compositor.vocal_compositor import assemble_vocal_video, build_vocal_subtitles, probe_audio_duration
from src.compositor.vocal_image_service import synthesize_vocal_scenes
from src.core.telemetry import logger
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail
from src.scripts.local_video_qa import run_video_qa_audit
from src.studios.music_video_studio.base_music_pipeline import BaseMusicVideoPipeline
from src.studios.music_video_studio.country_music_catalog import (
    resolve_culture_for_country_and_language,
    resolve_network_language_and_country,
)
from src.studios.music_video_studio.music_video_director import generate_music_video_screenplay


class VirtualArtistPipeline(BaseMusicVideoPipeline):
    """Studio pipeline for photorealistic virtual artist acoustic and concert music videos."""

    pipeline_type: str = "virtual_artist"

    async def stage_1_script(
        self, genre: str, sub_genre: Optional[str], primary_archetype: Optional[str],
        prompt: Optional[str], country: Optional[str], language: Optional[str],
        culture: Optional[str], duration_seconds: float, num_shots: int = 4,
        tier: str = "balanced", artist_mode: str = "scenic", instrument: Optional[str] = None,
        has_orchestra: bool = False, scenic: Optional[str] = None, landmark: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        sb_path = self.ep_dir / "storyboard.json"
        if self.is_script_cached() and not kwargs.get("rescript"):
            logger.info(f"virtual_artist_script_reused: {sb_path.name}")
            return json.loads(sb_path.read_text("utf-8"))

        eff_shots = max(3, num_shots)
        custom_p = (
            f"{prompt or ''} virtual artist performance ({artist_mode} mode), "
            f"instrument: {instrument or 'acoustic_guitar'}, natural singer movements, expressive face"
        ).strip()

        await self.with_retries(
            "stage_1_script",
            lambda: generate_music_video_screenplay(
                genre="music/virtual_artist", sub_genre=sub_genre or "acoustic_ballad",
                primary_archetype=primary_archetype or scenic or "scenic_meadow",
                channel_id=self.channel_id, custom_prompt=custom_p,
                duration_seconds=duration_seconds, num_shots=eff_shots,
                user_id=self.user_id, country=country, language=language,
                culture=culture, raw_output_path=self.ep_dir / "raw_gemini_screenplay.json",
                tier=tier, artist_mode=artist_mode, instrument=instrument,
                has_orchestra=has_orchestra, scenic=scenic, landmark=landmark,
                **kwargs,
            ),
        )
        return json.loads(sb_path.read_text("utf-8"))

    async def stage_2_keyframes(
        self, sb_data: dict[str, Any], num_shots: int = 4, force_live: bool = False,
        use_loras: bool = False, chars: str | list[str] | None = None, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        all_present = all((self.scenes_dir / f"scene_{i:02d}.jpg").is_file() and (self.scenes_dir / f"scene_{i:02d}.jpg").stat().st_size > 1000 for i in range(1, num_shots + 1))
        if all_present:
            logger.info(f"virtual_artist_keyframes_reused: all {num_shots} scenes present on disk")
            img_paths = [self.scenes_dir / f"scene_{i:02d}.jpg" for i in range(1, num_shots + 1)]
        else:
            img_paths = await self.with_retries(
                "stage_2_keyframes",
                lambda: synthesize_vocal_scenes(
                    storyboard_data=sb_data, scenes_dir=self.scenes_dir, num_images=num_shots,
                    user_id=self.user_id, network=self.channel_id, force_live=force_live,
                    episode_id=self.episode_id, use_loras=use_loras, chars=chars,
                    lora_model=kwargs.get("model") or kwargs.get("lora_model") or sb_data.get("model") or sb_data.get("lora_model", "z-image"),
                ),
            )
        avg_t = float(sb_data.get("duration_seconds", 60.0)) / max(1, len(img_paths))
        return [{"name": f"Scene {i + 1}", "url": self._file_url(p), "filename": p.name, "timing": f"{avg_t:.1f}s"} for i, p in enumerate(img_paths)]

    async def stage_3_audio(
        self, sb_data: dict[str, Any], duration_seconds: float = 60.0, force_live: bool = False,
    ) -> list[dict[str, Any]]:
        raw_audio = self.stems_dir / "raw_soundtrack.mp3"
        if not self.is_audio_cached():
            tags = (
                f"{sb_data.get('suno_tags') or 'intimate acoustic guitar and vocal performance, warm broadcast master'}, "
                f"expressive melodic phrasing, natural acoustic presence, radio-ready mix"
            )
            await self.with_retries(
                "stage_3_audio",
                lambda: SunoMusicAdapter().generate_to_file(
                    output_path=raw_audio, genre=tags, duration_seconds=duration_seconds,
                    lyrics=sb_data.get("lyrics") or "", vocal_gender=sb_data.get("vocal_gender") or "female",
                    title=sb_data.get("title_en") or "Acoustic Release", episode_id=self.episode_id,
                    force_live=force_live,
                ),
            )
        else:
            logger.info(f"virtual_artist_audio_reused: {raw_audio.name}")
        return [{"name": "Acoustic Master Track", "filename": raw_audio.name, "type": "vocal_music", "url": self._file_url(raw_audio), "color": "emerald"}]

    async def stage_4_master_assembly(
        self, sb_data: dict[str, Any], img_paths: list[Path], audio_path: Path,
        language: str, duration: float, force_live: bool = False, use_kling: bool = False,
        enable_lipsync: bool = True,
    ) -> Path:
        renders = sorted([p for p in self.renders_dir.glob("master_*.mp4") if p.stat().st_size > 1000])
        if renders:
            return renders[0]

        actual_dur = duration or probe_audio_duration(audio_path)
        motion_map = await synthesize_virtual_artist_motion(
            storyboard_data=sb_data, scenes_dir=self.scenes_dir, audio_path=audio_path,
            use_kling=use_kling, force_live=force_live, episode_id=self.episode_id,
            enable_lipsync=enable_lipsync,
        )

        resolved_scenes = list(img_paths)
        for i, p in enumerate(resolved_scenes):
            sc_idx = i + 1
            if sc_idx in motion_map and motion_map[sc_idx].is_file():
                resolved_scenes[i] = motion_map[sc_idx]

        out_ass = self.sub_dir / f"kinetic_{language}.ass"
        sub_path, fonts_dir = build_vocal_subtitles(sb_data, language, out_ass, actual_dur, audio_path=audio_path)
        out_render = self.renders_dir / f"master_16x9_ep{self.episode_id}_{language}.mp4"

        if sb_data.get("broadcast_timeline"):
            from src.compositor.virtual_artist_broadcast_service import synthesize_broadcast_timeline_clips, assemble_broadcast_cuts
            cuts = await synthesize_broadcast_timeline_clips(
                storyboard_data=sb_data, scenes_dir=self.scenes_dir, audio_path=audio_path,
                motion_map=motion_map, force_live=force_live, episode_id=self.episode_id,
                enable_lipsync=enable_lipsync,
            )
            return await assemble_broadcast_cuts(
                cuts=cuts, song_path=audio_path, sub_path=sub_path,
                out_video_path=out_render, total_duration=actual_dur,
            )

        seg_durs = [actual_dur / len(resolved_scenes)] * len(resolved_scenes) if len(resolved_scenes) > 1 else None

        return await assemble_vocal_video(
            image_paths=resolved_scenes, song_path=audio_path, sub_path=sub_path,
            out_video_path=out_render, duration=actual_dur,
            timeline_cues=sb_data.get("animation_timeline"), fonts_dir=fonts_dir,
            enable_vfx=False, theme=sb_data.get("hook_thesis") or sb_data.get("title_en"),
            episode_seed=abs(hash(str(self.episode_id))) % 30, segment_durations=seg_durs,
        )

    async def produce(
        self, genre: str = "music/virtual_artist", sub_genre: Optional[str] = None,
        primary_archetype: Optional[str] = None, prompt: Optional[str] = None,
        country: Optional[str] = None, language: Optional[str] = None, culture: Optional[str] = None,
        duration_seconds: float = 60.0, num_shots: int = 4, tier: str = "balanced",
        script_only: bool = False, photos_only: bool = False, audio_only: bool = False,
        master_only: bool = False, force_live: bool = False, artist_mode: str = "scenic",
        instrument: Optional[str] = None, has_orchestra: bool = False, scenic: Optional[str] = None,
        landmark: Optional[str] = None, use_kling: bool = False, enable_lipsync: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        t0 = time.time()
        eff_shots = max(3, num_shots)
        eff_lang = language or resolve_network_language_and_country(self.channel_id)[0]
        eff_country = country or resolve_network_language_and_country(self.channel_id)[1]
        eff_culture = culture or resolve_culture_for_country_and_language(eff_country, eff_lang)

        sb_data = await self.stage_1_script(
            genre=genre, sub_genre=sub_genre, primary_archetype=primary_archetype,
            prompt=prompt, country=eff_country, language=eff_lang, culture=eff_culture,
            duration_seconds=duration_seconds, num_shots=eff_shots, tier=tier,
            artist_mode=artist_mode, instrument=instrument, has_orchestra=has_orchestra,
            scenic=scenic, landmark=landmark, **kwargs,
        )
        self._save_user_inputs({
            "prompt": prompt, "channel_id": self.channel_id, "genre": genre,
            "artist_mode": artist_mode, "instrument": instrument, "has_orchestra": has_orchestra,
            "country": eff_country, "language": eff_lang, "culture": eff_culture,
            "duration_seconds": duration_seconds, "num_shots": eff_shots, "tier": tier, **kwargs,
        })
        self._save_manifest(sb_data, duration_seconds, eff_lang, eff_country, genre)
        if script_only:
            return self._make_response(sb_data, 1, [], [], None, t0, duration_seconds)

        kfs = await self.stage_2_keyframes(sb_data, num_shots=eff_shots, force_live=force_live, **kwargs)
        if photos_only:
            return self._make_response(sb_data, 2, kfs, [], None, t0, duration_seconds)

        stems = await self.stage_3_audio(sb_data, duration_seconds=duration_seconds, force_live=force_live)
        if audio_only:
            return self._make_response(sb_data, 3, kfs, stems, None, t0, duration_seconds)

        img_paths = sorted([p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000])
        audio_path = self.stems_dir / "raw_soundtrack.mp3"
        master_v = await self.stage_4_master_assembly(
            sb_data=sb_data, img_paths=img_paths, audio_path=audio_path, language=eff_lang,
            duration=duration_seconds, force_live=force_live, use_kling=use_kling,
            enable_lipsync=enable_lipsync,
        )

        thumb_p = self.thumb_dir / f"thumb_ep{self.episode_id}_{eff_lang}.jpg"
        if not thumb_p.exists() or thumb_p.stat().st_size < 1000:
            generate_episodic_thumbnail(
                output_path=thumb_p, base_image_path=img_paths[0] if img_paths else None,
                badge_config=EpisodicBadgeConfig(episode_number=1, language=eff_lang, style="pill", position="top_left", custom_label=eff_lang.upper()),
                headline=sb_data.get("title_localized") or sb_data.get("title_en") or "Virtual Artist",
                enable_vfx=False,
            )

        qa = run_video_qa_audit(master_v, duration_seconds)
        res = self._make_response(sb_data, 5, kfs, stems, self._file_url(master_v), t0, duration_seconds)
        res["qa_passed"] = qa.passed
        return res


__all__ = ["VirtualArtistPipeline"]
