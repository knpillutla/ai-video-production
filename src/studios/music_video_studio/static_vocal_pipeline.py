"""Specialized Pipeline for Static Vocal Music & Lyrical Videos.

Focuses on solo singer portrait with locked tripod framing, atmospheric
particle VFX (bokeh, dust motes, light rays), and center-screen kinetic ASS subtitles.
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


class StaticVocalPipeline(BaseMusicVideoPipeline):
    """Pipeline for static lyrical vocals with locked tripod and particle VFX."""

    pipeline_type: str = "static_vocal"

    async def stage_1_script(
        self, genre: str = "music/static_vocal", sub_genre: Optional[str] = None, primary_archetype: Optional[str] = None, prompt: Optional[str] = None,
        country: Optional[str] = None, language: Optional[str] = None, culture: Optional[str] = None, duration_seconds: float = 60.0,
        num_shots: int = 1, tier: str = "balanced", **kwargs: Any,
    ) -> dict[str, Any]:
        sb_path = self.ep_dir / "storyboard.json"
        if self.is_script_cached():
            logger.info(f"static_vocal_script_reused: {sb_path.name}")
            return json.loads(sb_path.read_text("utf-8"))

        await self.with_retries(
            "stage_1_script",
            lambda: generate_music_video_screenplay(
                genre=genre, sub_genre=sub_genre, primary_archetype=primary_archetype,
                channel_id=self.channel_id, custom_prompt=prompt, duration_seconds=duration_seconds,
                num_shots=num_shots, user_id=self.user_id, country=country, language=language,
                culture=culture, raw_output_path=self.ep_dir / "raw_gemini_screenplay.json", tier=tier,
                **kwargs,
            ),
        )
        return json.loads(sb_path.read_text("utf-8"))

    async def stage_2_keyframes(self, sb_data: dict[str, Any], num_shots: int = 1, force_live: bool = False, use_loras: bool = False, chars: str | list[str] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        cached = sorted([p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000 and not p.name.startswith("scene_000_title")])
        if cached and len(cached) >= num_shots:
            logger.info(f"static_vocal_keyframes_reused: {len(cached)} scenes")
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

        # Generate Scene 0 4K Title Card with 3-line imprint from first generated image
        if img_paths:
            title_p = self.scenes_dir / "scene_000_title.jpg"
            if not title_p.exists() or title_p.stat().st_size < 1000:
                from src.compositor.vocal_title_card import generate_vocal_title_card, resolve_song_mood_label
                eff_lang = sb_data.get("language") or resolve_network_language_and_country(self.channel_id)[0]
                mood_lbl = resolve_song_mood_label(
                    sub_genre=sb_data.get("sub_genre"), mood=sb_data.get("mood"), theme=sb_data.get("hook_thesis"),
                    storyboard_data=sb_data, suno_tags=sb_data.get("suno_tags"), song_type=sb_data.get("song_type"),
                )
                generate_vocal_title_card(
                    base_image_path=img_paths[0],
                    title_localized=sb_data.get("title_localized") or sb_data.get("title_en") or "Song Title",
                    title_en=sb_data.get("title_en") or "Song Title",
                    song_type=mood_lbl, language=eff_lang, output_path=title_p,
                )
            if title_p not in img_paths:
                img_paths = [title_p] + [p for p in img_paths if p != title_p]

        avg_t = float(sb_data.get("duration_seconds", 60.0)) / max(1, len(img_paths))
        return [
            {"name": "Scene 0 (Title)" if p.name.startswith("scene_000_title") else f"Scene {i}", "url": self._file_url(p), "filename": p.name, "timing": f"{avg_t:.1f}s"}
            for i, p in enumerate(img_paths)
        ]

    async def stage_3_audio(self, sb_data: dict[str, Any], duration_seconds: float = 60.0, force_live: bool = False) -> list[dict[str, Any]]:
        raw_audio = self.stems_dir / "raw_soundtrack.mp3"
        if not self.is_audio_cached():
            tags = sb_data.get("suno_tags") or "catchy hummable broadcast master stereo vocal"
            if not any(k in tags.lower() for k in ("catchy", "hummable", "earworm")):
                tags = f"{tags}, catchy hummable melody, memorable earworm hook"
            await self.with_retries(
                "stage_3_audio",
                lambda: SunoMusicAdapter().generate_to_file(
                    output_path=raw_audio, genre=tags,
                    duration_seconds=duration_seconds, lyrics=sb_data.get("lyrics") or "",
                    vocal_gender=sb_data.get("vocal_gender") or "female",
                    title=sb_data.get("title_en") or "Music Track", episode_id=self.episode_id, force_live=force_live,
                ),
            )
        else:
            logger.info(f"static_vocal_audio_reused: {raw_audio.name}")
        return [{"name": "Suno Vocal Soundtrack", "filename": raw_audio.name, "type": "vocal_music", "url": self._file_url(raw_audio), "color": "cyan"}]

    async def stage_4_master_assembly(self, sb_data: dict[str, Any], img_paths: list[Path], audio_path: Path, language: str, duration: float) -> Path:
        renders = sorted([p for p in self.renders_dir.glob("master_*.mp4") if p.stat().st_size > 1000])
        if renders:
            logger.info(f"static_vocal_master_reused: {renders[0].name}")
            return renders[0]

        actual_dur = duration or probe_audio_duration(audio_path)
        out_ass = self.sub_dir / f"kinetic_{language}.ass"
        sub_path, fonts_dir = build_vocal_subtitles(sb_data, language, out_ass, actual_dur, audio_path=audio_path)
        out_render = self.renders_dir / f"master_16x9_ep{self.episode_id}_{language}.mp4"

        # Allocate the first 5 seconds to Scene 0 Title Card with smooth crossfade, or equal time across scenes
        seg_durs = None
        if len(img_paths) > 1 and (img_paths[0].name.startswith("scene_00") or "title" in img_paths[0].name.lower()):
            intro_t = min(5.0, actual_dur * 0.25)
            rem_t = max(1.0, actual_dur - intro_t)
            other_cnt = len(img_paths) - 1
            seg_durs = [intro_t] + [rem_t / other_cnt] * other_cnt
        elif len(img_paths) > 1:
            seg_durs = [actual_dur / len(img_paths)] * len(img_paths)


        return await assemble_vocal_video(
            image_paths=img_paths, song_path=audio_path, sub_path=sub_path, out_video_path=out_render,
            duration=actual_dur, timeline_cues=sb_data.get("animation_timeline"), fonts_dir=fonts_dir,
            enable_vfx=True, theme=sb_data.get("hook_thesis") or sb_data.get("title_en"),
            episode_seed=abs(hash(str(self.episode_id))) % 30, segment_durations=seg_durs,
        )

    async def produce(
        self, genre: str = "music/static_vocal", sub_genre: Optional[str] = None, primary_archetype: Optional[str] = None,
        prompt: Optional[str] = None, country: Optional[str] = None, language: Optional[str] = None,
        culture: Optional[str] = None, duration_seconds: float = 60.0, num_shots: int = 1, tier: str = "balanced",
        script_only: bool = False, photos_only: bool = False, audio_only: bool = False, master_only: bool = False, force_live: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        t0 = time.time()
        eff_shots = max(1, num_shots)
        eff_lang = language or resolve_network_language_and_country(self.channel_id)[0]
        eff_country = country or resolve_network_language_and_country(self.channel_id)[1]
        eff_culture = culture or resolve_culture_for_country_and_language(eff_country, eff_lang)

        # Stage 1: Directorial Scripting
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

        # Stage 2: Keyframes & Scene 0 Title Card
        kfs = await self.stage_2_keyframes(sb_data, num_shots=eff_shots, force_live=force_live)
        if photos_only:
            return self._make_response(sb_data, 2, kfs, [], None, t0, duration_seconds)

        # Stage 3: Audio
        stems = await self.stage_3_audio(sb_data, duration_seconds=duration_seconds, force_live=force_live)
        if audio_only:
            return self._make_response(sb_data, 3, kfs, stems, None, t0, duration_seconds)

        # Stage 4: Assembly (Scene 0 first 5s + Vocal performance + Dynamic VFX)
        img_paths = sorted([p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000])
        audio_path = self.stems_dir / "raw_soundtrack.mp3"
        master_v = await self.stage_4_master_assembly(sb_data, img_paths, audio_path, eff_lang, duration_seconds)

        # Stage 5: Thumbnail & QA (Use Scene 0 4K Title Card directly for high-CTR thumbnail)
        thumb_p = self.thumb_dir / f"thumb_ep{self.episode_id}_{eff_lang}.jpg"
        title_card_p = self.scenes_dir / "scene_000_title.jpg"
        if not thumb_p.exists() or thumb_p.stat().st_size < 1000:
            if title_card_p.exists() and title_card_p.stat().st_size > 1000:
                from src.compositor.vocal_title_card import create_thumbnail_from_title_card
                create_thumbnail_from_title_card(title_card_p, thumb_p)
            else:
                generate_episodic_thumbnail(
                    output_path=thumb_p, base_image_path=img_paths[0] if img_paths else None,
                    badge_config=EpisodicBadgeConfig(episode_number=1, language=eff_lang, style="pill", position="top_left", custom_label=eff_lang.upper()),
                    headline=sb_data.get("title_localized") or sb_data.get("title_en") or "Music Video", enable_vfx=True,
                )

        qa = run_video_qa_audit(master_v, duration_seconds)
        v_url = self._file_url(master_v)
        res = self._make_response(sb_data, 5, kfs, stems, v_url, t0, duration_seconds)
        res["qa_passed"] = qa.passed
        return res
