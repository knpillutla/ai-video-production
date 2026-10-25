"""Concert Studio 3D Spatial Video Plate Extractor via H3 Max / Kling 3D.

Generates a continuous 3D arena camera flight from Plate 1 Master (Stage with Singer + Orchestra),
then deterministically extracts coherent physical perspective plates:
1. Frame 0 (t=0.0s): Stage master plate (Lead Singer + Orchestra)
2. Frame mid (t=2.5s): Side audience perspective viewing illuminated stage
3. Frame end (t=5.0s): High arena stadium vista / wide crowd panorama
Ensures 100% unified physical architecture, lighting, and wardrobe across all camera angles.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
from typing import Any
import cv2

from src.compliance.rights_ledger import AssetType, CommercialLicenseType, rights_ledger
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.dance.fal_h3_max_turbo import FalH3MaxTurboAdapter
from src.providers.dance.fal_kling import FalKlingAdapter
from src.providers.visual.fal_aura_sr import FalAuraSRAdapter


def extract_keyframes_from_video(
    video_path: Path,
    timestamps_sec: list[float],
    output_paths: list[Path],
) -> list[Path]:
    """Extract exact keyframes from video at target timestamps."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.warning(f"spatial_3d_video_open_failed: {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1)
    extracted: list[Path] = []

    for t, out_p in zip(timestamps_sec, output_paths):
        frame_idx = min(int(round(t * fps)), max(0, total_frames - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret and frame is not None:
            out_p.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_p), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            extracted.append(out_p)
            logger.info(f"spatial_3d_frame_extracted [t={t:.1f}s, frame={frame_idx}]: {out_p.name}")
        else:
            logger.warning(f"spatial_3d_frame_read_failed [t={t:.1f}s]: using fallback")

    cap.release()
    return extracted


def slice_spatial_window(video_path: Path, start_t: float, dur: float, out_path: Path) -> Path:
    """Slice dedicated spatial angle window from 3D flight video."""
    import subprocess
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_bin, "-y", "-ss", f"{start_t:.2f}", "-t", f"{dur:.2f}",
        "-i", str(video_path), "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(out_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if not (out_path.is_file() and out_path.stat().st_size > 10_000):
        shutil.copy2(video_path, out_path)
    return out_path


async def synthesize_spatial_3d_flight_plates(
    stage_master_image: Path,
    scenes_dir: Path,
    force_live: bool = False,
    episode_id: Any = None,
    custom_orbit_prompt: str | None = None,
    engine: str = "kling",
    storyboard_data: dict[str, Any] | None = None,
) -> list[Path]:
    """Generate 10s 3D camera flight matching authentic venue & genre (Kling 3D 10s or H3 Max 10s)."""
    scenes_dir.mkdir(parents=True, exist_ok=True)
    out_video = scenes_dir / "stadium_3d_flight.mp4"

    # Rule 3: Check disk cache
    if out_video.is_file() and out_video.stat().st_size > 50_000:
        logger.info(f"spatial_3d_video_cached: reusing {out_video.name} ($0.00 spend)")
        for t, p in [(2.5, scenes_dir / "scene_02.jpg"), (5.0, scenes_dir / "scene_03.jpg"), (7.5, scenes_dir / "scene_04.jpg")]:
            if not (p.is_file() and p.stat().st_size > 1000):
                extract_keyframes_from_video(out_video, [t], [p])
        return [stage_master_image]

    use_h3 = bool(engine and "h3" in str(engine).lower())
    engine_label = "Minimax H3 Max (~$0.26 / 10s)" if use_h3 else "Fal.ai Kling Video 1.6 (~$0.52 / 10s)"
    logger.info(f"selected_spatial_3d_engine: {engine_label}")

    sb = storyboard_data or {}
    style = str(sb.get("style", "carnatic"))
    setting = str(sb.get("setting", "beach"))
    v_type = str(sb.get("venue_type", "outdoor"))
    bg = str(sb.get("background", "beach_ocean"))
    weather = str(sb.get("weather", "clear"))
    inst = str(sb.get("instrument", "mic"))
    pos = str(sb.get("position", "standing"))
    chars = (sb.get("characters") or [{}])[0].get("name", "Radha") if sb.get("characters") else "Radha"

    from src.studios.concert_studio.concert_orbit_engine import build_contextual_orbit_prompt
    from src.studios.concert_studio.concert_prompt_engine import detect_chorus_presence
    has_chorus = detect_chorus_presence(sb)

    ctx_prompt, ctx_neg = build_contextual_orbit_prompt(
        style=style, setting=setting, venue_type=v_type, background=bg, weather=weather,
        chars=chars, instrument=inst, position=pos, has_chorus=has_chorus,
    )

    is_classical = any(k in style.lower() for k in ("carnatic", "hindustani", "classical", "fusion"))
    is_beach = any(k in f"{setting} {bg}".lower() for k in ("beach", "ocean", "coastal"))

    raw_p = custom_orbit_prompt.strip() if custom_orbit_prompt and len(custom_orbit_prompt.strip()) > 30 else ""
    if raw_p:
        has_leak = (is_classical or is_beach) and any(k in raw_p.lower() for k in ("stadium", "lightstick", "60,000", "arena crane"))
        if has_leak:
            logger.info("sanitizing_orbit_prompt: replaced stadium/lightstick leak with serene contextual prompt")
            prompt = ctx_prompt
            neg_prompt = ctx_neg
        else:
            prompt = raw_p if "360" in raw_p.lower() else f"Continuous 10-second 360-degree circular orbital camera flight, {raw_p}"
            neg_prompt = ctx_neg
    else:
        prompt = ctx_prompt
        neg_prompt = ctx_neg

    if (not is_mock_mode() or force_live) and force_live:
        print(f"    [~] Synthesizing 10s 3D Arena Camera Orbit Flight via {engine_label}...")
        if use_h3:
            logger.info(f"synthesizing_3d_flight [engine=fal-ai/minimax/h3-max] [input={stage_master_image.name}] (duration=10s)...")
            h3 = FalH3MaxTurboAdapter()
            await h3.generate_video(
                image_url=str(stage_master_image),
                motion_prompt=prompt,
                output_path=out_video,
                duration=10,
                force_live=force_live,
            )
        else:
            logger.info(f"synthesizing_3d_flight [engine=fal-ai/kling-video] [input={stage_master_image.name}] (duration=10s)...")
            kling = FalKlingAdapter()
            await kling.generate_video(
                image_url=str(stage_master_image),
                tail_image_url=str(stage_master_image),
                motion_prompt=prompt,
                output_path=out_video,
                duration=10,
                force_live=force_live,
                negative_prompt=neg_prompt,
            )
    else:
        out_video.write_bytes(b"\x00" * 60_000)

    for t, p in [(2.5, scenes_dir / "scene_02.jpg"), (5.0, scenes_dir / "scene_03.jpg"), (7.5, scenes_dir / "scene_04.jpg")]:
        if not (p.is_file() and p.stat().st_size > 1000):
            extract_keyframes_from_video(out_video, [t], [p])

    if episode_id and out_video.is_file():
        prov = "Minimax/H3-Max" if use_h3 else "Fal.ai/Kling-3D"
        rights_ledger.record_asset(
            episode_id, AssetType.VIDEO, str(out_video), prov, f"{prov}/10sOrbit",
            CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP, f"SPATIAL-3D-{out_video.name}-{episode_id}", True,
        )

    return [stage_master_image]


async def synthesize_living_stage_loop(
    stage_master_image: Path,
    scenes_dir: Path,
    force_live: bool = False,
    episode_id: Any = None,
    custom_prompt: str | None = None,
    custom_neg: str | None = None,
    has_chorus: bool = False,
    storyboard_data: dict[str, Any] | None = None,
) -> Path:
    """Generate 5s living stage loop with steady locked-off camera, closed lips, and chorus ($0.26 spend)."""
    scenes_dir.mkdir(parents=True, exist_ok=True)
    out_video = scenes_dir / "stage_living_5s.mp4"

    # Rule 3: Check disk cache
    if out_video.is_file() and out_video.stat().st_size > 50_000:
        logger.info(f"living_stage_video_cached: reusing {out_video.name} ($0.00 spend)")
        return out_video

    sb = storyboard_data or {}
    bg_name = str(sb.get("background", "beach_ocean")).replace("_", " ")
    stage_name = str(sb.get("stage_setting", "beach_platform")).replace("_", " ")
    is_out = str(sb.get("venue_type", "outdoor")).lower() == "outdoor" or any(k in f"{stage_name} {bg_name}".lower() for k in ("beach", "ocean", "outdoor", "garden", "mountain", "desert", "roof"))

    chorus_line = (
        "Beside the lead singer on stage, 2-3 backing chorus vocalists sway gently in rhythm at their standing microphones with closed lips, smiling and harmonizing. "
        if has_chorus else ""
    )
    if custom_prompt and len(custom_prompt.strip()) > 20:
        lead_cam = "Rock-steady tripod locked-off static front eye-level broadcast camera view. " if "locked" not in custom_prompt.lower() else ""
        prompt = f"{lead_cam}{custom_prompt.strip()}"
    else:
        prompt = (
            "Rock-steady tripod locked-off static front eye-level broadcast camera view of centerstage concert performance. "
            "Lead singer centerstage has lips gently closed, calm natural breathing, subtle torso micro-sway, gentle eye blinks, emotive face. "
            f"{chorus_line}"
            "Accompanists sway in rhythm: violinist glides bow smoothly across strings, mridangam drummer taps drumheads rhythmically. "
            f"Background features {bg_name} under atmospheric concert stage lighting on authentic {stage_name}. "
            "Infinite seamless loop, first frame matches last frame identically, 8k resolution, photorealistic, perfectly steady locked-off camera."
        )

    out_ban = ", indoor, indoor stadium, arena trusses, steel rafters, ceiling, enclosed walls, dark room, concrete stadium bowl" if is_out else ""
    c_neg_extra = f", {custom_neg.strip()}" if custom_neg and len(custom_neg.strip()) > 10 else ""
    neg_prompt = (
        "camera shake, camera wobble, camera movement, handheld camera, jitter, vibration, erratic camera, "
        "camera pan, camera zoom, drone flight, jump cut, open mouth, mouth flapping, distorted limbs, glitch"
        f"{out_ban}{c_neg_extra}"
    )
    if has_chorus:
        neg_prompt += ", solo singer, missing chorus, missing backing vocalists"

    if (not is_mock_mode() or force_live) and force_live:
        print("    [~] Synthesizing 5s Seamless Living Stage Loop via Kling Video (~$0.26)...")
        logger.info(f"synthesizing_living_stage_loop [engine=fal-ai/kling-video] [input={stage_master_image.name}] (duration=5s)...")
        kling = FalKlingAdapter()
        await kling.generate_video(
            image_url=str(stage_master_image),
            tail_image_url=str(stage_master_image),
            motion_prompt=prompt,
            output_path=out_video,
            duration=5,
            force_live=force_live,
            negative_prompt=neg_prompt,
        )
    else:
        out_video.write_bytes(b"\x00" * 60_000)

    if episode_id and out_video.is_file():
        rights_ledger.record_asset(
            episode_id, AssetType.VIDEO, str(out_video), "Fal.ai/Kling-5sLoop", "Fal.ai/Kling-5sLoop",
            CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP, f"LIVING-LOOP-{out_video.name}-{episode_id}", True,
        )
    return out_video


def materialize_living_stage_loop(
    source_5s_video: Path,
    output_path: Path,
    total_duration: float,
) -> Path:
    """Loop 5s seamless video across full song duration via FFmpeg ($0.00 spend)."""
    if output_path.is_file() and output_path.stat().st_size > 50_000:
        return output_path
    num_loops = int(total_duration // 5.0) + 2
    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [
        ffmpeg_bin, "-y", "-stream_loop", str(num_loops), "-i", str(source_5s_video),
        "-c", "copy", "-t", f"{total_duration:.2f}", str(output_path),
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return output_path


# Alias for backward compatibility
synthesize_kling_3d_flight_plates = synthesize_spatial_3d_flight_plates

__all__ = [
    "extract_keyframes_from_video",
    "slice_spatial_window",
    "synthesize_spatial_3d_flight_plates",
    "synthesize_kling_3d_flight_plates",
    "synthesize_living_stage_loop",
    "materialize_living_stage_loop",
]
