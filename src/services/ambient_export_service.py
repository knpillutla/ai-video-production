"""Ambient World Packaging and Export Utilities (long-play stretching, shorts, localized metadata)."""

from __future__ import annotations
import json, subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING
import imageio_ffmpeg

from src.core.telemetry import logger
from src.services.ambient_metadata_packager import YouTubeAmbientPackage, generate_youtube_ambient_package
from src.services.ambient_shorts_extractor import generate_ambient_short
from src.services.ambient_translator import LocalizedMetadata, localize_metadata_for_languages
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.thumbnail_ab_packager import ThumbnailABPackage, generate_thumbnail_ab_variants
from src.services.topic_memory import topic_memory

if TYPE_CHECKING:
    from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


def _probe_clip_duration(clip_path: Path) -> float:
    """Probe the exact duration of a media file in seconds."""
    try:
        import re
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_bin, "-i", str(clip_path)], capture_output=True, text=True, errors="ignore")
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            return float(m.group(1)) * 3600.0 + float(m.group(2)) * 60.0 + float(m.group(3))
    except Exception:
        pass
    return 5.0


def get_media_duration(media_path: Path) -> float:
    return _probe_clip_duration(media_path)


def _is_clip_4k(clip_path: Path) -> bool:
    try:
        res = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(clip_path)], capture_output=True, text=True, errors="ignore")
        return "3840x2160" in res.stderr or "2160x3840" in res.stderr
    except Exception:
        return False


