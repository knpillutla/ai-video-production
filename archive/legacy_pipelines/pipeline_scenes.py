import asyncio
from pathlib import Path
from typing import Any

from src.cinematics.continuity.environmental_state import environmental_state_tracker
from src.compliance.rights_ledger import rights_ledger
from src.compositor.ffmpeg_pipeline import get_audio_duration, get_ffmpeg_binary
from src.compositor.pipeline_prompts import extract_dialogue_text
from src.core.telemetry import logger
from src.domain.rights import AssetType, CommercialLicenseType
from src.scripts.image_quality_gate import ImageQualityGateDecision, execute_image_quality_gate
from src.scripts.local_pan_zoom import assign_scene_camera_movement, render_steadycam_clip
from src.services.character_consistency import inject_character_consistency


class RecreateScriptRequested(Exception):
    """Signal indicating user requested full script & storyboard recreation at image gate."""
    pass


class PipelineCancelled(Exception):
    """Signal indicating user cancelled production at the image quality gate."""
    pass


def derive_weather_motion_cues(cues: str) -> str:
    """Extract and synthesize kinetic atmospheric, thermal, and precipitation physics prompts."""
    c = cues.lower()
    if any(k in c for k in ("blizzard", "snowstorm", "heavy snow", "gale", "arctic storm")):
        return "intense swirling blizzard gusts, blowing powder snow whipping past, foot-stomps kicking up snow drifts, "
    if any(k in c for k in ("snow", "snowing", "snowfall", "flurry", "flurries", "winter", "frost")):
        return "soft delicate crystalline snowflakes drifting and floating gently down through the air, "
    if any(k in c for k in ("heavy rain", "downpour", "torrential", "storm", "monsoon", "deluge")):
        return "sheets of heavy rainfall actively pouring down through the air, visible rain streaks, "
    if any(k in c for k in ("rain", "drizzle", "shower", "rainy", "wet street", "puddle")):
        return "fine delicate raindrops gently falling through the air, visible rain streaks, "
    if any(k in c for k in ("hot sun", "fiery sun", "scorching", "heatwave", "desert heat", "blazing sun")):
        return "shimmering atmospheric heat waves rising from the ground, intense radiant sunbeams, "
    if any(k in c for k in ("fog", "foggy", "mist", "misty", "haze")):
        return "rolling tendrils of atmospheric mist and fog drifting slowly across the path, "
    if any(k in c for k in ("cloudy evening", "sunset", "twilight", "dusk")):
        return "dramatic shifting evening clouds across the colorful twilight sky, soft sunset breeze, "
    if any(k in c for k in ("cloudy", "overcast", "grey sky", "clouds")):
        return "dynamic low-hanging clouds slowly shifting and drifting across the overcast sky, "
    if any(k in c for k in ("autumn", "falling leaves", "foliage", "windy", "breeze")):
        return "crisp breeze causing golden leaves to swirl and flutter down through the air, "
    return ""


