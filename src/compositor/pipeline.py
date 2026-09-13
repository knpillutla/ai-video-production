"""Phase 2 End-to-End Video Production Pipeline Coordinator."""

from pathlib import Path
from uuid import UUID

from src.compositor.ffmpeg_pipeline import execute_single_pass_render
from src.compositor.timeline import compile_timeline_from_scenes
from src.core.storage import storage_service
from src.core.telemetry import logger
from src.domain.repo import repo
from src.providers.llm.gemini_adapter import GeminiLLMAdapter
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.providers.tts.azure_speech import AzureSpeechTTSAdapter
from src.providers.visual.together_flux import TogetherFluxAdapter
from src.scripts.local_subtitles import generate_subtitle_bundle


VOICE_MAP = {
    "te": "te-IN-MohanNeural",
    "hi": "hi-IN-MadhurNeural",
    "en": "en-US-ChristopherNeural",
    "es": "es-ES-AlvaroNeural",
}


class ProductionPipelineCoordinator:
    """Orchestrates the 0-GPU end-to-end video synthesis and single-pass FFmpeg render."""

    def __init__(self):
        self.llm = GeminiLLMAdapter()
        self.visual = TogetherFluxAdapter()
        self.tts = AzureSpeechTTSAdapter()
        self.music = SunoMusicAdapter()

    async def produce_episode_master(
        self,
        user_id: UUID,
        episode_id: UUID,
        dry_run: bool = False,
        language: str = "te",
        subtitle_language: str | None = None,
    ) -> Path:
        """Produce a complete broadcast-grade master video for an episode project."""
        episode = repo.get_episode(user_id, episode_id)
        if not episode:
            raise ValueError(f"Episode {episode_id} not found for user {user_id}")

        show = repo.get_show(user_id, episode.show_id)
        show_slug = show.slug if show else "default_universe"

        # Resolve episode workspace directory in user's isolated storage container
        ep_dir = storage_service.get_episode_path(str(user_id), show_slug, str(episode_id))
        scenes_dir = ep_dir / "scenes"
        stems_dir = ep_dir / "audio_stems"
        renders_dir = ep_dir / "master_renders"
        for d in (scenes_dir, stems_dir, renders_dir):
            d.mkdir(parents=True, exist_ok=True)

        logger.info(f"starting_production_pipeline: ep={episode.title}, user={user_id}")

        # 1. Generate Structured Scene Storyboard Plan via Gemini 1.5 Pro
        prompt = f"Write an engaging, high-retention video script on: {episode.title} in {show.genre if show else 'comedy'} genre"
        storyboard_data = await self.llm.generate_structured(prompt)
        scenes_list = storyboard_data.get("scenes", [])

        # 2. Synthesize Visual Keyframes and Voice Stems for each scene
        compiled_scenes = []
        subtitle_segments = []
        current_time = 0.0

        for sc in scenes_list:
            idx = sc.get("scene_index", len(compiled_scenes))
            dur = float(sc.get("duration_seconds", 4.0))
            vis_prompt = sc.get("visual_prompt", f"Scene {idx} for {episode.title}")
            dialogue = sc.get("dialogue", "")

            # Generate keyframe image
            img_path = scenes_dir / f"scene_{idx:02d}.jpg"
            await self.visual.generate_to_file(vis_prompt, output_path=img_path)

            # Generate voiceover stem
            voice_path = stems_dir / f"voice_{idx:02d}.wav"
            voice_id = VOICE_MAP.get(language, "te-IN-MohanNeural")
            await self.tts.synthesize_to_file(dialogue, output_path=voice_path, voice_id=voice_id)

            compiled_scenes.append({
                "scene_index": idx,
                "duration_seconds": dur,
                "image_path": str(img_path),
                "voice_path": str(voice_path),
                "shot_type": sc.get("shot_type", "medium"),
                "dialogue": dialogue,
            })

            subtitle_segments.append({
                "start": current_time,
                "end": current_time + dur,
                "text": dialogue,
            })
            current_time += dur

        # 3. Generate Commercially Cleared Soundtrack via Suno v3.5
        bgm_path = stems_dir / "bgm_master.wav"
        await self.music.generate_to_file(output_path=bgm_path, genre="cinematic comedy", duration_seconds=current_time)

        # 4. Generate Multi-Language Subtitle Bundle (English default on regional content)
        active_sub_lang = subtitle_language or ("en" if language.lower() != "en" else "en")
        subtitles_dir = ep_dir / "subtitles"
        bundle_info = generate_subtitle_bundle(
            base_segments=subtitle_segments,
            base_language=language,
            output_dir=subtitles_dir,
            default_subtitle_lang=active_sub_lang,
        )
        burned_ass_path = bundle_info["burned_ass_path"]

        # 5. Compile Multi-Track Timeline Layout
        timeline = compile_timeline_from_scenes(
            scene_data=compiled_scenes,
            bgm_path=bgm_path,
            subtitle_path=burned_ass_path,
            target_resolution=(1920, 1080),
            fps=30,
        )

        # 6. Execute Single-Pass FFmpeg Compositing
        master_mp4_path = renders_dir / f"master_16x9_ep{episode.episode_number:02d}.mp4"
        final_video = await execute_single_pass_render(
            timeline=timeline,
            output_path=master_mp4_path,
            dry_run=dry_run,
        )

        # 7. Update Episode Entity
        episode.status = "completed"
        episode.master_video_path = str(final_video)
        repo.save_episode(episode)
        logger.info(f"production_pipeline_complete: {final_video}")

        return final_video


pipeline_coordinator = ProductionPipelineCoordinator()

__all__ = ["ProductionPipelineCoordinator", "pipeline_coordinator"]
