"""Specialized Pipeline for Mass Song with Mass Beats Productions.

Focuses on explosive high-energy mass commercial dance songs, thumping dappu drums,
teenmaar rhythms, brass drops, whistles, catchy mass hook couplets (Rule 15),
vibrant festive crowd styling, 30fps temporary sharpness, and beat-snapped cuts.
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
from src.studios.music_video_studio.base_music_pipeline import BaseMusicVideoPipeline
from src.studios.music_video_studio.music_video_director import generate_music_video_screenplay


class MassSongPipeline(BaseMusicVideoPipeline):
    """Pipeline for high-energy mass commercial dance songs with thumping mass beats."""

    pipeline_type: str = "mass_song"

    async def stage_1_script(
        self, genre: str, sub_genre: Optional[str], primary_archetype: Optional[str], prompt: Optional[str],
        country: Optional[str], language: Optional[str], culture: Optional[str], duration_seconds: float,
        num_shots: int = 4, tier: str = "balanced", **kwargs: Any,
    ) -> dict[str, Any]:
        sb_path = self.ep_dir / "storyboard.json"
        if self.is_script_cached():
            logger.info(f"mass_song_script_reused: {sb_path.name}")
            return json.loads(sb_path.read_text("utf-8"))

        eff_shots = max(4, num_shots)
        mass_prompt = (
            f"{prompt or ''} explosive high-energy mass commercial dance song with thumping mass beats, "
            f"heavy dappu drums, fast teenmaar rhythm, brass trumpets, whistle drops, catchy mass hook couplets, "
            f"synchronized troupe choreography, energetic dance moves, 138 BPM"
        ).strip()
        await self.with_retries(
            "stage_1_script",
            lambda: generate_music_video_screenplay(
                genre=genre or "music/mass_song", sub_genre=sub_genre or "mass_beats",
                primary_archetype=primary_archetype or "mass_jathara_grounds",
                channel_id=self.channel_id, custom_prompt=mass_prompt, duration_seconds=duration_seconds,
                num_shots=eff_shots, user_id=self.user_id, country=country, language=language,
                culture=culture, raw_output_path=self.ep_dir / "raw_gemini_screenplay.json", tier=tier,
                **kwargs,
            ),
        )
        return json.loads(sb_path.read_text("utf-8"))

    async def stage_2_keyframes(self, sb_data: dict[str, Any], num_shots: int = 4, force_live: bool = False) -> list[dict[str, Any]]:
        cached = sorted([p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000])
        if cached and len(cached) >= num_shots:
            logger.info(f"mass_song_keyframes_reused: {len(cached)} scenes")
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
        return [{"name": f"Mass Beat {i + 1}", "url": self._file_url(p), "filename": p.name, "timing": f"{avg_t:.1f}s"} for i, p in enumerate(img_paths)]

    async def stage_3_audio(self, sb_data: dict[str, Any], duration_seconds: float = 60.0, force_live: bool = False) -> list[dict[str, Any]]:
        raw_audio = self.stems_dir / "raw_soundtrack.mp3"
        if not self.is_audio_cached():
            tags = (
                f"{sb_data.get('suno_tags') or 'catchy hummable mass commercial dance, heavy thumping dappu drums, fast teenmaar rhythm, brass trumpets, whistle drops, explosive earworm hook couplets'}, "
                f"138 bpm, thumping bass downbeats, clean punchy 48khz broadcast master"
            )
            await self.with_retries(
                "stage_3_audio",
                lambda: SunoMusicAdapter().generate_to_file(
                    output_path=raw_audio, genre=tags, duration_seconds=duration_seconds,
                    lyrics=sb_data.get("lyrics") or "", vocal_gender=sb_data.get("vocal_gender") or "male",
                    title=sb_data.get("title_en") or "Mass Song", episode_id=self.episode_id, force_live=force_live,
                ),
            )
        else:
            logger.info(f"mass_song_audio_reused: {raw_audio.name}")
        return [{"name": "Mass Beats Soundtrack", "filename": raw_audio.name, "type": "vocal_music", "url": self._file_url(raw_audio), "color": "orange"}]

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
            enable_vfx=True, theme=sb_data.get("hook_thesis") or sb_data.get("title_en"),
            episode_seed=abs(hash(str(self.episode_id))) % 30, segment_durations=seg_durs,
            enable_movement=True,
        )

    async def produce(
        self, genre: str = "music/mass_song", sub_genre: Optional[str] = "mass_beats",
        primary_archetype: Optional[str] = "mass_jathara_grounds",
        prompt: Optional[str] = None, country: Optional[str] = None, language: Optional[str] = None,
        culture: Optional[str] = None, duration_seconds: float = 60.0, num_shots: int = 4, tier: str = "balanced",
        script_only: bool = False, photos_only: bool = False, audio_only: bool = False, master_only: bool = False, force_live: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        t0 = time.time()
        eff_shots = max(4, num_shots)
        sb_data = await self.stage_1_script(
            genre=genre, sub_genre=sub_genre, primary_archetype=primary_archetype, prompt=prompt,
            country=country, language=language, culture=culture, duration_seconds=duration_seconds,
            num_shots=eff_shots, tier=tier, **kwargs,
        )
        if script_only:
            return {"status": "success", "stage": "script", "elapsed": round(time.time() - t0, 2), "storyboard": sb_data}

        keyframe_manifest = await self.stage_2_keyframes(sb_data, num_shots=eff_shots, force_live=force_live)
        if photos_only:
            return {"status": "success", "stage": "keyframes", "elapsed": round(time.time() - t0, 2), "keyframes": keyframe_manifest}

        audio_manifest = await self.stage_3_audio(sb_data, duration_seconds=duration_seconds, force_live=force_live)
        if audio_only:
            return {"status": "success", "stage": "audio", "elapsed": round(time.time() - t0, 2), "audio": audio_manifest}

        img_paths = sorted([p for p in self.scenes_dir.glob("scene_*.jpg") if p.stat().st_size > 1000])[:eff_shots]
        audio_path = self.stems_dir / "raw_soundtrack.mp3"
        eff_lang = language or sb_data.get("language") or "te"
        master_path = await self.stage_4_master_assembly(sb_data, img_paths, audio_path, eff_lang, duration_seconds)

        return {
            "status": "success", "pipeline": self.pipeline_type, "elapsed": round(time.time() - t0, 2),
            "master_video": str(master_path), "storyboard": sb_data,
        }


__all__ = ["MassSongPipeline"]
