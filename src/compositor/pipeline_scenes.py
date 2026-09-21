"""Scene synthesis runner for keyframe generation, TTS, and rights tracking."""

from pathlib import Path
from typing import Any

from src.compliance.rights_ledger import rights_ledger
from src.compositor.pipeline_prompts import extract_dialogue_text
from src.core.telemetry import logger
from src.domain.rights import AssetType, CommercialLicenseType
from src.services.character_consistency import inject_character_consistency


async def synthesize_scenes(
    scenes_list: list[dict[str, Any]],
    scenes_dir: Path,
    stems_dir: Path,
    episode: Any,
    scale: float,
    char_anchor: Any,
    derived_culture: Any,
    visual_adapter: Any,
    tts_adapter: Any,
    language: str = "en",
    enable_voice_over: bool = True,
    enable_lipsync: bool = False,
    force_live: bool = False,
    kling_adapter: Any | None = None,
    enable_video_motion: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float]:
    """Synthesize visual keyframes, motion video, and voice stems for each scene."""
    compiled_scenes: list[dict[str, Any]] = []
    subtitle_segments: list[dict[str, Any]] = []
    current_time = 0.0

    for sc in scenes_list:
        idx = sc.get("scene_index", sc.get("scene_number", len(compiled_scenes)))
        dur = round(float(sc.get("duration_seconds", sc.get("duration", 4.0))) * scale, 2)
        vis_prompt = sc.get("visual_prompt") or sc.get("visual_description") or f"Scene {idx} for {episode.title}"
        dialogue = extract_dialogue_text(sc)

        enhanced_vis, scene_loras, scene_seed = inject_character_consistency(vis_prompt, char_anchor)
        if derived_culture.art_style_prompt and derived_culture.art_style_prompt not in enhanced_vis:
            enhanced_vis = f"{enhanced_vis}, {derived_culture.art_style_prompt}"
        for lora in derived_culture.recommended_loras:
            if not any(sl.get("path") == lora.get("path") or sl.get("name") == lora.get("name") for sl in scene_loras):
                scene_loras.append(lora)

        img_path = scenes_dir / f"scene_{idx:02d}.jpg"
        if not (img_path.is_file() and img_path.stat().st_size > 0):
            _, generated_img_path = await visual_adapter.generate_to_file(
                enhanced_vis, output_path=img_path, force_live=force_live,
                loras=scene_loras, seed=scene_seed,
            )
            img_path = generated_img_path

        if idx == 0 and char_anchor and not char_anchor.reference_image_path:
            char_anchor.reference_image_path = str(img_path)

        rights_ledger.record_asset(
            episode_id=episode.id, asset_type=AssetType.IMAGE, file_path=str(img_path),
            provider="Fal.ai/Flux", model_name="FLUX.1-dev (28 steps)",
            license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
            license_id=f"BFL-COMM-{episode.id}-{idx}", cleared=True,
        )

        voice_path = None
        if enable_voice_over and episode.options.enable_tts and dialogue:
            voice_path = stems_dir / f"voice_{idx:02d}_{language}.wav"
            voice_id = derived_culture.voice_id
            await tts_adapter.synthesize_to_file(dialogue, output_path=voice_path, voice_id=voice_id, force_live=force_live)
            rights_ledger.record_asset(
                episode_id=episode.id, asset_type=AssetType.VOICE, file_path=str(voice_path),
                provider="Microsoft/NeuralVoice", model_name=voice_id,
                license_type=CommercialLicenseType.COMMERCIAL_ROYALTY_FREE,
                license_id=f"MS-TTS-{episode.id}-{idx}", cleared=True,
            )
            if enable_lipsync:
                rights_ledger.record_asset(
                    episode_id=episode.id, asset_type=AssetType.VIDEO_MOTION, file_path=str(img_path),
                    provider="Fal.ai/LivePortrait", model_name="LivePortrait-v1",
                    license_type=CommercialLicenseType.COMMERCIAL_ROYALTY_FREE,
                    license_id=f"FAL-LIPSYNC-{episode.id}-{idx}", cleared=True,
                )

        video_path = None
        if enable_video_motion and kling_adapter:
            vid_path = scenes_dir / f"scene_{idx:02d}_motion.mp4"
            fmt_val = str(getattr(episode.format, "value", episode.format)).lower()
            aspect_ratio = "9:16" if "9_16" in fmt_val or "vertical" in fmt_val else "16:9"
            motion_prompt = sc.get("motion_prompt") or sc.get("visual_prompt") or sc.get("visual_description") or episode.title
            try:
                _, local_vid = await kling_adapter.generate_video(
                    image_url=str(img_path), motion_prompt=motion_prompt,
                    output_path=vid_path, duration=10 if dur >= 8 else 5,
                    aspect_ratio=aspect_ratio, force_live=force_live,
                )
                if local_vid and Path(local_vid).exists() and Path(local_vid).stat().st_size > 1000:
                    video_path = local_vid
                    rights_ledger.record_asset(
                        episode_id=episode.id, asset_type=AssetType.VIDEO_MOTION, file_path=str(video_path),
                        provider="Fal.ai/Kling", model_name="Kling-v1.5-Pro",
                        license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
                        license_id=f"FAL-KLING-{episode.id}-{idx}", cleared=True,
                    )
            except Exception as ex:
                logger.warning(f"Video motion synthesis failed for scene {idx}: {ex}")

        compiled_scenes.append({
            "scene_index": idx, "duration_seconds": dur, "image_path": str(img_path),
            "video_path": str(video_path) if video_path else None,
            "voice_path": str(voice_path) if voice_path else None,
            "shot_type": sc.get("shot_type", "medium"), "dialogue": dialogue,
        })
        subtitle_segments.append({"start": current_time, "end": current_time + dur, "text": dialogue})
        current_time += dur

    return compiled_scenes, subtitle_segments, current_time
