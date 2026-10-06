"""Broadcast Packaging and Export Utilities (long-play stretching, shorts, localized metadata)."""

from __future__ import annotations
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Dict, Optional, TYPE_CHECKING
import imageio_ffmpeg

from src.core.telemetry import logger
from src.services.ambient_export_service import build_adaptive_resolution_filter
from src.services.ambient_metadata_packager import generate_youtube_ambient_package
from src.services.ambient_shorts_extractor import generate_ambient_short
from src.services.ambient_translator import localize_metadata_for_languages
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.thumbnail_ab_packager import generate_thumbnail_ab_variants
from src.services.topic_memory import topic_memory

if TYPE_CHECKING:
    from src.studios.screenplay_models import AmbientStoryboard


def get_media_duration(media_path: Path) -> float:
    """Probe the exact duration of a media file in seconds."""
    try:
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_bin, "-i", str(media_path)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="ignore")
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            return float(m.group(1)) * 3600.0 + float(m.group(2)) * 60.0 + float(m.group(3))
    except Exception:
        pass
    return 60.0


def _is_clip_4k(clip_path: Path) -> bool:
    try:
        res = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(clip_path)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="ignore")
        return "3840x2160" in res.stderr or "2160x3840" in res.stderr
    except Exception:
        return False


def build_seamless_forward_cineloop(clip_path: Path, xfade_dur: float = 1.2, crf: int = 22) -> Path:
    """Transform short 5s/10s AI diffusion motion clip into an infinitely loopable cineloop."""
    if clip_path.name.endswith("_fwd_seamless.mp4") and clip_path.is_file():
        return clip_path

    base_stem = clip_path.stem.replace("_fwd_seamless", "")
    out_seamless = clip_path.parent / f"{base_stem}_fwd_seamless.mp4"
    duration = get_media_duration(clip_path)
    if duration <= xfade_dur + 0.5:
        return clip_path

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    has_audio = False
    try:
        check = subprocess.run([ffmpeg_bin, "-i", str(clip_path)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="ignore")
        has_audio = "Audio:" in check.stderr
    except Exception:
        pass

    if out_seamless.is_file() and out_seamless.stat().st_size > 1000:
        return out_seamless

    split_offset = max(0.1, duration - xfade_dur)
    if has_audio:
        filter_graph = (
            f"[0:v]split=2[h][t];"
            f"[t]trim=start={split_offset:.2f}:end={duration:.2f},setpts=PTS-STARTPTS,fps=24[t1];"
            f"[h]trim=start=0:end={split_offset:.2f},setpts=PTS-STARTPTS,fps=24[h1];"
            f"[t1][h1]xfade=transition=fade:duration={xfade_dur:.2f}:offset=0,fps=24,format=yuv420p[v];"
            f"[0:a]atrim=0:{split_offset:.2f},asetpts=PTS-STARTPTS[a]"
        )
        cmd = [
            ffmpeg_bin, "-y", "-nostats", "-loglevel", "error", "-i", str(clip_path),
            "-filter_complex", filter_graph,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000", str(out_seamless),
        ]
    else:
        filter_graph = (
            f"[0:v]split=2[h][t];"
            f"[t]trim=start={split_offset:.2f}:end={duration:.2f},setpts=PTS-STARTPTS,fps=24[t1];"
            f"[h]trim=start=0:end={split_offset:.2f},setpts=PTS-STARTPTS,fps=24[h1];"
            f"[t1][h1]xfade=transition=fade:duration={xfade_dur:.2f}:offset=0,fps=24,format=yuv420p[v]"
        )
        cmd = [
            ffmpeg_bin, "-y", "-nostats", "-loglevel", "error", "-i", str(clip_path),
            "-filter_complex", filter_graph,
            "-map", "[v]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
            str(out_seamless),
        ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as err:
        err_msg = (err.stderr or str(err)).strip()
        logger.warning(f"failed_to_build_seamless_loop: {err_msg}")
        return clip_path

    return out_seamless


def assemble_4k_master(
    seamless_clips: list[Path],
    audio_path: Optional[Path],
    out_master: Path,
    scene_hold_sec: float = 60.0,
    x_dur: float = 2.0,
    crf: int = 22,
) -> Path:
    """Concatenate 4K cineloops into a master broadcast matching the full duration of the music track."""
    out_master.parent.mkdir(parents=True, exist_ok=True)
    n = len(seamless_clips)
    if n == 0:
        raise ValueError("Cannot assemble 4K master: zero valid seamless clips provided.")

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    v_filter = build_adaptive_resolution_filter(seamless_clips[0], 3840, 2160)

    if n == 1:
        c_dur = get_media_duration(seamless_clips[0]) or 5.0
        if audio_path and audio_path.is_file():
            a_dur = get_media_duration(audio_path) or 60.0
            target_dur = max(scene_hold_sec, a_dur) if a_dur > 15.0 else scene_hold_sec
            v_loops = max(1, int(target_dur / max(1.0, c_dur)) + 2)
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-stream_loop", str(v_loops), "-i", str(seamless_clips[0]),
                "-i", str(audio_path),
                "-map", "0:v:0", "-map", "1:a:0", "-t", str(target_dur),
                "-vf", v_filter,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-movflags", "+faststart", str(out_master)
            ]
        else:
            target_dur = scene_hold_sec
            v_loops = max(1, int(target_dur / max(1.0, c_dur)) + 2)
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-stream_loop", str(v_loops), "-i", str(seamless_clips[0]),
                "-map", "0:v:0", "-t", str(target_dur),
                "-vf", v_filter,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
                "-movflags", "+faststart", str(out_master)
            ]
    else:
        inputs = []
        for c in seamless_clips:
            v_loops = max(1, int(scene_hold_sec / max(1.0, get_media_duration(c) or 5.0)) + 2)
            inputs.extend(["-stream_loop", str(v_loops), "-i", str(c)])

        filter_parts = [f"[{i}:v]{build_adaptive_resolution_filter(c, 3840, 2160)}[s{i}]" for i, c in enumerate(seamless_clips)]
        prev_tag, curr_offset = "s0", scene_hold_sec - x_dur
        for i in range(1, n):
            out_tag = f"v{i}" if i < n - 1 else "v"
            filter_parts.append(f"[{prev_tag}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={curr_offset:.2f}[{out_tag}]")
            prev_tag, curr_offset = out_tag, curr_offset + scene_hold_sec - x_dur

        total_vid_dur = (scene_hold_sec * n) - (x_dur * (n - 1))
        if audio_path and audio_path.is_file():
            a_dur = get_media_duration(audio_path) or 60.0
            target_dur = max(total_vid_dur, a_dur) if a_dur > 15.0 else total_vid_dur
            inputs.extend(["-i", str(audio_path)])
            cmd = [ffmpeg_bin, "-y", "-nostats", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[v]", "-map", f"{n}:a", "-t", f"{target_dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)]
        else:
            cmd = [ffmpeg_bin, "-y", "-nostats", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[v]", "-t", f"{total_vid_dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-movflags", "+faststart", str(out_master)]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as err:
        err_msg = (err.stderr or str(err)).strip()
        logger.error(f"failed_to_assemble_4k_master: {err_msg}")
        raise RuntimeError(f"FFmpeg assembly failed: {err_msg}") from err
    return out_master


def assemble_dual_masters(
    video_clips: list[Path],
    audio_path: Optional[Path] = None,
    ep_dir: Optional[Path] = None,
    audio_track: Optional[Path] = None,
    target_fps: int = 24,
    force_rerun: bool = False,
    crf: int = 22,
    **kwargs,
) -> Dict[str, Path]:
    """Assemble 4K masters matching complete music track length."""
    eff_audio = audio_path or audio_track
    if not ep_dir and video_clips:
        ep_dir = video_clips[0].parent

    seamless_clips = [build_seamless_forward_cineloop(c, crf=crf) for c in video_clips]
    master_music = ep_dir / "master_4k_ambient.mp4"
    needs_rebuild = (
        force_rerun
        or not master_music.is_file()
        or master_music.stat().st_size < 1000
        or any(sc.stat().st_mtime > master_music.stat().st_mtime for sc in seamless_clips)
    )
    if needs_rebuild:
        assemble_4k_master(seamless_clips, eff_audio, master_music, crf=crf)
    else:
        logger.info(f"decision_master_video_cache_hit: Reusing {master_music.name} ($0.00 spend)")

    # Nature master disabled for the time being to cut assembly time in half (50% CPU reduction)
    return {
        "music_master": master_music,
        "master_4k": master_music,
        "nature_master": master_music,
        "master_nature": master_music,
        "master_1080p": master_music,
    }


def handle_long_play_export(master: Path, ep_dir: Path, hours: Optional[float], fade_hours: Optional[float]) -> Optional[Path]:
    """Export long-play multi-hour stream loop for primary 4K broadcast master."""
    eff_hours = hours if (hours and hours > 0) else 3.0
    suffix = f"_{int(fade_hours)}h_black" if fade_hours else ""
    label = int(eff_hours) if eff_hours.is_integer() else eff_hours
    lp_path = ep_dir / f"master_4k_{label}hour{suffix}_broadcast.mp4"

    if master.is_file() and (not lp_path.is_file() or lp_path.stat().st_size < 1000):
        export_long_play_broadcast(source_4k_video=master, output_long_play=lp_path, target_duration_seconds=eff_hours * 3600.0, fade_to_black_hours=fade_hours)

    return lp_path if lp_path.is_file() else None


def export_metadata_packages(sb: AmbientStoryboard, ep_dir: Path) -> Dict[str, Any]:
    """Generate YouTube SEO, Multi-Language, and A/B Thumbnail metadata."""
    yt_pkg = generate_youtube_ambient_package(sb)
    yt_pkg_nature = generate_youtube_ambient_package(sb, nature_only=True)
    loc_pkg = localize_metadata_for_languages(sb)
    ab_pkg = generate_thumbnail_ab_variants(sb)

    (ep_dir / "youtube_packaging.json").write_text(json.dumps(yt_pkg.model_dump(), indent=2), encoding="utf-8")
    (ep_dir / "youtube_packaging_nature_only.json").write_text(json.dumps(yt_pkg_nature.model_dump(), indent=2), encoding="utf-8")
    (ep_dir / "localized_metadata.json").write_text(json.dumps(loc_pkg.model_dump(), indent=2), encoding="utf-8")
    (ep_dir / "thumbnail_ab_testing.json").write_text(json.dumps(ab_pkg.model_dump(), indent=2), encoding="utf-8")

    return {
        "youtube": yt_pkg.model_dump(),
        "youtube_nature_only": yt_pkg_nature.model_dump(),
        "localized": loc_pkg.model_dump(),
        "thumbnail_ab": ab_pkg.model_dump(),
    }


async def handle_short_export(
    sb: AmbientStoryboard, ep_dir: Path, video_clips: list[Path], audio_track: Path,
    t_start: float, hours: Optional[float], fade_h: Optional[float], force_rerun: bool
) -> Dict[str, Any]:
    """Export 9:16 vertical short and return completed artifact package."""
    short_path = ep_dir / "short_9x16_teaser.mp4"
    if force_rerun or not short_path.is_file() or short_path.stat().st_size < 1000:
        short_path = generate_ambient_short(video_clips, audio_track, short_path)

    dual_res = assemble_dual_masters(video_clips=video_clips, audio_path=audio_track, ep_dir=ep_dir, force_rerun=force_rerun)
    meta = export_metadata_packages(sb, ep_dir)

    await topic_memory.record_production(
        topic=sb.title, genre=f"nature_{sb.cluster}",
        tags=meta.get("youtube", {}).get("seo_tags", []), episode_id=ep_dir.name
    )

    return {
        "status": "success",
        "production_type": "short_and_dual_master",
        "episode_id": ep_dir.name,
        "short_video_path": str(short_path),
        "master_4k_path": str(dual_res["master_4k"]),
        "render_time_seconds": round(time.time() - t_start, 2),
        "video_clips": [str(c) for c in video_clips],
        "metadata": meta,
    }
