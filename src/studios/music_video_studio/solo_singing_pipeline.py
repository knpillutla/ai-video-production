"""Specialized Pipeline for Solo Singer & Expressive Performance Videos.

Focuses on dynamic multi-angle camera transitions (intimate close-up,
medium stage performance, atmospheric wide), character LoRA consistency,
and vocal performance narrative progression.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

from src.compositor.vocal_compositor import assemble_vocal_video, build_vocal_subtitles, probe_audio_duration
from src.compositor.vocal_image_service import synthesize_vocal_scenes
from src.core.telemetry import logger
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail
from src.scripts.local_video_qa import run_video_qa_audit
from src.studios.music_video_studio.base_music_pipeline import BaseMusicVideoPipeline
from src.studios.music_video_studio.country_music_catalog import resolve_culture_for_country_and_language, resolve_network_language_and_country
from src.studios.music_video_studio.music_video_director import generate_music_video_screenplay


class SoloSingingPipeline(BaseMusicVideoPipeline):
    """Pipeline for solo vocalist expressive performance across multi-angle scenes."""

    pipeline_type: str = "solo_singer"

    async def stage_1_script(
        self, genre: str, sub_genre: Optional[str], primary_archetype: Optional[str], prompt: Optional[str],
        country: Optional[str], language: Optional[str], culture: Optional[str], duration_seconds: float,
        num_shots: int = 3, tier: str = "balanced", **kwargs: Any,
    ) -> dict[str, Any]:
        sb_path = self.ep_dir / "storyboard.json"
        if self.is_script_cached():
            logger.info(f"solo_singing_script_reused: {sb_path.name}")
            return json.loads(sb_path.read_text("utf-8"))

        # Default to multi-angle performance (at least 3 shots)
        eff_shots = max(3, num_shots)
        await self.with_retries(
            "stage_1_script",
            lambda: generate_music_video_screenplay(
                genre=genre or "music/solo_singer", sub_genre=sub_genre, primary_archetype=primary_archetype,
                channel_id=self.channel_id, custom_prompt=prompt, duration_seconds=duration_seconds,
                num_shots=eff_shots, user_id=self.user_id, country=country, language=language,
                culture=culture, raw_output_path=self.ep_dir / "raw_gemini_screenplay.json", tier=tier,
                **kwargs,
            ),
        )
        return json.loads(sb_path.read_text("utf-8"))

    async def stage_2_keyframes(self, sb_data: dict[str, Any], num_shots: int = 3, force_live: bool = False, use_loras: bool = False, chars: str | list[str] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        cached = sorted([p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000])
        if cached and len(cached) >= num_shots:
            logger.info(f"solo_singing_keyframes_reused: {len(cached)} scenes")
            img_paths = cached
        else:
            img_paths = await self.with_retries(
                "stage_2_keyframes",
                lambda: synthesize_vocal_scenes(
                    storyboard_data=sb_data, scenes_dir=self.scenes_dir, num_images=num_shots,
                    user_id=self.user_id, network=self.channel_id, force_live=force_live,
                    episode_id=self.episode_id, use_loras=use_loras, chars=chars,
                ),
            )
        avg_t = float(sb_data.get("duration_seconds", 60.0)) / max(1, len(img_paths))
        return [{"name": f"Angle {i + 1}", "url": self._file_url(p), "filename": p.name, "timing": f"{avg_t:.1f}s"} for i, p in enumerate(img_paths)]

    async def stage_3_audio(self, sb_data: dict[str, Any], duration_seconds: float = 60.0, force_live: bool = False) -> list[dict[str, Any]]:
        raw_audio = self.stems_dir / "raw_soundtrack.mp3"
        if not self.is_audio_cached():
            tags = f"{sb_data.get('suno_tags') or 'catchy hummable expressive solo vocal, studio acoustic mastering'}, memorable earworm hook, emotional melodic progression"
            await self.with_retries(
                "stage_3_audio",
                lambda: SunoMusicAdapter().generate_to_file(
                    output_path=raw_audio, genre=tags, duration_seconds=duration_seconds,
                    lyrics=sb_data.get("lyrics") or "", vocal_gender=sb_data.get("vocal_gender") or "female",
                    title=sb_data.get("title_en") or "Solo Track", episode_id=self.episode_id, force_live=force_live,
                ),
            )
        else:
            logger.info(f"solo_singing_audio_reused: {raw_audio.name}")
        return [{"name": "Solo Vocal Soundtrack", "filename": raw_audio.name, "type": "vocal_music", "url": self._file_url(raw_audio), "color": "cyan"}]

    async def stage_4_master_assembly(self, sb_data: dict[str, Any], img_paths: list[Path], audio_path: Path, language: str, duration: float) -> Path:
        renders = sorted([p for p in self.renders_dir.glob("master_*.mp4") if p.stat().st_size > 1000])
        if renders:
            return renders[0]

        actual_dur = duration or probe_audio_duration(audio_path)
        out_ass = self.sub_dir / f"kinetic_{language}.ass"
        sub_path, fonts_dir = build_vocal_subtitles(sb_data, language, out_ass, actual_dur, audio_path=audio_path)
        out_render = self.renders_dir / f"master_16x9_ep{self.episode_id}_{language}.mp4"
        seg_durs = [actual_dur / len(img_paths)] * len(img_paths) if len(img_paths) > 1 else None

        return await assemble_vocal_video(
            image_paths=img_paths, song_path=audio_path, sub_path=sub_path, out_video_path=out_render,
            duration=actual_dur, timeline_cues=sb_data.get("animation_timeline"), fonts_dir=fonts_dir,
            enable_vfx=False, theme=sb_data.get("hook_thesis") or sb_data.get("title_en"),
            episode_seed=abs(hash(str(self.episode_id))) % 30, segment_durations=seg_durs,
        )


    async def produce(
        self, genre: str = "music/solo_singer", sub_genre: Optional[str] = None, primary_archetype: Optional[str] = None,
        prompt: Optional[str] = None, country: Optional[str] = None, language: Optional[str] = None,
        culture: Optional[str] = None, duration_seconds: float = 60.0, num_shots: int = 3, tier: str = "balanced",
        script_only: bool = False, photos_only: bool = False, audio_only: bool = False, master_only: bool = False, force_live: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        t0 = time.time()
        eff_shots = max(3, num_shots)
        eff_lang = language or resolve_network_language_and_country(self.channel_id)[0]
        eff_country = country or resolve_network_language_and_country(self.channel_id)[1]
        eff_culture = culture or resolve_culture_for_country_and_language(eff_country, eff_lang)

        sb_data = await self.stage_1_script(
            genre=genre, sub_genre=sub_genre, primary_archetype=primary_archetype, prompt=prompt,
            country=eff_country, language=eff_lang, culture=eff_culture, duration_seconds=duration_seconds,
            num_shots=eff_shots, tier=tier, **kwargs,
        )
        self._save_user_inputs({
            "prompt": prompt, "channel_id": self.channel_id, "genre": genre, "sub_genre": sub_genre,
            "country": eff_country, "language": eff_lang, "culture": eff_culture, "duration_seconds": duration_seconds,
            "num_shots": eff_shots, "tier": tier, **kwargs,
        })
        self._save_manifest(sb_data, duration_seconds, eff_lang, eff_country, genre)
        if script_only:
            return self._make_response(sb_data, 1, [], [], None, t0, duration_seconds)

        kfs = await self.stage_2_keyframes(sb_data, num_shots=eff_shots, force_live=force_live)
        if photos_only:
            return self._make_response(sb_data, 2, kfs, [], None, t0, duration_seconds)

        stems = await self.stage_3_audio(sb_data, duration_seconds=duration_seconds, force_live=force_live)
        if audio_only:
            return self._make_response(sb_data, 3, kfs, stems, None, t0, duration_seconds)

        img_paths = sorted([p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000])
        audio_path = self.stems_dir / "raw_soundtrack.mp3"
        master_v = await self.stage_4_master_assembly(sb_data, img_paths, audio_path, eff_lang, duration_seconds)

        thumb_p = self.thumb_dir / f"thumb_ep{self.episode_id}_{eff_lang}.jpg"
        if not thumb_p.exists() or thumb_p.stat().st_size < 1000:
            generate_episodic_thumbnail(
                output_path=thumb_p, base_image_path=img_paths[0] if img_paths else None,
                badge_config=EpisodicBadgeConfig(episode_number=1, language=eff_lang, style="pill", position="top_left", custom_label=eff_lang.upper()),
                headline=sb_data.get("title_localized") or sb_data.get("title_en") or "Solo Singer", enable_vfx=False,
            )

        qa = run_video_qa_audit(master_v, duration_seconds)
        v_url = self._file_url(master_v)
        res = self._make_response(sb_data, 5, kfs, stems, v_url, t0, duration_seconds)
        res["qa_passed"] = qa.passed
        return res
