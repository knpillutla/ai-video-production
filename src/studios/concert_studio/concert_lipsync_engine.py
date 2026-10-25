"""Master Singer Lip-Sync Plate Synthesizer for 4K Live Concerts.

Synthesizes a single continuous master lip-sync plate for the full song duration.
Adheres strictly to Rule 3 Universal Artifact Caching:
If scenes/master_singer_lipsync.mp4 exists on disk and is non-empty (> 50KB),
it is reused immediately ($0.00 spend).
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional

from src.compositor.vocal_compositor import probe_audio_duration
from src.core.telemetry import logger
from src.studios.concert_studio.concert_movement_engine import render_audio_synced_movement_cut


def _is_valid_mp4(p: Path) -> bool:
    """Validate MP4 container and moov atom presence to prevent corrupted playback."""
    if not (p.is_file() and p.stat().st_size > 50_000):
        return False
    try:
        with open(p, "rb") as f:
            h = f.read(8192)
            f.seek(max(0, p.stat().st_size - 524288))
            return (b"moov" in h) or (b"moov" in f.read())
    except Exception:
        return False


async def synthesize_master_singer_plate(
    stage_image: Path,
    audio_path: Path,
    output_path: Path,
    total_duration: float,
    lipsync_model: str | None = None,
    force_live: bool = False,
    onepass_bytedance: bool = False,
    position: str = "sitting",
    has_chorus: bool = False,
    storyboard_data: dict[str, Any] | None = None,
) -> Path:
    """Synthesize or reuse full-duration master singer lipsync plate."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Rule 3 Tier 1: Check existing non-empty artifact
    if _is_valid_mp4(output_path):
        dur = probe_audio_duration(output_path)
        if dur >= (total_duration - 3.0):
            logger.info(f"master_singer_lipsync_reused: {output_path.name} ({dur:.1f}s, $0.00 spend)")
            print(f"[+] Stage 5: Reusing full-duration master singer lipsync plate: {output_path.name} ({dur:.1f}s) ($0.00 spend)")
            return output_path

    print(f"[~] Stage 5: Synthesizing continuous master singer lipsync plate ({total_duration:.1f}s) [model={lipsync_model or 'wav2lip'}]...")

    eff_model = (lipsync_model or "wav2lip").lower()
    is_onepass = onepass_bytedance or any(k in eff_model for k in ("bytedance", "omnihuman"))

    # Mode 1: 1-Pass ByteDance OmniHuman (audio-driven movement + lipsync)
    if is_onepass:
        from src.providers.lipsync.fal_bytedance_omnihuman import fal_bytedance_omnihuman_adapter
        try:
            await fal_bytedance_omnihuman_adapter.generate_avatar_video(
                image_path=stage_image, audio_path=audio_path, output_path=output_path, force_live=force_live,
            )
            if _is_valid_mp4(output_path):
                return output_path
        except Exception as ex:
            logger.warning(f"master_bytedance_failed, falling back to local: {ex}")

    # Mode 2: Living Stage Movement Base Plate
    base_mv = output_path.parent / "master_singer_movement.mp4"
    if not _is_valid_mp4(base_mv) or probe_audio_duration(base_mv) < (total_duration - 3.0):
        scenes_dir = output_path.parent
        living_5s = scenes_dir / "scene_01.mp4" if (scenes_dir / "scene_01.mp4").is_file() else (scenes_dir / "scene_01_motion.mp4" if (scenes_dir / "scene_01_motion.mp4").is_file() else scenes_dir / "stage_living_5s.mp4")
        living_generated = False

        # Option A: Reuse existing scene_01.mp4 living stage loop or synthesize via motion model
        if living_5s.is_file() and living_5s.stat().st_size > 50_000:
            try:
                from src.studios.concert_studio.concert_kling_3d import materialize_living_stage_loop
                print(f"  [>] Materializing full-duration living stage loop from {living_5s.name} ({total_duration:.1f}s)...")
                materialize_living_stage_loop(living_5s, base_mv, total_duration)
                if _is_valid_mp4(base_mv):
                    living_generated = True
                    print(f"  [+] Materialized living stage loop -> {base_mv.name}")
            except Exception as ex:
                logger.warning(f"loop_materialize_failed: {ex}")
        elif force_live:
            try:
                from src.studios.concert_studio.concert_kling_3d import (
                    materialize_living_stage_loop,
                    synthesize_living_stage_loop,
                )
                motion_p, motion_neg = None, None
                if storyboard_data and storyboard_data.get("scenes"):
                    sc0 = storyboard_data["scenes"][0]
                    m_dict = sc0.get("motion_prompts", {})
                    km = m_dict.get("kling_prod") or m_dict.get("kling_4k") or m_dict.get("wan_2_1")
                    if isinstance(km, dict):
                        motion_p, motion_neg = km.get("prompt"), km.get("negative_prompt")
                    elif isinstance(km, str):
                        motion_p = km
                    if not motion_p:
                        motion_p = sc0.get("motion_prompt")
                living_5s_res = await synthesize_living_stage_loop(
                    stage_master_image=stage_image, scenes_dir=scenes_dir, force_live=force_live,
                    has_chorus=has_chorus, custom_prompt=motion_p, custom_neg=motion_neg,
                    storyboard_data=storyboard_data,
                )
                if _is_valid_mp4(living_5s_res):
                    print(f"  [>] Materializing full-duration living stage loop ({total_duration:.1f}s)...")
                    materialize_living_stage_loop(living_5s_res, base_mv, total_duration)
                    if _is_valid_mp4(base_mv):
                        living_generated = True
                        print(f"  [+] Materialized living stage loop -> {base_mv.name}")
            except Exception as ex:
                print(f"  [!] Living stage video unavailable ({ex}). Falling back to static image physics...")
                logger.warning(f"kling_living_stage_failed, falling back to static image physics: {ex}")

        # Option B: Fallback to Pitch-Responsive Steady CPU Torso & Head Physics on static image ($0.00 spend)
        if not living_generated and not _is_valid_mp4(base_mv):
            print(f"  [>] Starting steady singer torso & head physics on CPU ({total_duration:.1f}s, 24fps)...")
            render_audio_synced_movement_cut(
                source_media=stage_image, audio_path=audio_path, output_path=base_mv,
                duration_seconds=total_duration, fps=24, is_singing=True, intensity=0.5, position=position,
            )
            print(f"  [+] Completed steady singer torso & head physics render -> {base_mv.name}")
    else:
        print(f"  [+] Reusing existing singer physics plate -> {base_mv.name} ($0.00 spend)")

    lipsync_source = base_mv if _is_valid_mp4(base_mv) else stage_image

    # Mode 3: Lip-Sync Engine
    print(f"  [>] Starting master lip-sync synthesis on plate ({lipsync_source.name}) [model={eff_model}]...")
    if "sadtalker" in eff_model:
        from src.providers.lipsync.local_sadtalker import local_sadtalker_adapter
        await local_sadtalker_adapter.sync_lips(
            video_path=lipsync_source, audio_path=audio_path, output_path=output_path, force_live=force_live,
        )
    elif any(k in eff_model for k in ("kling", "latentsync", "fal")):
        from src.providers.lipsync.fal_latentsync import FalLatentSyncAdapter
        adapter = FalLatentSyncAdapter(default_model=lipsync_model or "fal-ai/latentsync")
        try:
            await adapter.sync_lips(
                video_path=lipsync_source, audio_path=audio_path, output_path=output_path,
                force_live=force_live, model=lipsync_model,
            )
        except Exception as ex:
            print(f"  [!] Cloud lip-sync unavailable ({ex}). Starting local Wav2Lip fallback...")
            logger.warning(f"cloud_lipsync_failed, using local fallback: {ex}")
            try:
                from src.providers.lipsync.local_wav2lip import LocalWav2LipAdapter
                await LocalWav2LipAdapter().sync_lips(
                    video_path=lipsync_source, audio_path=audio_path, output_path=output_path, force_live=force_live,
                )
            except Exception as lex:
                logger.warning(f"local_wav2lip_fallback_failed: {lex}")
    else:
        # Default: Local ONNX Wav2Lip ($0.00 spend on CPU/GPU)
        try:
            from src.providers.lipsync.local_wav2lip import LocalWav2LipAdapter
            await LocalWav2LipAdapter().sync_lips(
                video_path=lipsync_source, audio_path=audio_path, output_path=output_path, force_live=force_live,
            )
        except Exception as lex:
            logger.warning(f"local_wav2lip_failed: {lex}")

    if not _is_valid_mp4(output_path) and _is_valid_mp4(base_mv):
        import shutil
        shutil.copy2(base_mv, output_path)

    if _is_valid_mp4(output_path):
        print(f"  [+] Completed master singer lipsync plate -> {output_path.name}")
    return output_path


__all__ = ["synthesize_master_singer_plate", "_is_valid_mp4"]
