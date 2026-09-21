import asyncio
from pathlib import Path
from typing import Any

from src.cinematics.continuity.environmental_state import environmental_state_tracker
from src.compliance.rights_ledger import rights_ledger
from src.compositor.pipeline_prompts import extract_dialogue_text
from src.core.telemetry import logger
from src.domain.rights import AssetType, CommercialLicenseType
from src.services.character_consistency import inject_character_consistency


def derive_weather_motion_cues(cues: str) -> str:
    """Extract and synthesize kinetic atmospheric, thermal, and precipitation physics prompts."""
    c = cues.lower()
    is_dance = any(k in c for k in ("dance", "step", "choreograph", "troupe", "hero", "heroine", "jump", "spin"))

    # 1. Snow & Winter Conditions
    if any(k in c for k in ("blizzard", "snowstorm", "heavy snow", "gale", "arctic storm")):
        if is_dance:
            return "intense swirling blizzard gusts, blowing powder snow whipping past dancing troupe, foot-stomps kicking up snow drifts, visible breath vapor, "
        return "intense swirling blizzard gusts, dense clouds of blowing white powder snow whipping across the frame, visible snow flurries and dynamic wind drift, "
    if any(k in c for k in ("snow", "snowing", "snowfall", "flurry", "flurries", "winter", "frost")):
        if is_dance:
            return "delicate crystalline snowflakes floating and swirling around dancers, energetic foot-stomps kicking up fresh white snow powder, subtle frosty breath vapor, "
        return "soft delicate crystalline snowflakes drifting and floating gently down through the air, peaceful tranquil snowfall with drifting flakes, "

    # 2. Rain & Monsoon Conditions
    if any(k in c for k in ("heavy rain", "downpour", "torrential", "storm", "monsoon", "deluge", "drench")):
        if is_dance:
            return "sheets of heavy rain actively pouring down, visible raindrops slicing through frame, splashing water droplets flying off spinning bodies and hair, heavy foot-stomps violently splashing water from reflective puddles with expanding ripples, "
        return "sheets of heavy rainfall actively pouring down through the air, visible rain streaks slicing through frame, splashing raindrops bouncing off wet pavement and puddles with expanding ripples, streaming water runoff, "
    if any(k in c for k in ("rain", "drizzle", "shower", "rainy", "wet street", "puddle")):
        if is_dance:
            return "fine raindrops gently falling through frame, glistening wet stage, splashes of water kicked up by dance steps with expanding puddle ripples, "
        return "fine delicate raindrops gently falling through the air, visible rain streaks, soft water droplets creating ripples on glistening wet surfaces, "

    # 3. Fiery Hot Sun, Desert Heat & Summer
    if any(k in c for k in ("hot sun", "fiery sun", "scorching", "heatwave", "desert heat", "blazing sun", "midday sun", "summer heat")):
        if is_dance:
            return "shimmering atmospheric heat haze waves rising from the ground, intense radiant sunbeams illuminating dancing performers, golden dust clouds vigorously kicked up by energetic footwork, "
        return "shimmering atmospheric heat waves rising from the ground, intense radiant sunbeams, subtle heat distortion, "

    # 4. Fog, Mist & Atmospheric Haze
    if any(k in c for k in ("fog", "foggy", "mist", "misty", "haze")):
        return "rolling tendrils of atmospheric mist and fog drifting slowly across the path and between trees and buildings, ethereal shifting atmospheric depth, "

    # 5. Cloudy Evening, Sunset & Overcast Skies
    if any(k in c for k in ("cloudy evening", "evening clouds", "sunset", "twilight", "dusk")):
        if is_dance:
            return "dramatic evening clouds drifting across twilight sky, warm ambient sunset light, evening breeze fluttering vibrant costumes and flying scarves during dance turns, "
        return "dramatic shifting evening clouds across the colorful twilight sky, soft sunset breeze, shifting ambient golden-hour radiance, "
    if any(k in c for k in ("cloudy", "overcast", "grey sky", "gray sky", "clouds")):
        if is_dance:
            return "dynamic low-hanging moody clouds shifting across the sky, cool breeze fluttering dancer costumes and hair, diffuse natural daylight, "
        return "dynamic low-hanging clouds slowly shifting and drifting across the overcast sky, subtle shifting diffuse daylight filtering through rolling grey cloud layers, "

    # 6. Autumn leaves, Dust & Wind
    if any(k in c for k in ("autumn", "falling leaves", "foliage", "windy", "breeze", "breezy")):
        return "crisp breeze causing golden leaves to swirl and flutter down through the air, gentle wind rustling branches and swaying foliage, "
    if any(k in c for k in ("dust", "sandstorm", "desert wind", "gulal", "kumkum", "powder")):
        return "swirling airborne dust clouds skimming across the ground, dynamic wind-blown particle currents, "

    return ""


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
    # -------------------------------------------------------------------------
    # Step 1: Parallel Batch Keyframe & Voiceover Synthesis
    # -------------------------------------------------------------------------
    img_results: dict[int, tuple[Path, bool]] = {}
    voice_results: dict[int, Path | None] = {}
    motion_sem = asyncio.Semaphore(4)
    img_sem = asyncio.Semaphore(6)

    async def _proc_keyframe(idx: int, sc: dict[str, Any]):
        vis_prompt = sc.get("visual_prompt") or sc.get("visual_description") or f"Scene {idx} for {episode.title}"
        enhanced_vis, scene_loras, scene_seed = inject_character_consistency(vis_prompt, char_anchor)
        env_state = environmental_state_tracker.compute_scene_environmental_state(
            scene_index=idx, total_scenes=len(scenes_list),
            weather=getattr(derived_culture, "weather_condition", "clear_daylight"),
            space=getattr(derived_culture, "environment_space", "outdoor"),
        )
        if env_state.get("environmental_prompt") and env_state["environmental_prompt"] not in enhanced_vis:
            enhanced_vis = f"{enhanced_vis}, {env_state['environmental_prompt']}"
        if derived_culture.art_style_prompt and derived_culture.art_style_prompt not in enhanced_vis:
            enhanced_vis = f"{enhanced_vis}, {derived_culture.art_style_prompt}"
        for lora in derived_culture.recommended_loras:
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

        if idx == 0 and char_anchor and not char_anchor.reference_image_path:
            char_anchor.reference_image_path = str(img_path)

        rights_ledger.record_asset(
            episode_id=episode.id, asset_type=AssetType.IMAGE, file_path=str(img_path),
            provider="Fal.ai/Flux", model_name="FLUX.1-dev (28 steps)",
            license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
            license_id=f"BFL-COMM-{episode.id}-{idx}", cleared=True,
        )
        img_results[idx] = (img_path, recreated)

    async def _proc_voice(idx: int, sc: dict[str, Any]):
        dialogue = extract_dialogue_text(sc)
        if not (enable_voice_over and episode.options.enable_tts and dialogue):
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

    await asyncio.gather(
        *[_proc_keyframe(sc.get("scene_index", sc.get("scene_number", i)), sc) for i, sc in enumerate(scenes_list)],
        *[_proc_voice(sc.get("scene_index", sc.get("scene_number", i)), sc) for i, sc in enumerate(scenes_list)],
    )

    # -------------------------------------------------------------------------
    # Step 2: Parallel Batch Video Motion Synthesis
    # -------------------------------------------------------------------------
    video_results: dict[int, Path | None] = {}

    async def _proc_motion(idx: int, sc: dict[str, Any]):
        if not (enable_video_motion and kling_adapter):
            video_results[idx] = None
            logger.info(f"scene_{idx:02d}_mode: [4K FLUX 2.5D Steadycam Glide] (video motion disabled)")
            return

        motion_type = sc.get("motion_type", "kinetic_video")
        # Hybrid Directorial Mode: Vista scenes use 4K FLUX steadycam glides for breathing room
        if motion_type == "steadycam_vista" and len(scenes_list) > 2 and not getattr(episode.options, "force_video_all_scenes", False):
            logger.info(f"scene_{idx:02d}_mode: [4K FLUX 2.5D Steadycam Glide (Vista)] for scene_{idx:02d}.jpg")
            video_results[idx] = None
            return

        logger.info(f"scene_{idx:02d}_mode: [AI Video Motion (Kling Pro 10s)] for scene_{idx:02d}.jpg")
        img_path, img_was_recreated = img_results.get(idx, (scenes_dir / f"scene_{idx:02d}.jpg", False))
        vid_path = scenes_dir / f"scene_{idx:02d}_motion.mp4"
        if img_was_recreated and vid_path.exists():
            try: vid_path.unlink()
            except Exception: pass

        if vid_path.is_file() and vid_path.stat().st_size > 1000 and not img_was_recreated:
            video_results[idx] = vid_path
            logger.info(f"scene_motion_cache_hit: reusing existing {vid_path.name}")
            return

        fmt_val = str(getattr(episode.format, "value", episode.format)).lower()
        aspect_ratio = "9:16" if "9_16" in fmt_val or "vertical" in fmt_val else "16:9"
        base_motion = sc.get("motion_prompt") or sc.get("visual_prompt") or sc.get("visual_description") or episode.title
        combined_cues = f"{episode.title} {sc.get('visual_prompt', '')} {base_motion}"
        weather_motion = derive_weather_motion_cues(combined_cues)
        dur = round(float(sc.get("duration_seconds", sc.get("duration", 4.0))) * scale, 2)

        if not char_anchor or "walking" in fmt_val or "scenic" in fmt_val:
            motion_prompt = f"first-person steadycam forward camera glide, pure scenic environmental perspective, empty unobstructed pathway, {weather_motion}{base_motion}"
        else:
            motion_prompt = f"{weather_motion}{base_motion}"

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
                if force_live:
                    logger.error(f"Video motion synthesis failed for scene {idx} in LIVE mode: {ex}")
                    raise
                logger.warning(f"Video motion synthesis failed for scene {idx}: {ex}")
                video_results[idx] = None

    await asyncio.gather(*[_proc_motion(sc.get("scene_index", sc.get("scene_number", i)), sc) for i, sc in enumerate(scenes_list)])

    # -------------------------------------------------------------------------
    # Step 3: Order Compiled Scenes & Build Timeline Subtitles
    # -------------------------------------------------------------------------
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
        subtitle_segments.append({"start": current_time, "end": current_time + dur, "text": dialogue})
        current_time += dur

    return compiled_scenes, subtitle_segments, current_time
