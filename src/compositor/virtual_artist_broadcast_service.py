"""Multi-Camera Concert Broadcast Execution Engine for Virtual Artist Videos.

Handles:
1. Asset resolution mapping camera_id to camera rig scenes (1..6).
2. Audio segment slicing [start_time, end_time] for active singing cuts.
3. Beat-synchronized LatentSync lipsync strictly on singer camera cuts during singing.
4. Local drone 2.5D camera motion across audience, instrument solos, and crane vistas.
5. Single-pass FFmpeg broadcast assembly with beat-aligned cuts and zero looping artifacts.
Preserves Rule 4 (< 300 lines limit).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import subprocess
from typing import Any

import imageio_ffmpeg

from src.compliance.rights_ledger import AssetType, CommercialLicenseType, rights_ledger
from src.core.telemetry import logger
from src.providers.fal_storage import _fal_api_key
from src.providers.lipsync.fal_latentsync import FalLatentSyncAdapter


def resolve_camera_index(camera_id: str, scenes: list[dict[str, Any]], active_inst: str = "") -> int:
    """Find the 1-based scene index corresponding to a camera_id in the camera rig."""
    if active_inst:
        inst_l = active_inst.lower()
        for sc in scenes:
            p = (sc.get("visual_prompt") or "").lower()
            c = (sc.get("character_pose") or "").lower()
            if inst_l in p or inst_l in c:
                return int(sc.get("scene_index", 1))
    for sc in scenes:
        if sc.get("camera_id") == camera_id:
            return int(sc.get("scene_index", 1))
    defaults = {
        "center_vocalist_front": 1,
        "stage_profile_45": 6,
        "vocal_close_up": 3,
        "drone_audience_focus": 4,
        "active_instrument_macro": 5,
        "high_crane_arena_vista": 4,
    }
    return defaults.get(camera_id, 1)


def slice_cut_audio(audio_path: Path, start_time: float, duration: float, out_path: Path) -> Path:
    """Slice an exact audio segment [start_time : start_time + duration] using FFmpeg."""
    if out_path.is_file() and out_path.stat().st_size > 1000:
        return out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin, "-y", "-ss", f"{start_time:.2f}", "-t", f"{duration:.2f}",
        "-i", str(audio_path), "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
        str(out_path),
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    return out_path


async def synthesize_broadcast_timeline_clips(
    storyboard_data: dict[str, Any],
    scenes_dir: Path,
    audio_path: Path,
    motion_map: dict[int, Path],
    force_live: bool = False,
    episode_id: Any = None,
    enable_lipsync: bool = True,
) -> list[dict[str, Any]]:
    """Synthesize sliced vocal lipsync clips for singing cuts and resolve broadcast assets."""
    timeline = storyboard_data.get("broadcast_timeline") or []
    scenes = storyboard_data.get("scenes") or []
    cuts_dir = scenes_dir / "broadcast_cuts"
    cuts_dir.mkdir(parents=True, exist_ok=True)

    latentsync_adapter = FalLatentSyncAdapter(api_key=_fal_api_key())
    resolved_cuts = []

    singer_cameras = {"center_vocalist_front", "stage_profile_45", "vocal_close_up"}

    for cut in timeline:
        c_idx = int(cut.get("cut_index", len(resolved_cuts) + 1))
        cam_id = cut.get("camera_id", "center_vocalist_front")
        dur = float(cut.get("duration_seconds", 4.5))
        t_start = float(cut.get("start_time", 0.0))
        is_singing = bool(cut.get("is_singing", False))
        sc_idx = int(cut.get("scene_index") or resolve_camera_index(cam_id, scenes, cut.get("active_instrument", "")))

        if c_idx == 0 or t_start == 0.0 or sc_idx == 0:
            scene_00_path = scenes_dir / "scene_00.jpg"
            if scene_00_path.is_file():
                keyframe_path = scene_00_path
                raw_motion = None
                is_singing = False

        cut_info = {
            "cut_index": c_idx,
            "camera_id": cam_id,
            "scene_index": sc_idx,
            "duration": dur,
            "start_time": t_start,
            "is_singing": is_singing,
            "drone_motion": "static" if (c_idx == 0 or t_start == 0.0 or sc_idx == 0) else cut.get("local_drone_motion", "steady"),
            "transition": cut.get("transition", "cut"),
            "media_path": raw_motion if (raw_motion and raw_motion.is_file()) else keyframe_path,
            "is_video": bool(raw_motion and raw_motion.is_file()),
        }

        # Apply beat-synchronized lipsync ONLY when singing on singer camera
        if enable_lipsync and is_singing and cam_id in singer_cameras and raw_motion and raw_motion.is_file():
            sliced_audio = cuts_dir / f"cut_{c_idx:02d}_audio.mp3"
            lipsync_cut_video = cuts_dir / f"cut_{c_idx:02d}_lipsync.mp4"

            try:
                slice_cut_audio(audio_path, t_start, dur, sliced_audio)
                if lipsync_cut_video.is_file() and lipsync_cut_video.stat().st_size > 10_000:
                    cut_info["media_path"] = lipsync_cut_video
                    cut_info["is_video"] = True
                else:
                    logger.info(f"synthesizing_broadcast_lipsync_cut_{c_idx:02d} [{cam_id}]: {t_start:.1f}s-{t_start+dur:.1f}s")
                    synced = await latentsync_adapter.lipsync_video(
                        video_url=str(raw_motion),
                        audio_path=sliced_audio,
                        output_path=lipsync_cut_video,
                        force_live=force_live,
                    )
                    if synced and synced.is_file() and synced.stat().st_size > 10_000:
                        cut_info["media_path"] = synced
                        cut_info["is_video"] = True
                        if episode_id:
                            rights_ledger.record_asset(
                                episode_id, AssetType.VIDEO_MOTION, str(synced),
                                "Fal.ai/LatentSync", "latentsync",
                                CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
                                f"LIPSYNC-CUT-{c_idx}-{episode_id}", True,
                            )
            except Exception as e:
                logger.warning(f"broadcast_cut_lipsync_fallback_raw_{c_idx:02d}: {e}")

        resolved_cuts.append(cut_info)

    return resolved_cuts


async def assemble_broadcast_cuts(
    cuts: list[dict[str, Any]],
    song_path: Path,
    sub_path: Path | None,
    out_video_path: Path,
    total_duration: float,
    fps: int = 30,
) -> Path:
    """Assemble multi-camera broadcast cuts with smooth 2.5D local drone glides and zero looping."""
    out_video_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    input_args = []
    chains = []
    count = len(cuts)
    sum_cuts_dur = sum(float(c.get("duration") or c.get("duration_seconds", 3.0)) for c in cuts)
    if sum_cuts_dur > 0 and (total_duration <= 0 or total_duration < (sum_cuts_dur - 1.0)):
        logger.info(f"assemble_broadcast_cuts: auto-adjusting total_duration from {total_duration:.1f}s to {sum_cuts_dur:.1f}s to assemble all {count} clips")
        total_duration = sum_cuts_dur

    parent_master = song_path.parent / "music_master.mp3"
    if parent_master.is_file() and parent_master != song_path:
        from src.compositor.vocal_compositor import probe_audio_duration
        pm_dur = probe_audio_duration(parent_master) or 0.0
        if pm_dur >= (total_duration - 2.0):
            song_path = parent_master

    for i, c in enumerate(cuts):
        p = c.get("media_path") or c.get("path")
        dur = float(c.get("duration") or c.get("duration_seconds", 3.0))
        d_frames = max(30, int(dur * fps))
        mov = str(c.get("drone_motion") or c.get("local_drone_motion") or "steady_eye_level").lower().strip()
        is_vid = bool(c.get("is_video", True)) if "is_video" in c else str(p).lower().endswith((".mp4", ".mov", ".mkv", ".webm"))
        tag = f"v_cut_{i}"

        if is_vid:
            # Native motion video: play for exact cut duration with smooth cinematic camera glide
            input_args.extend(["-t", f"{dur:.2f}", "-i", str(p)])
            cam_id = str(c.get("camera_id", "")).lower()
            cut_t = str(c.get("cut_type", "")).upper()
            is_singer_cut = any(k in cam_id for k in ("singer", "vocalist", "face")) or bool(c.get("is_singing"))
            is_face_dolly = any(k in mov for k in ("dolly", "close", "face", "zoom_in_singer")) or cut_t == "CLOSE_UP"

            if is_face_dolly:
                c_x = "(in_w-out_w)/2"
                c_y = f"(in_h-out_h)*(0.48-0.18*(t/{dur:.2f}))"
            elif any(k in mov for k in ("pan-right", "right", "orbit-right", "pan_to_guitarist")):
                c_x = f"(in_w-out_w)*(0.30+0.40*(t/{dur:.2f}))"
                c_y = "(in_h-out_h)*0.35"
            elif any(k in mov for k in ("pan-left", "left", "orbit-left", "pan_to_drummer")):
                c_x = f"(in_w-out_w)*(0.70-0.40*(t/{dur:.2f}))"
                c_y = "(in_h-out_h)*0.35"
            elif any(k in mov for k in ("orbit", "arc")):
                c_x = f"(in_w-out_w)*(0.50+0.25*sin(3.14159*t/{dur:.2f}))"
                c_y = "(in_h-out_h)*0.35"
            elif any(k in mov for k in ("crane-down", "down", "pedestal-down")):
                c_x = "(in_w-out_w)/2"
                c_y = f"(in_h-out_h)*(0.25+0.30*(t/{dur:.2f}))"
            elif any(k in mov for k in ("pedestal-up", "pedestal_up", "tilt-up", "up")):
                c_x = "(in_w-out_w)/2"
                c_y = f"(in_h-out_h)*(0.55-0.25*(t/{dur:.2f}))"
            elif is_singer_cut:
                c_x = "(in_w-out_w)/2"
                c_y = f"(in_h-out_h)*(0.42-0.12*(t/{dur:.2f}))"
            else:
                c_x, c_y = "(in_w-out_w)/2", "(in_h-out_h)/2"

            chains.append(f"[{i}:v]scale=4224:2376:force_original_aspect_ratio=increase,crop=3840:2160:{c_x}:{c_y},fps={fps},format=yuv420p,setsar=1[{tag}]")
        else:
            # High-res 4K keyframe: apply smooth 2.5D local drone motion across the cut (or static canvas for scene_00/steady)
            input_args.extend(["-loop", "1", "-t", f"{dur:.2f}", "-i", str(p)])
            if mov in ("static", "steady", "steady_eye_level") or Path(p).name.startswith("scene_00"):
                chains.append(f"[{i}:v]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,fps={fps},format=yuv420p,setsar=1[{tag}]")
            else:
                if any(k in mov for k in ("dolly", "close", "face", "zoom_in_singer")):
                    z_e, x_e, y_e = f"1.0+0.12*(on/{d_frames})", "'iw/2-(iw/zoom/2)'", "'(ih*0.35)-(ih/zoom*0.35)'"
                elif any(k in mov for k in ("crane-down", "down", "tilt-down")):
                    z_e, x_e, y_e = "1.08", "'iw/2-(iw/zoom/2)'", f"'(ih-ih/zoom)*(on/{d_frames})'"
                elif any(k in mov for k in ("orbit", "pan-right", "right")):
                    z_e, x_e, y_e = "1.06", f"'(iw-iw/zoom)*(on/{d_frames})'", "'ih/2-(ih/zoom/2)'"
                elif any(k in mov for k in ("pan-left", "left")):
                    z_e, x_e, y_e = "1.06", f"'(iw-iw/zoom)*(1.0-on/{d_frames})'", "'ih/2-(ih/zoom/2)'"
                else:
                    z_e, x_e, y_e = "1.04", "'iw/2-(iw/zoom/2)'", "'ih/2-(ih/zoom/2)'"

                chains.append(f"[{i}:v]zoompan=z='{z_e}':x={x_e}:y={y_e}:d={d_frames}:s=3840x2160:fps={fps},format=yuv420p,setsar=1[{tag}]")

    # Sequence cuts with clean live concert switching
    concat_inputs = "".join(f"[{f'v_cut_{k}'}]" for k in range(count))
    chains.append(f"{concat_inputs}concat=n={count}:v=1:a=0[base_v]")

    # Add subtitle filter if available
    v_out_tag = "[base_v]"
    final_v_tag = "[v_final]"
    if sub_path and sub_path.is_file():
        clean_sub = str(sub_path).replace("\\", "/").replace(":", "\\:")
        chains.append(f"{v_out_tag}subtitles='{clean_sub}'{final_v_tag}")
    else:
        chains.append(f"{v_out_tag}null{final_v_tag}")

    filter_complex = ";".join(chains)
    cmd = [
        ffmpeg_bin, "-y", *input_args, "-i", str(song_path), "-t", f"{total_duration:.2f}",
        "-filter_complex", filter_complex, "-map", final_v_tag, "-map", f"{count}:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-threads", "8", "-shortest", str(out_video_path),
    ]

    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        err = stderr.decode(errors="replace")
        logger.error(f"assemble_broadcast_cuts_failed: {err[-1000:]}")
        raise RuntimeError(f"Broadcast assembly error: {err[-1000:]}")

    return out_video_path


__all__ = [
    "resolve_camera_index",
    "slice_cut_audio",
    "synthesize_broadcast_timeline_clips",
    "assemble_broadcast_cuts",
]
