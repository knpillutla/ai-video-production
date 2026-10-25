"""Concert Director: Wan 2.1 ISO Motion & Beat-Synchronized Multi-Camera Switching.

Handles:
1. Wan 2.1 ISO camera motion synthesis for the 6 distinct concert camera plates.
2. Directorial switching cuts assembly.
3. Beat-synchronized LatentSync lip-sync applied STRICTLY to Camera 1 singing cuts.
4. Single-pass FFmpeg 4K broadcast assembly with ASS subtitles.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from src.compliance.rights_ledger import AssetType, CommercialLicenseType, rights_ledger
from src.core.telemetry import logger
from src.providers.visual.fal_wan21 import FalWan21Adapter
from src.studios.concert_studio.concert_lipsync_engine import synthesize_master_singer_plate, _is_valid_mp4

CAMERA_MOTION_PROMPTS = {
    "center_vocalist_front": "Passionate live concert vocal performance: artist poised at vintage stand microphone at chin level, subtle natural rhythm sway, expressive eyes, calm natural breathing, authentic skin pore fidelity.",
    "active_instrument_macro": "Extreme close-up macro of skilled musician hands playing instrument in sync with driving concert rhythm, fingers fretting chords with precision, strings vibrating crisply under warm amber spotlight.",
    "backing_orchestra_ensemble": "Live backing band in energetic concert motion: drummer energetically striking cymbals in rhythm, bassist swaying to the driving groove, sweeping overhead stage spotlights.",
    "overall_stadium_vista": "Slow panoramic high-crane arena descent from overhead steel trusses looking across the mammoth illuminated stadium bowl and glowing central stage.",
    "stadium_audience_crowd": "Slow sweeping drone glide forward over the ecstatic sea of cheering concert fans waving glowing amber and cyan lightsticks and smartphone flashlights.",
    "stage_lightshow_pyro": "Dynamic camera push towards stage as crisscrossing volumetric lasers sweep overhead and golden pyrotechnic fountains flare dramatically against glowing LED backdrop.",
}


async def synthesize_concert_motion(
    storyboard_data: dict[str, Any],
    scenes_dir: Path,
    audio_path: Path,
    force_live: bool = False,
    episode_id: Any = None,
    use_kling: bool = False,
    motion_model: str = "wan",
) -> dict[int, Path]:
    """Synthesize motion videos using specified motion model (wan2.1, kling, kling-4k, or local drone)."""
    scenes_list = storyboard_data.get("scenes") or []
    motion_map: dict[int, Path] = {}
    eff_model = "kling" if use_kling else (motion_model or "wan").lower()

    flight_3d = scenes_dir / "stadium_3d_flight.mp4"
    from src.providers.visual.fal_wan21 import FalWan21Adapter
    wan = FalWan21Adapter()

    for idx in range(1, len(scenes_list) + 1 if scenes_list else 7):
        img_path = scenes_dir / f"scene_{idx:02d}.jpg"
        out_vid = scenes_dir / ("scene_01.mp4" if idx == 1 else f"scene_{idx:02d}_motion.mp4")
        if not (img_path.is_file() and img_path.stat().st_size > 1000):
            continue

        if idx > 1 and flight_3d.is_file() and flight_3d.stat().st_size > 50_000:
            logger.info(f"concert_motion_reused [cam {idx}]: {flight_3d.name} ($0.00 spend)")
            motion_map[idx] = flight_3d
            continue

        if out_vid.is_file() and out_vid.stat().st_size > 50_000:
            logger.info(f"concert_motion_reused: {out_vid.name} ($0.00 spend)")
            motion_map[idx] = out_vid
            if idx == 1:
                for alias in (scenes_dir / "scene_01_motion.mp4", scenes_dir / "stage_living_5s.mp4"):
                    if not alias.is_file():
                        import shutil
                        shutil.copyfile(out_vid, alias)
            continue

        sc = scenes_list[idx - 1] if idx <= len(scenes_list) else {}
        cam_id = sc.get("camera_id", "")
        m_prompts = sc.get("motion_prompts", {})

        # Select prompt by motion model
        if "kling_4k" in eff_model or "4k" in eff_model:
            prompt = (m_prompts.get("kling_4k") or {}).get("prompt") or CAMERA_MOTION_PROMPTS.get(cam_id, CAMERA_MOTION_PROMPTS["center_vocalist_front"])
        elif "kling" in eff_model:
            prompt = (m_prompts.get("kling_prod") or {}).get("prompt") or CAMERA_MOTION_PROMPTS.get(cam_id, CAMERA_MOTION_PROMPTS["center_vocalist_front"])
        else:
            prompt = (m_prompts.get("wan_2_1") or {}).get("prompt") or CAMERA_MOTION_PROMPTS.get(cam_id, CAMERA_MOTION_PROMPTS["center_vocalist_front"])

        neg_prompt = (m_prompts.get(eff_model) or m_prompts.get("wan_2_1") or {}).get("negative_prompt") or ""
        if idx == 1:
            mouth_safety = "microphone covering mouth, hand covering mouth, exaggerated mouth flapping, gaping mouth, wide open jaw, rapid talking, teeth chatter, distorted mouth"
            neg_prompt = f"{neg_prompt}, {mouth_safety}".strip(", ")

        logger.info(f"generating_concert_motion [model={eff_model}] [scene_{idx:02d}]: {prompt[:65]}...")

        if "sadtalker" in eff_model or "drone" in eff_model or "local" in eff_model:
            from src.scripts.local_perspective_drone import render_perspective_drone_clip_sync
            render_perspective_drone_clip_sync(image_path=img_path, output_path=out_vid, duration_seconds=5.0, fps=24, choreography="steady_eye_level", force_rerun=True)
        elif "h3" in eff_model or "minimax" in eff_model:
            from src.providers.dance.fal_h3_max_turbo import FalH3MaxTurboAdapter
            await FalH3MaxTurboAdapter().generate_video(image_url=str(img_path), motion_prompt=prompt, output_path=out_vid, duration=5, force_live=force_live)
        elif "kling" in eff_model:
            from src.providers.dance.fal_kling import FalKlingAdapter
            await FalKlingAdapter().generate_video(image_url=str(img_path), motion_prompt=prompt, output_path=out_vid, duration=5, force_live=force_live, negative_prompt=neg_prompt)
        else:
            await wan.generate_to_file(image_path=img_path, output_path=out_vid, prompt=prompt, duration_seconds=5, aspect_ratio="16:9", force_live=force_live, negative_prompt=neg_prompt)

        if episode_id and out_vid.is_file():
            prov = "Minimax-H3" if ("h3" in eff_model or "minimax" in eff_model) else ("Kling" if "kling" in eff_model else "Wan-2.1")
        if idx == 1 and out_vid.is_file():
            import shutil
            for alias in (scenes_dir / "scene_01_motion.mp4", scenes_dir / "stage_living_5s.mp4"):
                shutil.copyfile(out_vid, alias)
        motion_map[idx] = out_vid

    return motion_map


CAMERA_NAME_TO_INDEX = {
    "singer_orchestra_stage": 1, "center_vocalist_front": 1,
    "stage_left_profile": 2, "orchestra_profile": 2, "backing_orchestra_ensemble": 2,
    "stadium_audience_crowd": 3, "audience_reaction": 3,
    "overall_stage_vista": 4, "overall_stadium_vista": 4, "stage_lightshow_pyro": 4,
    "active_instrument_macro": 1,
}


async def synthesize_concert_broadcast_cuts(
    storyboard_data: dict[str, Any],
    scenes_dir: Path,
    audio_path: Path,
    motion_map: dict[int, Path],
    force_live: bool = False,
    episode_id: Any = None,
    enable_lipsync: bool = True,
    lipsync_model: str | None = None,
    onepass_bytedance: bool = False,
) -> list[dict[str, Any]]:
    """Synthesize broadcast cuts from Stream A (3D Arena Flight) & Stream B (Master Singer Lip-Sync Plate)."""
    cuts_data = storyboard_data.get("broadcast_timeline") or []
    cuts_dir = scenes_dir.parent / "broadcast_cuts"
    cuts_dir.mkdir(parents=True, exist_ok=True)
    import subprocess
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    # Stream A: 10s 360-degree closed-loop spatial video & full-duration loop
    flight_3d = scenes_dir / "stadium_3d_flight.mp4"
    has_flight = flight_3d.is_file() and flight_3d.stat().st_size > 50_000
    scene_01 = scenes_dir / "scene_01.jpg"
    total_dur = max([float(c.get("end_time", 0.0)) for c in cuts_data] or [60.0])
    flight_3d_looped = scenes_dir / "stadium_3d_flight_looped.mp4"
    if has_flight and not _is_valid_mp4(flight_3d_looped):
        print(f"[~] Stage 5 (Stream A): Materializing full-duration 3D arena flight loop ({flight_3d_looped.name}, {total_dur:.1f}s)...")
        num_loops = int(total_dur // 10.0) + 2
        subprocess.run([
            ffmpeg_bin, "-y", "-stream_loop", str(num_loops), "-i", str(flight_3d),
            "-c", "copy", "-t", f"{total_dur:.2f}", str(flight_3d_looped)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if _is_valid_mp4(flight_3d_looped):
        print(f"[+] Stage 5 (Stream A): Reusing full-duration 3D arena flight loop: {flight_3d_looped.name} ($0.00 spend)")

    # Stream B: Full-duration Master Singer Lip-Sync Plate
    master_sync_clip = scenes_dir / "master_singer_lipsync.mp4"
    if enable_lipsync and scene_01.is_file():
        pos = storyboard_data.get("artist_position") or storyboard_data.get("position") or "sitting"
        from src.studios.concert_studio.concert_prompt_engine import detect_chorus_presence
        has_chorus = detect_chorus_presence(storyboard_data)
        await synthesize_master_singer_plate(
            stage_image=scene_01, audio_path=audio_path, output_path=master_sync_clip,
            total_duration=total_dur, lipsync_model=lipsync_model, force_live=force_live,
            onepass_bytedance=onepass_bytedance, position=pos, has_chorus=has_chorus,
            storyboard_data=storyboard_data,
        )

    has_master_sync = _is_valid_mp4(master_sync_clip)

    resolved_cuts: list[dict[str, Any]] = []
    for c in cuts_data:
        c_idx = c["cut_index"]
        cam_id = c["camera_id"]
        c_start, c_end = float(c["start_time"]), float(c["end_time"])
        c_dur = round(c_end - c_start, 2)
        if c_dur <= 0:
            continue

        source_cam_idx = CAMERA_NAME_TO_INDEX.get(cam_id, 1)
        drone_motion = c.get("local_drone_motion", "steady_eye_level")
        is_singing = bool(c.get("is_singing", False))
        is_singing_cut = is_singing and cam_id in ("singer_orchestra_stage", "center_vocalist_front")
        cut_clip = cuts_dir / f"cut_{c_idx:02d}_{cam_id}.mp4"

        # Rule 3 Tier 1: Check existing valid cut
        if _is_valid_mp4(cut_clip):
            print(f"  [+] Cut {c_idx:02d} (Cam {source_cam_idx} {cam_id}): Reusing existing cut ({c_dur:.1f}s) ($0.00 spend)")
            resolved_cuts.append({
                "cut_index": c_idx, "path": cut_clip, "media_path": cut_clip, "duration": c_dur,
                "camera_id": cam_id, "start_time": c_start, "end_time": c_end, "drone_motion": drone_motion, "is_video": True,
            })
            continue

        # Route 1: Singing cuts -> Stream B (Master Singer Lip-Sync Plate)
        if is_singing_cut and has_master_sync:
            print(f"  [>] Cut {c_idx:02d} (Cam 1 Singer): Slicing Master Lip-Sync Plate [{c_start:.1f}s - {c_end:.1f}s] ({c_dur:.1f}s)...")
            subprocess.run([
                ffmpeg_bin, "-y", "-ss", f"{c_start:.2f}", "-t", f"{c_dur:.2f}",
                "-i", str(master_sync_clip), "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "24",
                "-pix_fmt", "yuv420p", "-an", str(cut_clip)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

        # Route 2: Camera Rig Directed Motion via Local Perspective Drone ($0.00 spend)
        else:
            from src.scripts.local_perspective_drone import render_perspective_drone_clip_sync
            cam_map = {
                1: scenes_dir / "scene_01.jpg",
                2: scenes_dir / "scene_02.jpg",
                3: scenes_dir / "scene_03.jpg",
                4: scenes_dir / "scene_04.jpg",
            }
            cam_plate = cam_map.get(source_cam_idx)
            src_img = cam_plate if (cam_plate and cam_plate.is_file() and cam_plate.stat().st_size > 1000) else scene_01
            print(f"  [~] Cut {c_idx:02d} (Cam {source_cam_idx} {cam_id}): Rendering Local Drone motion '{drone_motion}' from {src_img.name} ({c_dur:.1f}s)...")
            render_perspective_drone_clip_sync(
                image_path=src_img, output_path=cut_clip, duration_seconds=c_dur, fps=24,
                choreography=drone_motion, curve="cosine", motion_curve=c.get("motion_curve", "cosine"),
                start_pan="center", start_zoom="normal", start_tilt="center", max_depth=0.20,
                speed_factor=0.5, force_rerun=True,
            )

        if cut_clip.is_file() and cut_clip.stat().st_size > 10_000:
            resolved_cuts.append({
                "cut_index": c_idx, "path": cut_clip, "media_path": cut_clip, "duration": c_dur,
                "camera_id": cam_id, "start_time": c_start, "end_time": c_end, "drone_motion": drone_motion, "is_video": True,
            })

    return resolved_cuts


__all__ = ["synthesize_concert_motion", "synthesize_concert_broadcast_cuts"]
