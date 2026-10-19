"""Specialized Pipeline for Pure Instrumental & Virtuoso Performance Videos.

Focuses on acoustic master recordings with zero vocal tracks, multi-angle camera
transitions (macro close-up on instrument craftsmanship/strings/keys, absorbed musician bhava,
atmospheric wide vistas), and clean broadcast assembly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from src.compositor.vocal_compositor import assemble_vocal_video, build_vocal_subtitles, probe_audio_duration
from src.compositor.vocal_image_service import synthesize_vocal_scenes
from src.core.telemetry import logger
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail
from src.scripts.local_video_qa import run_video_qa_audit
from src.studios.music_video_studio.base_music_pipeline import BaseMusicVideoPipeline
from src.studios.music_video_studio.music_video_director import generate_music_video_screenplay


class InstrumentalPipeline(BaseMusicVideoPipeline):
    """Pipeline for solo virtuoso and jugalbandi instrumental performance videos."""

    pipeline_type: str = "instrumental"

    async def stage_1_script(
        self, genre: str, sub_genre: Optional[str], primary_archetype: Optional[str], prompt: Optional[str],
        country: Optional[str], language: Optional[str], culture: Optional[str], duration_seconds: float,
        num_shots: int = 3, tier: str = "balanced", **kwargs: Any,
    ) -> dict[str, Any]:
        sb_path = self.ep_dir / "storyboard.json"
        if self.is_script_cached():
            logger.info(f"instrumental_script_reused: {sb_path.name}")
            return json.loads(sb_path.read_text("utf-8"))

        eff_shots = max(3, num_shots)
        instr_prompt = f"{prompt or ''} pure instrumental performance, virtuoso musician playing traditional acoustic instrument, zero singing, zero vocals".strip()
        await self.with_retries(
            "stage_1_script",
            lambda: generate_music_video_screenplay(
                genre=genre or "music/instrumental_solo",
                sub_genre=sub_genre or "instrumental_solo",
                primary_archetype=primary_archetype,
                channel_id=self.channel_id,
                custom_prompt=instr_prompt,
                duration_seconds=duration_seconds,
                num_shots=eff_shots,
                user_id=self.user_id,
                country=country,
                language=language,
                culture=culture,
                raw_output_path=self.ep_dir / "raw_gemini_screenplay.json",
                tier=tier,
                **kwargs,
            ),
        )
        return json.loads(sb_path.read_text("utf-8"))

    async def stage_2_keyframes(self, sb_data: dict[str, Any], num_shots: int = 3, force_live: bool = False) -> list[dict[str, Any]]:
        cached = sorted([p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000])
        if cached and len(cached) >= num_shots:
            logger.info(f"instrumental_keyframes_reused: {len(cached)} scenes")
            img_paths = cached
        else:
            img_paths = await self.with_retries(
                "stage_2_keyframes",
                lambda: synthesize_vocal_scenes(
                    storyboard_data=sb_data, scenes_dir=self.scenes_dir, num_images=num_shots,
                    user_id=self.user_id, network=self.channel_id, force_live=force_live,
                    episode_id=self.episode_id, use_loras=True,
                ),
            )
        avg_t = float(sb_data.get("duration_seconds", 60.0)) / max(1, len(img_paths))
        return [{"name": f"Movement {i + 1}", "url": self._file_url(p), "filename": p.name, "timing": f"{avg_t:.1f}s"} for i, p in enumerate(img_paths)]

    async def stage_3_audio(self, sb_data: dict[str, Any], duration_seconds: float = 60.0, force_live: bool = False) -> list[dict[str, Any]]:
        raw_audio = self.stems_dir / "raw_soundtrack.mp3"
        if not self.is_audio_cached():
            tags = f"{sb_data.get('suno_tags') or 'pure instrumental solo, acoustic bansuri flute, resonant sitar, zero vocals'}, audiophile acoustic master"
            await self.with_retries(
                "stage_3_audio",
                lambda: SunoMusicAdapter().generate_to_file(
                    output_path=raw_audio,
                    genre=tags,
                    duration_seconds=duration_seconds,
                    lyrics="",  # Zero lyrics for pure instrumental synthesis
                    vocal_gender="",  # Zero vocal tag prevents phantom vocalizations
                    title=sb_data.get("title_en") or "Instrumental Melody",
                    episode_id=self.episode_id,
                    force_live=force_live,
                ),
            )
        else:
            logger.info(f"instrumental_audio_reused: {raw_audio.name}")
        return [{"name": "Acoustic Instrumental Master", "filename": raw_audio.name, "type": "instrumental_music", "url": self._file_url(raw_audio), "color": "emerald"}]

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
            static_canvas=False, enable_movement=True, scene_movements=["slow_push", "drift-up-right", "dollyout"],
            segment_durations=seg_durs, enable_vfx=False, is_mass=False,
        )

    async def stage_5_thumbnail_and_qa(self, sb_data: dict[str, Any], master_path: Path) -> dict[str, Any]:
        thumb_path = self.thumbs_dir / f"thumb_16x9_ep{self.episode_id}.jpg"
        if not thumb_path.is_file() or thumb_path.stat().st_size < 1000:
            thumb_prompt = sb_data.get("youtube_metadata", {}).get("thumbnail_prompt") or "Virtuoso instrumental musician performing in scenic setting"
            cfg = EpisodicBadgeConfig(network=self.channel_id, episode_num=int(self.episode_id) if str(self.episode_id).isdigit() else 1, title_top="INSTRUMENTAL", title_bottom=sb_data.get("title_en", "Acoustic Solo"))
            generate_episodic_thumbnail(prompt=thumb_prompt, output_path=thumb_path, badge_config=cfg)

        qa_res = run_video_qa_audit(video_path=master_path)
        return {
            "qa": {"status": "passed" if qa_res.get("overall_pass", True) else "flagged", "details": qa_res},
            "thumbnail_url": self._file_url(thumb_path),
            "video_url": self._file_url(master_path),
        }