def build_seamless_forward_cineloop(clip_path: Path, xfade_dur: float = 1.2, crf: int = 22) -> Path:
    """Transform short 5s/10s AI diffusion motion clip into an infinitely loopable forward-flowing cineloop (zero reverse flow, zero flicker)."""
    if clip_path.name.endswith("_fwd_seamless.mp4") and clip_path.is_file():
        return clip_path

    base_stem = clip_path.stem.replace("_fwd_seamless", "")
    out_seamless = clip_path.parent / f"{base_stem}_fwd_seamless.mp4"

    duration = _probe_clip_duration(clip_path)
    if duration <= xfade_dur + 0.5:
        return clip_path

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    has_audio = False
    try:
        check = subprocess.run([ffmpeg_bin, "-i", str(clip_path)], capture_output=True, text=True, errors="ignore")
        has_audio = "Audio:" in check.stderr
    except Exception:
        pass

    if out_seamless.is_file() and out_seamless.stat().st_size > 1000:
        if has_audio:
            check_out = subprocess.run([ffmpeg_bin, "-i", str(out_seamless)], capture_output=True, text=True, errors="ignore")
            if "Audio:" in check_out.stderr:
                return out_seamless
        else:
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
            ffmpeg_bin, "-y", "-i", str(clip_path),
            "-filter_complex", filter_graph,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            str(out_seamless),
        ]
    else:
        filter_graph = (
            f"[0:v]split=2[h][t];"
            f"[t]trim=start={split_offset:.2f}:end={duration:.2f},setpts=PTS-STARTPTS,fps=24[t1];"
            f"[h]trim=start=0:end={split_offset:.2f},setpts=PTS-STARTPTS,fps=24[h1];"
            f"[t1][h1]xfade=transition=fade:duration={xfade_dur:.2f}:offset=0,fps=24,format=yuv420p[v]"
        )
        cmd = [
            ffmpeg_bin, "-y", "-i", str(clip_path),
            "-filter_complex", filter_graph,
            "-map", "[v]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", str(crf),
            str(out_seamless),
        ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return out_seamless
    except Exception as err:
        logger.warning(f"forward_cineloop_fallback: {err}")
        return clip_path


def assemble_4k_master(video_clips: list[Path], audio_path: Optional[Path], out_master: Path, scene_hold_sec: float = 60.0, crf: int = 22) -> Path:
    """Assemble relaxing 4K master with seamless forward cineloops, Extended Perspective Hold, and crossfades in CRF 22 format."""
    from src.services.procedural_foley import synthesize_foley_stem
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    seamless_clips = [build_seamless_forward_cineloop(c, crf=crf) for c in video_clips]
    n, x_dur = len(seamless_clips), 2.0
    total_vid_dur = scene_hold_sec if n == 1 else (n * scene_hold_sec) - ((n - 1) * x_dur)

    target_audio = audio_path
    if not target_audio or not target_audio.is_file():
        has_clip_audio = all("Audio:" in subprocess.run([ffmpeg_bin, "-i", str(c)], capture_output=True, text=True, errors="ignore").stderr for c in seamless_clips)
        if not has_clip_audio:
            foley_wav = out_master.parent / "procedural_nature_foley.wav"
            if not foley_wav.is_file() or foley_wav.stat().st_size < 1000:
                synthesize_foley_stem(weather_type="water stream alpine breeze", setting_type="nature", space="outdoor", duration_seconds=total_vid_dur + 5.0, output_path=foley_wav)
            target_audio = foley_wav

    if n == 1:
        c_dur = get_media_duration(seamless_clips[0]) or 5.0
        v_loops = max(1, int(scene_hold_sec / max(1.0, c_dur)) + 2)
        if target_audio and target_audio.is_file():
            a_dur = get_media_duration(target_audio) or 5.0
            a_loops = max(1, int(scene_hold_sec / max(1.0, a_dur)) + 2)
            cmd = [
                ffmpeg_bin, "-y",
                "-stream_loop", str(v_loops), "-i", str(seamless_clips[0]),
                "-stream_loop", str(a_loops), "-i", str(target_audio),
                "-map", "0:v:0", "-map", "1:a:0", "-t", str(scene_hold_sec),
                "-c:v", "copy" if _is_clip_4k(seamless_clips[0]) else "libx264",
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-movflags", "+faststart", str(out_master)
            ]
        else:
            cmd = [
                ffmpeg_bin, "-y",
                "-stream_loop", str(v_loops), "-i", str(seamless_clips[0]),
                "-map", "0:v:0", "-map", "0:a:0", "-t", str(scene_hold_sec),
                "-c:v", "copy" if _is_clip_4k(seamless_clips[0]) else "libx264",
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-movflags", "+faststart", str(out_master)
            ]
    else:
        inputs = []
        for c in seamless_clips:
            v_loops = max(1, int(scene_hold_sec / max(1.0, get_media_duration(c) or 5.0)) + 2)
            inputs.extend(["-stream_loop", str(v_loops), "-i", str(c)])

        filter_parts = [f"[{i}:v]scale=3840:2160,setsar=1[s{i}]" for i in range(n)]
        prev_tag, curr_offset = "s0", scene_hold_sec - x_dur
        for i in range(1, n):
            out_tag = f"v{i}" if i < n - 1 else "v"
            filter_parts.append(f"[{prev_tag}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={curr_offset:.2f}[{out_tag}]")
            prev_tag, curr_offset = out_tag, curr_offset + scene_hold_sec - x_dur

        if target_audio and target_audio.is_file():
            a_loops = max(1, int(total_vid_dur / max(1.0, get_media_duration(target_audio) or 5.0)) + 2)
            inputs.extend(["-stream_loop", str(a_loops), "-i", str(target_audio)])
            cmd = [ffmpeg_bin, "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[v]", "-map", f"{n}:a", "-t", f"{total_vid_dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)]
        else:
            filter_a = [f"[{'0:a' if i == 1 else f'a{i-1}'}][{i}:a]acrossfade=d={x_dur:.2f}[{'a' if i == n - 1 else f'a{i}'}]" for i in range(1, n)]
            cmd = [ffmpeg_bin, "-y", *inputs, "-filter_complex", ";".join(filter_parts + filter_a), "-map", "[v]", "-map", "[a]", "-t", f"{total_vid_dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as err:
        err_msg = (err.stderr or err.stdout or str(err)).strip()
        logger.error(f"failed_to_assemble_4k_master: {err_msg}")
        raise RuntimeError(f"FFmpeg assembly failed: {err_msg}") from err
    return out_master


def assemble_dual_masters(video_clips: list[Path], audio_path: Optional[Path], ep_dir: Path, crf: int = 22) -> Dict[str, Path]:
    """Assemble 4K masters in CRF 22 format. Automatically rebuilds if forward cineloops are updated."""
    seamless_clips = [build_seamless_forward_cineloop(c, crf=crf) for c in video_clips]
    master_music = ep_dir / "master_4k_ambient.mp4"
    needs_music_rebuild = (
        not master_music.is_file()
        or master_music.stat().st_size < 1000
        or any(sc.stat().st_mtime > master_music.stat().st_mtime for sc in seamless_clips)
    )
    if needs_music_rebuild:
        assemble_4k_master(seamless_clips, audio_path, master_music, crf=crf)
    else:
        logger.info(f"decision_master_video_cache_hit: Reusing {master_music.name} ($0.00 spend)")

    if not audio_path:
        return {"music_master": master_music, "nature_master": None}

    master_nature = ep_dir / "master_4k_ambient_nature_only.mp4"
    needs_nature_rebuild = not master_nature.is_file() or master_nature.stat().st_size < 1000 or any(sc.stat().st_mtime > master_nature.stat().st_mtime for sc in seamless_clips)
    if needs_nature_rebuild:
        assemble_4k_master(seamless_clips, None, master_nature, crf=crf)
    else:
        logger.info(f"decision_nature_master_cache_hit: Reusing {master_nature.name} ($0.00 spend)")

    return {"music_master": master_music, "nature_master": master_nature}


def handle_long_play_export(master: Path, ep_dir: Path, hours: Optional[float], fade_hours: Optional[float]) -> Optional[Path]:
    """Export long-play multi-hour stream loop for all existing master versions (with BGM and pure nature), plus 30-min broadcast by default."""
    eff_hours = hours if (hours and hours > 0) else 3.0
    suffix = f"_{int(fade_hours)}h_black" if fade_hours else ""
    label = int(eff_hours) if eff_hours.is_integer() else eff_hours
    lp_path = ep_dir / f"master_4k_{label}hour{suffix}_broadcast.mp4"
    legacy_lp = ep_dir / f"master_4k_{label}hour{suffix}_sleep.mp4"
    if legacy_lp.is_file() and legacy_lp.stat().st_size > 1000 and (not lp_path.is_file() or lp_path.stat().st_size < 1000):
        try:
            legacy_lp.rename(lp_path)
        except Exception:
            pass

    if master.is_file() and (not lp_path.is_file() or lp_path.stat().st_size < 1000):
        export_long_play_broadcast(source_4k_video=master, output_long_play=lp_path, target_duration_seconds=eff_hours * 3600.0, fade_to_black_hours=fade_hours)
    
    # Also generate default 30-Minute (0.5 hour) Broadcast Edition
    lp_30m = ep_dir / "master_4k_30min_broadcast.mp4"
    if master.is_file() and (not lp_30m.is_file() or lp_30m.stat().st_size < 1000):
        export_long_play_broadcast(source_4k_video=master, output_long_play=lp_30m, target_duration_seconds=1800.0)

    nature_master = ep_dir / "master_4k_ambient_nature_only.mp4"
    if nature_master.is_file() and nature_master.resolve() != master.resolve():
        lp_nature_path = ep_dir / f"master_4k_{label}hour_nature_only{suffix}_broadcast.mp4"
        legacy_nature_lp = ep_dir / f"master_4k_{label}hour_nature_only{suffix}_sleep.mp4"
        if legacy_nature_lp.is_file() and legacy_nature_lp.stat().st_size > 1000 and (not lp_nature_path.is_file() or lp_nature_path.stat().st_size < 1000):
            try:
                legacy_nature_lp.rename(lp_nature_path)
            except Exception:
                pass
        if not lp_nature_path.is_file() or lp_nature_path.stat().st_size < 1000:
            logger.info(f"stretching_dual_nature_master: {lp_nature_path.name}")
            export_long_play_broadcast(source_4k_video=nature_master, output_long_play=lp_nature_path, target_duration_seconds=eff_hours * 3600.0, fade_to_black_hours=fade_hours)
        
        lp_30m_nature = ep_dir / "master_4k_30min_nature_only_broadcast.mp4"
        if not lp_30m_nature.is_file() or lp_30m_nature.stat().st_size < 1000:
            export_long_play_broadcast(source_4k_video=nature_master, output_long_play=lp_30m_nature, target_duration_seconds=1800.0)
    return lp_path


def handle_short_export(master: Path, ep_dir: Path, gen: bool = True) -> Optional[Path]:
    """Generate 9:16 vertical teaser short from 4K master."""
    s_path = ep_dir / "short_9x16_teaser.mp4"
    if master.is_file() and master.stat().st_size > 1000:
        if not s_path.is_file() or s_path.stat().st_size < 1000:
            generate_ambient_short(source_4k_video=master, output_short_path=s_path)
    return s_path if s_path.is_file() else None


def export_metadata_packages(
    sb: AmbientStoryboard, ep_dir: Path, hours: Optional[float], fade_h: Optional[float]
) -> Tuple[YouTubeAmbientPackage, ThumbnailABPackage, Dict[str, LocalizedMetadata]]:
    """Generate YouTube packaging for 3-Hour, 30-Minute, Nature-Only, and Short variants, plus A/B thumbnails and multi-language SEO."""
    eff_h = hours or 3.0
    pkg_music = generate_youtube_ambient_package(sb.primary_archetype, eff_h, sb.secondary_archetype, fade_h)
    (ep_dir / "youtube_packaging.json").write_text(json.dumps(pkg_music.model_dump(), indent=2), encoding="utf-8")
    
    pkg_nature = generate_youtube_ambient_package(sb.primary_archetype, eff_h, sb.secondary_archetype, fade_h)
    pkg_nature.title = f"{pkg_nature.title} | Pure Nature Sounds (NO MUSIC) [4K ASMR]"
    pkg_nature.description = f"100% pure natural ambient soundscape without background music.\n\n{pkg_nature.description}"
    (ep_dir / "youtube_packaging_nature_only.json").write_text(json.dumps(pkg_nature.model_dump(), indent=2), encoding="utf-8")

    # 30-Minute Broadcast Editions
    pkg_30m_m = generate_youtube_ambient_package(sb.primary_archetype, 0.5, sb.secondary_archetype)
    (ep_dir / "youtube_packaging_30min.json").write_text(json.dumps(pkg_30m_m.model_dump(), indent=2), encoding="utf-8")

    pkg_30m_n = generate_youtube_ambient_package(sb.primary_archetype, 0.5, sb.secondary_archetype)
    pkg_30m_n.title = f"{pkg_30m_n.title} | Pure Nature Sounds (NO MUSIC) [4K ASMR]"
    pkg_30m_n.description = f"100% pure natural ambient soundscape without background music.\n\n{pkg_30m_n.description}"
    (ep_dir / "youtube_packaging_30min_nature_only.json").write_text(json.dumps(pkg_30m_n.model_dump(), indent=2), encoding="utf-8")

    pkg_short = {
        "title": f"Experience {sb.title.split('~')[0].strip()} in 4K 🌊✨ #shorts",
        "description": f"Stand directly in front of {sb.title.split('~')[0].strip()} in crisp 4K.\n\n🎧 Watch the full 30-Minute & 3-Hour Velvet Broadcasts on our channel!\n\n#shorts #nature #asmr #satisfying #4k",
        "tags": [sb.primary_archetype, "shorts", "nature_asmr", "satisfying", "4k_nature"],
        "pinned_comment": "🌊 Would you visit here? Watch the full 30-Minute & 3-Hour editions with 432Hz sleep audio on our channel! 🌙💤",
    }
    (ep_dir / "youtube_packaging_short.json").write_text(json.dumps(pkg_short, indent=2), encoding="utf-8")
    ab = generate_thumbnail_ab_variants(sb.primary_archetype)
    (ep_dir / "thumbnail_ab_variants.json").write_text(json.dumps(ab.model_dump(), indent=2), encoding="utf-8")
    loc = localize_metadata_for_languages(sb.primary_archetype, pkg_music.title, pkg_music.description)
    (ep_dir / "localized_metadata.json").write_text(json.dumps({k: v.model_dump() for k, v in loc.items()}, indent=2), encoding="utf-8")
    return pkg_music, ab, loc