async def _generate_single_keyframe(
    idx: int, sc: dict[str, Any], scenes_dir: Path, episode: Any,
    char_anchor: Any, derived_culture: Any, visual_adapter: Any,
    force_live: bool, total_scenes: int, img_sem: asyncio.Semaphore,
) -> tuple[Path, bool]:
    """Synthesize or load a single keyframe image for a scene."""
    vis_prompt = sc.get("visual_prompt") or sc.get("visual_description") or f"Scene {idx} for {episode.title}"
    enhanced_vis, scene_loras, scene_seed = inject_character_consistency(vis_prompt, char_anchor)
    env_state = environmental_state_tracker.compute_scene_environmental_state(
        scene_index=idx, total_scenes=total_scenes,
        weather=getattr(derived_culture, "weather_condition", "clear_daylight"),
        space=getattr(derived_culture, "environment_space", "outdoor"),
    )
    if env_state.get("environmental_prompt") and env_state["environmental_prompt"] not in enhanced_vis:
        enhanced_vis = f"{enhanced_vis}, {env_state['environmental_prompt']}"
    if derived_culture.art_style_prompt and derived_culture.art_style_prompt not in enhanced_vis:
        enhanced_vis = f"{enhanced_vis}, {derived_culture.art_style_prompt}"
    for lora in getattr(derived_culture, "recommended_loras", []):
        if not any(sl.get("path") == lora.get("path") or sl.get("name") == lora.get("name") for sl in scene_loras):
            scene_loras.append(lora)

    img_path = scenes_dir / f"scene_{idx:02d}.jpg"
    recreated = False
    async with img_sem:
        if not (img_path.is_file() and img_path.stat().st_size > 0):
            _, generated_img_path = await visual_adapter.generate_to_file(
                enhanced_vis, output_path=img_path, force_live=force_live,
                loras=scene_loras, seed=scene_seed,
            )
            img_path = generated_img_path
            recreated = True

    if idx == 0 and char_anchor and not getattr(char_anchor, "reference_image_path", None):
        char_anchor.reference_image_path = str(img_path)

    rights_ledger.record_asset(
        episode_id=episode.id, asset_type=AssetType.IMAGE, file_path=str(img_path),
        provider="Fal.ai/Flux", model_name="FLUX.1-dev (28 steps)",
        license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
        license_id=f"BFL-COMM-{episode.id}-{idx}", cleared=True,
    )
    return img_path, recreated


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
    auto_confirm: bool = False,
    custom_gate_input_fn: Any = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float]:
    """Synthesize visual keyframes with interactive quality gate review before motion & stems."""
    img_results: dict[int, tuple[Path, bool]] = {}
    voice_results: dict[int, Path | None] = {}
    motion_sem = asyncio.Semaphore(4)
    img_sem = asyncio.Semaphore(6)

    # 1. Initial Keyframe Generation for All Scenes
    async def _run_kf(i: int, sc: dict[str, Any]):
        idx = sc.get("scene_index", sc.get("scene_number", i))
        res = await _generate_single_keyframe(
            idx=idx, sc=sc, scenes_dir=scenes_dir, episode=episode,
            char_anchor=char_anchor, derived_culture=derived_culture,
            visual_adapter=visual_adapter, force_live=force_live,
            total_scenes=len(scenes_list), img_sem=img_sem,
        )
        img_results[idx] = res

    await asyncio.gather(*[_run_kf(i, sc) for i, sc in enumerate(scenes_list)])

    # 2. Quality Gate Review Loop (Approve, Recreate Specific/All, Script, Cancel)
    while True:
        decision = execute_image_quality_gate(
            scenes_list=scenes_list, scenes_dir=scenes_dir,
            auto_confirm=auto_confirm, custom_input_fn=custom_gate_input_fn,
        )

        if decision.action == "proceed":
            logger.info("image_quality_gate_approved: proceeding to motion video & audio synthesis")
            break
        if decision.action == "cancel":
            raise PipelineCancelled("Production cancelled by user at Image Quality Gate.")
        if decision.action == "recreate_script":
            raise RecreateScriptRequested("User requested full script and keyframe recreation.")
        if decision.action == "recreate_all":
            logger.info("image_quality_gate: recreating all scene keyframe images")
            for p in scenes_dir.glob("scene_*.jpg"):
                try: p.unlink()
                except Exception: pass
            for p in scenes_dir.glob("scene_*_motion.mp4"):
                try: p.unlink()
                except Exception: pass
            img_results.clear()
            await asyncio.gather(*[_run_kf(i, sc) for i, sc in enumerate(scenes_list)])
            continue
        if decision.action == "recreate_specific":
            target_set = set(decision.target_scene_indices)
            logger.info(f"image_quality_gate: recreating specific scene keyframes: {target_set}")
            for s_idx in target_set:
                img_file = scenes_dir / f"scene_{s_idx:02d}.jpg"
                motion_file = scenes_dir / f"scene_{s_idx:02d}_motion.mp4"
                if img_file.exists():
                    try: img_file.unlink()
                    except Exception: pass
                if motion_file.exists():
                    try: motion_file.unlink()
                    except Exception: pass
                if s_idx in decision.prompt_overrides:
                    for sc in scenes_list:
                        if sc.get("scene_index", sc.get("scene_number")) == s_idx:
                            sc["visual_prompt"] = decision.prompt_overrides[s_idx]

            await asyncio.gather(*[
                _run_kf(i, sc) for i, sc in enumerate(scenes_list)
                if sc.get("scene_index", sc.get("scene_number", i)) in target_set
            ])
            continue

    # 3. Voiceover Synthesis (TTS)
    async def _proc_voice(idx: int, sc: dict[str, Any]):
        dialogue = extract_dialogue_text(sc)
        if not (enable_voice_over and getattr(episode.options, "enable_tts", True) and dialogue):
            voice_results[idx] = None
            return

        target_voice_path = stems_dir / f"voice_{idx:02d}_{language}.wav"
        if target_voice_path.is_file() and target_voice_path.stat().st_size > 1000:
            voice_results[idx] = target_voice_path
        else:
            await tts_adapter.synthesize_to_file(dialogue, output_path=target_voice_path, voice_id=derived_culture.voice_id, force_live=force_live)
            voice_results[idx] = target_voice_path

        rights_ledger.record_asset(
            episode_id=episode.id, asset_type=AssetType.VOICE, file_path=str(target_voice_path),
            provider="Microsoft/NeuralVoice", model_name=derived_culture.voice_id,
            license_type=CommercialLicenseType.COMMERCIAL_ROYALTY_FREE,
            license_id=f"MS-TTS-{episode.id}-{idx}", cleared=True,
        )

    await asyncio.gather(*[_proc_voice(sc.get("scene_index", sc.get("scene_number", i)), sc) for i, sc in enumerate(scenes_list)])

    # 4. Video Motion Synthesis (Kling / Optical Steadycam)
    video_results: dict[int, Path | None] = {}

    async def _proc_motion(idx: int, sc: dict[str, Any]):
        img_path, img_was_recreated = img_results.get(idx, (scenes_dir / f"scene_{idx:02d}.jpg", False))
        vid_path = scenes_dir / f"scene_{idx:02d}_motion.mp4"
        if img_was_recreated and vid_path.exists():
            try: vid_path.unlink()
            except Exception: pass

        if vid_path.is_file() and vid_path.stat().st_size > 1000 and not img_was_recreated:
            video_results[idx] = vid_path
            return

        fmt_val = str(getattr(episode.format, "value", episode.format)).lower()
        aspect_ratio = "9:16" if "9_16" in fmt_val or "vertical" in fmt_val else "16:9"
        target_res = (1080, 1920) if "9:16" in aspect_ratio else (1920, 1080)
        dur = round(float(sc.get("duration_seconds", sc.get("duration", 4.0))) * scale, 2)
        motion_type = sc.get("motion_type", "kinetic_video")

        if (not (enable_video_motion and kling_adapter)) or (motion_type == "steadycam_vista" and len(scenes_list) > 2 and not getattr(episode.options, "force_video_all_scenes", False)):
            mov = sc.get("camera_movement") or assign_scene_camera_movement(idx, sc.get("shot_type", "medium"))
            try:
                await render_steadycam_clip(
                    image_path=img_path, output_path=vid_path,
                    duration_seconds=dur, fps=30, target_res=target_res,
                    movement=mov, ffmpeg_bin=get_ffmpeg_binary(),
                )
                video_results[idx] = vid_path
                rights_ledger.record_asset(
                    episode_id=episode.id, asset_type=AssetType.VIDEO_MOTION, file_path=str(vid_path),
                    provider="Local/FFmpeg-2.5D", model_name="Optical-Steadycam-Glide",
                    license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
                    license_id=f"LOCAL-GLIDE-{episode.id}-{idx}", cleared=True,
                )
            except Exception as ex:
                logger.warning(f"Steadycam render failed for scene {idx}: {ex}")
                video_results[idx] = None
            return

        base_motion = sc.get("motion_prompt") or sc.get("visual_prompt") or episode.title
        weather_motion = derive_weather_motion_cues(f"{episode.title} {sc.get('visual_prompt', '')} {base_motion}")
        motion_prompt = f"first-person steadycam forward camera glide, {weather_motion}{base_motion}" if (not char_anchor or "walking" in fmt_val) else f"{weather_motion}{base_motion}"

        async with motion_sem:
            try:
                _, local_vid = await kling_adapter.generate_video(
                    image_url=str(img_path), motion_prompt=motion_prompt,
                    output_path=vid_path, duration=10 if (dur >= 8 or "walking" in fmt_val) else 5,
                    aspect_ratio=aspect_ratio, force_live=force_live,
                )
                if local_vid and Path(local_vid).exists() and Path(local_vid).stat().st_size > 1000:
                    video_results[idx] = local_vid
                    rights_ledger.record_asset(
                        episode_id=episode.id, asset_type=AssetType.VIDEO_MOTION, file_path=str(local_vid),
                        provider="Fal.ai/Kling", model_name="Kling-v1.5-Pro",
                        license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
                        license_id=f"FAL-KLING-{episode.id}-{idx}", cleared=True,
                    )
            except Exception as ex:
                if force_live: raise
                logger.warning(f"Video motion synthesis failed for scene {idx}: {ex}")
                video_results[idx] = None

    await asyncio.gather(*[_proc_motion(sc.get("scene_index", sc.get("scene_number", i)), sc) for i, sc in enumerate(scenes_list)])

    # 5. Order Compiled Scenes & Build Timeline Subtitles
    compiled_scenes: list[dict[str, Any]] = []
    subtitle_segments: list[dict[str, Any]] = []
    current_time = 0.0

    for i, sc in enumerate(scenes_list):
        idx = sc.get("scene_index", sc.get("scene_number", i))
        dur = round(float(sc.get("duration_seconds", sc.get("duration", 4.0))) * scale, 2)
        dialogue = extract_dialogue_text(sc)
        img_path, _ = img_results.get(idx, (scenes_dir / f"scene_{idx:02d}.jpg", False))
        vid_path = video_results.get(idx)
        voice_path = voice_results.get(idx)

        compiled_scenes.append({
            "scene_index": idx, "duration_seconds": dur, "image_path": str(img_path),
            "video_path": str(vid_path) if vid_path else None,
            "voice_path": str(voice_path) if voice_path else None,
            "shot_type": sc.get("shot_type", "medium"), "dialogue": dialogue,
        })
        speech_dur = get_audio_duration(voice_path) if voice_path else 0.0
        sub_dur = min(dur - 0.20, speech_dur + 0.45) if speech_dur > 0 else (dur - 0.20)
        subtitle_segments.append({
            "start": round(current_time, 2),
            "end": round(current_time + max(0.5, sub_dur), 2),
            "text": dialogue,
        })
        current_time += dur

    return compiled_scenes, subtitle_segments, current_time
